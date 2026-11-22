#pragma once
#include <type_traits>
#include "internal.hpp"
#include "format.hpp"
#include "quactlize_actlize.hpp"
#include "cutlass/device_kernel.h"
#include "actlize_extensions/cutlass/gemm/kernel/kpack_warpk_ppu.hpp"

namespace quactlize::affine {

template<int TM, int TN, int TK, int WM, int WN, int Stages, int WK,
         bool NativeA = false, bool VectorReduction = false, bool PadGridTo40 = false,
         bool NativeB = false, bool ChunkA = false, bool BoundedReduction = false,
         bool ChunkReduction = false, int StaticN = 0, int StaticK = 0, int MinBlocks = 1,
         bool StageCycles = false, int GlobalSlices = 1,
         int FusedStoreWarps = 0, bool PersistentMN = false, int MmaM8 = 0,
         bool RegisterPrefetch = false, bool PairedScales = false,
         bool FullRegisterPipeline = false, int GridMultiple = 40,
         bool VectorOutput = false, bool DirectOutput = false,
         bool UnrollCycles = false, int CompilerFence = 0,
         bool OpaqueCoordinates = false, bool SharedB = false,
         bool UnsignedIndices = false, bool InterleaveA = false, int StreamKWorkers = 0,
         bool NFastRaster = false, int StaticM = 0, bool PruneRows = false,
         bool TailM8 = false, bool CacheScales = false, int CompactOutput = 0,
         bool SkipStage2Barrier = false, int ReductionStorage = 0, int DirectA = 0,
         int CohortPipeline = 0, int WarpOrder = 0, int BProducerWarp = 0,
         bool PrefetchReduction = false, bool GroupOutputStores = false,
         bool IntegerZero = false, bool ZeroWordLoad = false, bool SingleZeroBias = false,
         bool InterleaveZeroGroups = false, bool PairedZeroBias = false,
         bool CacheZeroBias = false, bool PermuteZeroBias = false,
         bool PreparedZeroBias = false, bool ByteZeroWords = false,
         bool InlineReduction = false, int RasterGroupM = 1, int StreamKMode = 0,
         int GlobalOutputPadding = 8, bool PersistentPrefetch = false>
struct CooperativeKernel {
    static_assert(TM % WM == 0);
    static_assert(GridMultiple>0);
    static_assert(!SkipStage2Barrier || (GlobalSlices==1 && StreamKWorkers==0),
                  "the stage2 barrier experiment admits whole-K tiles only");
    using Mainloop = cutlass::gemm::collective::NativeInt4WarpKCollectivePPU<
        TM,TN,TK,WN,WK,Stages,NativeA,kClassicWeights,NativeB,ChunkA,StageCycles,
        MmaM8,RegisterPrefetch,PairedScales,FullRegisterPipeline,WM<16 ? 8 : 16,WM,UnrollCycles,
        CompilerFence,OpaqueCoordinates,SharedB,UnsignedIndices,InterleaveA,TailM8,CacheScales,
        SkipStage2Barrier,DirectA,CohortPipeline,BProducerWarp,IntegerZero,ZeroWordLoad,SingleZeroBias,
        InterleaveZeroGroups,PairedZeroBias,CacheZeroBias,PermuteZeroBias,PreparedZeroBias,ByteZeroWords>;
    using Driver = cutlass::gemm::kernel::KPackWarpKKernelPPU<
        Mainloop,VectorReduction,PadGridTo40,BoundedReduction,ChunkReduction,
        StaticN,StaticK,MinBlocks,GlobalSlices,FusedStoreWarps,PersistentMN,
        VectorOutput,DirectOutput,StreamKWorkers,NFastRaster,StaticM,PruneRows,CompactOutput,
        ReductionStorage,WarpOrder,PrefetchReduction,GroupOutputStores,InlineReduction,RasterGroupM,
        StreamKMode,GlobalOutputPadding,PersistentPrefetch>;
    // Keep the whole-K prefix's compiled mainloop and resource footprint
    // independent of the FP32 completion path used by the final wave.
    using PrefixDriver = std::conditional_t<StreamKMode==3,
        cutlass::gemm::kernel::KPackWarpKKernelPPU<
            Mainloop,VectorReduction,PadGridTo40,BoundedReduction,ChunkReduction,
            StaticN,StaticK,MinBlocks,1,0,true,
            VectorOutput,DirectOutput,0,NFastRaster,StaticM,PruneRows,CompactOutput,
            ReductionStorage,WarpOrder,PrefetchReduction,GroupOutputStores,InlineReduction,
            RasterGroupM,0,8>,Driver>;
    static constexpr int SharedStorageSize =
        Driver::SharedStorageSize>PrefixDriver::SharedStorageSize ?
        Driver::SharedStorageSize : PrefixDriver::SharedStorageSize;
    static_assert(Mainloop::MappingId == kWeightMappingId);
    static constexpr bool NeedsCompletion=GlobalSlices>1 || StreamKWorkers>0;
    static auto streamk_schedule(qwa_problem_v1 const& p) {
        uint64_t const tiles=((uint64_t(p.m)+TM-1)/TM)*(p.n/TN);
        require(tiles<=uint64_t(INT32_MAX),"Stream-K tile count exceeds its index range");
        if constexpr (StreamKMode>=2)
            return cutlass::gemm::kernel::KPackStreamKSchedulePPU::make_tail(
                uint32_t(tiles),uint32_t(p.k/TK),StreamKWorkers);
        else
            return cutlass::gemm::kernel::KPackStreamKSchedulePPU::make(
                uint32_t(tiles),uint32_t(p.k/TK),StreamKWorkers);
    }
    static auto workspace_layout(qwa_problem_v1 const& p) {
        if constexpr (StreamKWorkers>0)
            return cutlass::gemm::kernel::fixed_splitk::make_completion_workspace(
                uint64_t(2)*StreamKWorkers*TM*TN*sizeof(float),uint64_t(StreamKWorkers));
        else
            return cutlass::gemm::kernel::fixed_splitk::make_completion_workspace(
                size_t(p.m)*p.n*sizeof(float)*GlobalSlices,uint64_t(p.n/TN));
    }
    static uint64_t scale_workspace_offset(qwa_problem_v1 const& p) {
        if constexpr (NeedsCompletion)
            return (workspace_layout(p).total_bytes+127)&~uint64_t(127);
        return 0;
    }
    static uint64_t zero_workspace_offset(qwa_problem_v1 const& p) {
        return scale_workspace_offset(p)+uint64_t(p.n)*p.k/16;
    }
    static qwa_info_v1 query(qwa_problem_v1 const& p) {
        require(p.zero_mode==int(IntegerZero),"candidate quantization mode does not match");
        if constexpr (StaticM>0) require(p.m==StaticM,"specialized M does not match the problem");
        if constexpr (StaticN>0) require(p.n==StaticN,"specialized N does not match the problem");
        if constexpr (StaticK>0) require(p.k==StaticK,"specialized K does not match the problem");
        require(p.split == GlobalSlices, "candidate requires its compiled K partition count");
        require(p.n % TN == 0 && p.k % TK == 0, "warp-K candidate requires whole N/K tiles");
        require(p.k / TK >= Stages - 1, "warp-K candidate requires a complete pipeline prime");
        if constexpr (PersistentPrefetch)
            require(cutlass::gemm::kernel::KPackMNPipelinePPU::aligned(p.k/TK,Stages),
                    "persistent-prefetch candidate requires aligned whole stage cycles");
        require(SharedStorageSize <= 262144, "warp-K candidate exceeds shared memory");
        if constexpr (StreamKWorkers>0) {
            auto schedule=streamk_schedule(p);
            require(schedule.valid() && schedule.units<=uint32_t(INT32_MAX),
                    "Stream-K scheduling domain is empty or exceeds its index range");
            require(schedule.max_contributors()<=2,
                    "Stream-K candidate admits at most two contributors per output tile");
        }
        uint64_t bytes=0;
        if constexpr (NeedsCompletion) {
            if constexpr (GlobalSlices>1) {
                require(p.m<=TM,"fused K partition requires one M tile");
                require((p.k/TK)%GlobalSlices==0,"fused K partitions require equal whole K tiles");
            }
            auto layout=workspace_layout(p);
            require(layout.is_valid() && layout.total_bytes<=64*1024*1024,
                    "fused K workspace exceeds its bounded envelope");
            bytes=layout.total_bytes;
        }
        if constexpr (PairedScales) {
            bytes=scale_workspace_offset(p)+uint64_t(p.n)*p.k/16;
        }
        if constexpr (IntegerZero)
            bytes=zero_workspace_offset(p)+uint64_t(p.n)*p.k/(ByteZeroWords ? 32 : 64)+sizeof(unsigned);
        if constexpr (PreparedZeroBias)
            bytes=scale_workspace_offset(p)+uint64_t(p.n)*p.k/8+sizeof(unsigned);
        require(bytes<=64*1024*1024,"prepared metadata workspace exceeds its bounded envelope");
        return {1,sizeof(qwa_info_v1),bytes,SharedStorageSize,Driver::MaxThreadsPerBlock,0};
    }
    struct Prepared : Plan {
        typename Driver::Params params;
        std::conditional_t<StreamKMode==3,typename PrefixDriver::Params,int> prefix_params{};
        dim3 grid;
        Prepared(qwa_problem_v1 const& p, qwa_buffers_v1 const& b)
            : params{Mainloop::make_params(p.m,p.n,p.k,static_cast<cutlass::half_t const*>(b.input),
                       static_cast<uint16_t const*>(b.weight),static_cast<cutlass::half_t const*>(b.scales)),
                     static_cast<cutlass::half_t*>(b.output),
                     cutlass::FastDivmod((p.m+TM-1)/TM),((p.m+TM-1)/TM)*(p.n/TN)},
              grid((p.m+TM-1)/TM,p.n/TN,1) {
            query(p);
            if constexpr (PadGridTo40)
                grid = dim3((params.tile_count+GridMultiple-1)/GridMultiple*GridMultiple,1,1);
            if constexpr (PersistentMN) grid=dim3(GridMultiple,1,1);
            if constexpr (StreamKWorkers>0) {
                params.streamk=streamk_schedule(p);
                grid=dim3(StreamKWorkers,1,1);
            }
            if constexpr (NeedsCompletion) {
                auto layout=workspace_layout(p);
                params.partials=static_cast<float*>(b.workspace);
                params.counters=reinterpret_cast<int32_t*>(
                    static_cast<char*>(b.workspace)+layout.counter_offset);
                if constexpr (GlobalSlices>1) {
                    int tasks=params.tile_count*GlobalSlices;
                    if constexpr (PadGridTo40) tasks=(tasks+GridMultiple-1)/GridMultiple*GridMultiple;
                    grid=dim3(tasks,1,1);
                }
                auto stream=static_cast<hggcStream_t>(b.stream);
                require(hggcMemsetAsync(params.counters,0,layout.counter_bytes,stream)==hggcSuccess &&
                        hggcStreamSynchronize(stream)==hggcSuccess,
                        "fused K counter initialization failed");
            }
            if constexpr (PreparedZeroBias) {
                using Copy=cutlass::gemm::kernel::KPackScaleZeroBiasCopyPPU;
                auto* packed=static_cast<char*>(b.workspace)+scale_workspace_offset(p);
                auto* invalid=reinterpret_cast<unsigned*>(packed+uint64_t(p.n)*p.k/8);
                typename Copy::Params copy{int(int64_t(p.n)*p.k/64),
                    static_cast<uint16_t const*>(b.scales),static_cast<uint8_t const*>(b.zeros),
                    reinterpret_cast<uint2*>(packed),invalid};
                void* arguments[]={&copy};
                auto stream=static_cast<hggcStream_t>(b.stream);
                require(hggcMemsetAsync(invalid,0,sizeof(unsigned),stream)==hggcSuccess &&
                    hggcLaunchKernel(
                        reinterpret_cast<void const*>(cutlass::device_kernel<Copy>),
                        dim3((copy.pairs+Copy::MaxThreadsPerBlock-1)/Copy::MaxThreadsPerBlock,1,1),
                        dim3(Copy::MaxThreadsPerBlock,1,1),arguments,0,stream)==hggcSuccess &&
                    hggcStreamSynchronize(stream)==hggcSuccess,"scale/zero bias preparation failed");
                unsigned invalid_value=0;
                require(hggcMemcpy(&invalid_value,invalid,sizeof(unsigned),hggcMemcpyDeviceToHost)==hggcSuccess,
                        "integer-zero validation transfer failed");
                require(invalid_value==0,"integer zero points must be in [0,15]");
                params.mainloop.scales=reinterpret_cast<cutlass::half_t const*>(packed);
            } else {
            if constexpr (PairedScales) {
                using Copy=cutlass::gemm::kernel::KPackScalePairCopyPPU;
                auto* packed=static_cast<char*>(b.workspace)+scale_workspace_offset(p);
                typename Copy::Params copy{int(int64_t(p.n)*p.k/64),
                    static_cast<uint16_t const*>(b.scales),reinterpret_cast<uint32_t*>(packed)};
                void* arguments[]={&copy};
                auto stream=static_cast<hggcStream_t>(b.stream);
                require(hggcLaunchKernel(
                    reinterpret_cast<void const*>(cutlass::device_kernel<Copy>),
                    dim3((copy.pairs+Copy::MaxThreadsPerBlock-1)/Copy::MaxThreadsPerBlock,1,1),
                    dim3(Copy::MaxThreadsPerBlock,1,1),arguments,0,stream)==hggcSuccess &&
                    hggcStreamSynchronize(stream)==hggcSuccess,"scale metadata preparation failed");
                params.mainloop.scales=reinterpret_cast<cutlass::half_t const*>(packed);
            }
            if constexpr (IntegerZero) {
                using Copy=cute::conditional_t<ByteZeroWords,
                    cutlass::gemm::kernel::KPackIntegerZeroByteCopyPPU,
                    cutlass::gemm::kernel::KPackIntegerZeroPairCopyPPU<Mainloop::ZeroGroupInterleave>>;
                auto* packed=static_cast<char*>(b.workspace)+zero_workspace_offset(p);
                auto* invalid=reinterpret_cast<unsigned*>(
                    packed+uint64_t(p.n)*p.k/(ByteZeroWords ? 32 : 64));
                int const elements=int(int64_t(p.n)*p.k/(ByteZeroWords ? 128 : 64));
                typename Copy::Params copy{elements,p.n,
                    static_cast<uint8_t const*>(b.zeros),reinterpret_cast<uint8_t*>(packed),invalid};
                void* arguments[]={&copy};
                auto stream=static_cast<hggcStream_t>(b.stream);
                require(hggcMemsetAsync(invalid,0,sizeof(unsigned),stream)==hggcSuccess &&
                    hggcLaunchKernel(
                        reinterpret_cast<void const*>(cutlass::device_kernel<Copy>),
                        dim3((elements+Copy::MaxThreadsPerBlock-1)/Copy::MaxThreadsPerBlock,1,1),
                        dim3(Copy::MaxThreadsPerBlock,1,1),arguments,0,stream)==hggcSuccess &&
                    hggcStreamSynchronize(stream)==hggcSuccess,"integer-zero preparation failed");
                unsigned invalid_value=0;
                require(hggcMemcpy(&invalid_value,invalid,sizeof(unsigned),hggcMemcpyDeviceToHost)==hggcSuccess,
                        "integer-zero validation transfer failed");
                require(invalid_value==0,"integer zero points must be in [0,15]");
                params.mainloop.zeros=reinterpret_cast<uint8_t const*>(packed);
            }
            }
            require(hggcFuncSetAttribute(cutlass::device_kernel<Driver>,
                         hggcFuncAttributeMaxDynamicSharedMemorySize, Driver::SharedStorageSize) == hggcSuccess,
                    "warp-K shared-memory initialization failed");
            if constexpr (StreamKMode==3) {
                prefix_params={params.mainloop,params.output,params.m_tiles,
                               params.tile_count-int(params.streamk.tiles)};
                if(prefix_params.tile_count>0)
                    require(hggcFuncSetAttribute(cutlass::device_kernel<PrefixDriver>,
                                hggcFuncAttributeMaxDynamicSharedMemorySize,
                                PrefixDriver::SharedStorageSize)==hggcSuccess,
                            "whole-K prefix shared-memory initialization failed");
            }
        }
        int run(void* stream) override {
            if constexpr (StreamKMode==3) {
                if(prefix_params.tile_count>0) {
                    void* prefix_arguments[]={&prefix_params};
                    if(hggcLaunchKernel(
                        reinterpret_cast<void const*>(cutlass::device_kernel<PrefixDriver>),
                        dim3(GridMultiple,1,1),dim3(PrefixDriver::MaxThreadsPerBlock,1,1),
                        prefix_arguments,PrefixDriver::SharedStorageSize,
                        static_cast<hggcStream_t>(stream))!=hggcSuccess) return 41;
                }
            }
            void* arguments[] = {&params};
            return hggcLaunchKernel(
                reinterpret_cast<void const*>(cutlass::device_kernel<Driver>), grid,
                dim3(Driver::MaxThreadsPerBlock,1,1), arguments, Driver::SharedStorageSize,
                static_cast<hggcStream_t>(stream)) == hggcSuccess ? 0 : 41;
        }
    };
    static Plan* prepare(qwa_problem_v1 const& p, qwa_buffers_v1 const& b) { return new Prepared(p,b); }
};

}
