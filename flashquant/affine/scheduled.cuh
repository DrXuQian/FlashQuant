#pragma once
#include "launch.cuh"
#include "actlize_extensions/cutlass/gemm/kernel/ppu_aiu_gemm_mixed_input_streamk.hpp"
#include "actlize_extensions/cutlass/gemm/kernel/ppu_aiu_gemm_mixed_input_marlin.hpp"
#include <hggc_ad.h>

namespace quactlize::affine {

template<int TM, int TN, int TK, int WM, int WN, int Stages, int Algorithm, int Ctas>
struct ScheduledKernel {
    using Base = Kernel<TM, TN, TK, WM, WN, Stages>;
    using Types = typename Base::Types;
    using Mainloop = typename Types::CollectiveMainloop;
    using Epilogue = typename Types::CollectiveEpilogue;
    using Driver = std::conditional_t<Algorithm == 1,
        cutlass::gemm::kernel::StreamKMixedInputKernel<cute::Shape<int,int,int,int>, Mainloop, Epilogue>,
        cutlass::gemm::kernel::MarlinMixedInputKernel<cute::Shape<int,int,int,int>, Mainloop, Epilogue>>;
    using Gemm = cutlass::gemm::device::GemmUniversalAdapter<Driver>;
    using Arguments = typename Gemm::Arguments;
    static_assert(Algorithm == 1 || Algorithm == 2);

    static Arguments arguments(qwa_problem_v1 const& p, qwa_buffers_v1 const& b) {
        require(p.split == 1, "persistent scheduler owns K partitioning");
        require(p.k % TK == 0 && p.k / TK >= 8, "persistent scheduler requires at least eight K tiles");
        require(Driver::SharedStorageSize <= 262144, "persistent candidate exceeds shared memory");
        int device = 0, tensor_cus = 0;
        require(hggcGetDevice(&device) == hggcSuccess, "cannot query active device");
        require(hgDeviceGetAttributeAD(&tensor_cus, HGAD_DEVICE_ATTRIBUTE_TENSOR_MULTIPROCESSOR_COUNT,
                                      device) == HGGC_SUCCESS && tensor_cus > 0,
                "cannot query tensor CU count");
        require(Ctas <= Gemm::maximum_active_blocks(), "scheduler grid exceeds kernel residency");
        auto base = Base::arguments(p, b);
        Arguments args{base.mode, base.problem_shape, base.mainloop, base.epilogue,
                       cutlass::KernelHardwareInfo{device, tensor_cus}, {}};
        if constexpr (Algorithm == 1) {
            using SchedulerParams = typename Driver::TileSchedulerParams;
            args.scheduler.splits = 1;
            args.scheduler.max_swizzle_size = 1;
            args.scheduler.reduction_mode = SchedulerParams::ReductionMode::Deterministic;
            args.scheduler.decomposition_mode = SchedulerParams::DecompositionMode::StreamK;
            args.ctas_per_cu = Ctas;
        } else {
            args.scheduler.blocks_per_cu = Ctas;
        }
        return args;
    }

    static qwa_info_v1 query(qwa_problem_v1 const& p) {
        auto args = arguments(p, {});
        return {1, sizeof(qwa_info_v1), Gemm::get_workspace_size(args), Driver::SharedStorageSize,
                int(Driver::MaxThreadsPerBlock), 0};
    }

    struct Prepared : Plan {
        Arguments args;
        void* workspace;
        Gemm gemm;
        Prepared(qwa_problem_v1 const& p, qwa_buffers_v1 const& b)
            : args(arguments(p,b)), workspace(b.workspace) {
            require(Gemm::can_implement(args) == cutlass::Status::kSuccess,
                    "persistent scheduler cannot implement this shape");
            require(gemm.initialize(args, workspace, static_cast<hggcStream_t>(b.stream)) ==
                        cutlass::Status::kSuccess, "persistent scheduler initialization failed");
        }
        int run(void* stream) override {
            auto native_stream = static_cast<hggcStream_t>(stream);
            if constexpr (Algorithm == 1) {
                // Stream-K's final peer consumes the lock without resetting it.
                // Keep its mandatory reset inside the measured operation/graph.
                if (Driver::initialize_workspace(args, workspace, native_stream) != cutlass::Status::kSuccess)
                    return 41;
            }
            return gemm.run(native_stream) == cutlass::Status::kSuccess ? 0 : 41;
        }
    };

    static Plan* prepare(qwa_problem_v1 const& p, qwa_buffers_v1 const& b) {
        return new Prepared(p,b);
    }
};

}
