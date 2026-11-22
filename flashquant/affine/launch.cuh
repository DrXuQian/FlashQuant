#pragma once
#include "internal.hpp"
#include "fpA_intB_ppu.cuh"
#include "dense_splitk_multiformat_ppu.cuh"

namespace quactlize::affine {

template<int TM, int TN, int TK, int WM, int WN, int Stages>
struct Kernel {
    using Tile = cute::Shape<cute::Int<TM>, cute::Int<TN>, cute::Int<TK>>;
    using Warp = cute::Shape<cute::Int<WM>, cute::Int<WN>, cute::Int<TK>>;
    using Types = fpa_intb_ppu::DenseQ4KPack4KernelTypes<
        fpa_intb_ppu::QuantMode::FinegrainedScaleOnly,
        ppu_group_schedule::FinegrainedSchedule<32>,
        Tile,
        cute::Shape<cute::Int<TN>, cute::Int<TK / 32>>,
        Warp, Stages, true, 0, 0>;
    using Gemm = typename Types::Gemm;
    using PreparedGemm = dense_splitk_parallel_ppu::PreparedMultiformatLauncher<
        Types, Tile, Warp>;
    using Arguments = typename Gemm::Arguments;
    using GemmKernel = typename Types::GemmKernel;
    static_assert(!Types::CollectiveMainloop::is_packed_scale);
    static_assert(Types::MainloopPolicy::Descriptor::q4_kpack4_transpose);
    static_assert(Types::MainloopPolicy::ArtifactTileK == 0);

    static Arguments arguments(qwa_problem_v1 const& p, qwa_buffers_v1 const& b) {
        using namespace cute;
        auto a_stride = cutlass::make_cute_packed_stride(typename GemmKernel::StrideA{}, make_shape(p.m, p.k, 1));
        auto b_stride = cutlass::make_cute_packed_stride(typename GemmKernel::StrideB{}, make_shape(p.n, p.k, 1));
        auto c_stride = cutlass::make_cute_packed_stride(typename GemmKernel::StrideC{}, make_shape(p.m, p.n, 1));
        auto d_stride = cutlass::make_cute_packed_stride(typename GemmKernel::StrideD{}, make_shape(p.m, p.n, 1));
        auto s_stride = cutlass::make_cute_packed_stride(
            typename Types::CollectiveMainloop::StrideScale{}, make_shape(p.n, p.k / 32, 1));
        return {
            cutlass::gemm::GemmUniversalMode::kGemm, {p.m, p.n, p.k, 1},
            {static_cast<cutlass::half_t const*>(b.input), a_stride,
             static_cast<cutlass::int4b_t const*>(b.weight), b_stride,
             static_cast<cutlass::half_t const*>(b.scales), s_stride, 32, nullptr},
            {{1.f, 0.f}, nullptr, c_stride, static_cast<cutlass::half_t*>(b.output), d_stride},
            p.split
        };
    }

    static qwa_info_v1 query(qwa_problem_v1 const& p) {
        require(TM != 8 || p.m <= 7, "W4A16 M8 scale-first candidate admits M1..7");
        require(p.k % (TK * p.split) == 0 && p.k / (TK * p.split) >= Stages - 1,
                "W4A16 split must contain complete pipeline tiles");
        uint64_t shared = p.split == 1 ? Types::SharedStorageSize : PreparedGemm::SplitKernel::SharedStorageSize;
        require(shared <= 262144, "W4A16 candidate exceeds shared-memory limit");
        uint64_t workspace = p.split == 1 ? 0 : uint64_t(p.m) * p.n * p.split * sizeof(float);
        return {1, sizeof(qwa_info_v1), workspace, shared,
                int(cute::size(typename Types::CollectiveMainloop::TiledMma{})), 0};
    }

    struct Prepared : Plan {
        PreparedGemm gemm;
        Prepared(qwa_problem_v1 const& p, qwa_buffers_v1 const& b) {
            require(gemm.initialize(
                        static_cast<cutlass::half_t const*>(b.input),
                        static_cast<cutlass::int4b_t const*>(b.weight), b.scales, nullptr,
                        static_cast<cutlass::half_t*>(b.output), p.m, p.n, p.k, p.group_size,
                        p.split, static_cast<char*>(b.workspace), b.workspace_bytes,
                        static_cast<hggcStream_t>(b.stream)),
                    "W4A16 CUTLASS initialization failed");
        }
        int run(void* stream) override {
            return gemm.run(static_cast<hggcStream_t>(stream)) == cutlass::Status::kSuccess ? 0 : 41;
        }
    };

    static Plan* prepare(qwa_problem_v1 const& p, qwa_buffers_v1 const& b) {
        return new Prepared(p, b);
    }
};

}
