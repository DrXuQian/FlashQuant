#pragma once
#include "launch.cuh"
#include "actlize_extensions/cutlass/gemm/kernel/ppu_aiu_gemm_cooperative_k.hpp"

namespace quactlize::affine {
template<int TM,int TN,int TK,int WM,int WN,int Stages,int Cohorts>
struct CohortKernel {
    using Base = Kernel<TM,TN,TK,WM,WN,Stages>;
    using Mainloop = typename Base::Types::CollectiveMainloop;
    using Driver = cutlass::gemm::kernel::GemmUniversalMixedInputCooperativeK<Mainloop,Cohorts>;
    static qwa_info_v1 query(qwa_problem_v1 const& p) {
        require(p.split == 1, "cooperative K owns its partitioning");
        require(p.k % (TK*Cohorts) == 0 && p.k/(TK*Cohorts) >= Stages-1,
                "cooperative K requires equal complete pipeline slices");
        require(Driver::SharedStorageSize <= 262144, "cooperative K exceeds shared memory");
        return {1,sizeof(qwa_info_v1),0,Driver::SharedStorageSize,Driver::MaxThreadsPerBlock,0};
    }
    struct Prepared : Plan {
        typename Driver::Params params;
        dim3 grid;
        Prepared(qwa_problem_v1 const& p, qwa_buffers_v1 const& b)
            : grid((p.m+TM-1)/TM,p.n/TN,1) {
            query(p);
            auto base = Base::arguments(p,b);
            params = {base.problem_shape,
                      Mainloop::to_underlying_arguments(base.problem_shape,base.mainloop,nullptr),
                      static_cast<cutlass::half_t*>(b.output)};
            require(hggcFuncSetAttribute(cutlass::device_kernel<Driver>,
                        hggcFuncAttributeMaxDynamicSharedMemorySize,Driver::SharedStorageSize) == hggcSuccess,
                    "cooperative K shared-memory initialization failed");
        }
        int run(void* stream) override {
            void* arguments[] = {&params};
            return hggcLaunchKernel(
                reinterpret_cast<void const*>(cutlass::device_kernel<Driver>),grid,
                dim3(Driver::MaxThreadsPerBlock,1,1),arguments,Driver::SharedStorageSize,
                static_cast<hggcStream_t>(stream)) == hggcSuccess ? 0 : 41;
        }
    };
    static Plan* prepare(qwa_problem_v1 const& p,qwa_buffers_v1 const& b) { return new Prepared(p,b); }
};
}
