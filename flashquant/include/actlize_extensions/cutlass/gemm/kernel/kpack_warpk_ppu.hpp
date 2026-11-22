// Copyright (c) 2026, quactlize contributors.
// SPDX-License-Identifier: BSD-3-Clause
#pragma once
#include "actlize_extensions/cutlass/gemm/collective/kpack_warpk_ppu.hpp"
#include "actlize_extensions/cutlass/gemm/kernel/marlin_output_map_ppu.hpp"
#include "actlize_extensions/cutlass/gemm/kernel/ppu_fixed_splitk_last_arriver.hpp"
#include "actlize_extensions/cutlass/gemm/kernel/kpack_streamk_schedule.hpp"
#include "cutlass/fast_math.h"

namespace cutlass::gemm::kernel {

// Preparation-only, bit-preserving metadata copy. The public input remains
// group-major FP16; each N16 block becomes (n0,n8),(n1,n9),...,(n7,n15).
struct KPackScalePairCopyPPU {
  static constexpr int MaxThreadsPerBlock=256;
  static constexpr int MinBlocksPerMultiprocessor=1;
  struct Params {
    int pairs;
    uint16_t const* source;
    uint32_t* destination;
  };
  CUTLASS_HOST_DEVICE static constexpr int source_index(int pair) {
    return (pair/8)*16+pair%8;
  }
  CUTLASS_DEVICE void operator()(Params const& p,char*) {
    for(int pair=int(blockIdx.x)*MaxThreadsPerBlock+int(threadIdx.x);
        pair<p.pairs;pair+=int(gridDim.x)*MaxThreadsPerBlock) {
      int const source=source_index(pair);
      p.destination[pair]=uint32_t(p.source[source]) |
                          (uint32_t(p.source[source+8])<<16);
    }
  }
};

// Each record contains two unchanged FP16 scales followed by the exact FP16
// encodings of 1024+z for those columns. Only metadata expands during prepare.
struct KPackScaleZeroBiasCopyPPU {
  static constexpr int MaxThreadsPerBlock=256;
  static constexpr int MinBlocksPerMultiprocessor=1;
  struct Params {
    int pairs;
    uint16_t const* scales;
    uint8_t const* zeros;
    uint2* destination;
    unsigned* invalid;
  };
  CUTLASS_DEVICE void operator()(Params const& p,char*) {
    for(int pair=int(blockIdx.x)*MaxThreadsPerBlock+int(threadIdx.x);
        pair<p.pairs;pair+=int(gridDim.x)*MaxThreadsPerBlock) {
      int const source=KPackScalePairCopyPPU::source_index(pair);
      unsigned const lo=p.zeros[source],hi=p.zeros[source+8];
      if(lo>15 || hi>15) atomicOr(p.invalid,1u);
      p.destination[pair]=make_uint2(
          uint32_t(p.scales[source])|(uint32_t(p.scales[source+8])<<16),
          (0x6400u|(lo&15))|((0x6400u|(hi&15))<<16));
    }
  }
};

// A word contains z(g,n), z(g,n+8), z(g+1,n), z(g+1,n+8), with even g.
// Each thread owns a whole word; no overlapping byte/halfword writes.
struct KPackIntegerZeroByteCopyPPU {
  static constexpr int MaxThreadsPerBlock=256;
  static constexpr int MinBlocksPerMultiprocessor=1;
  struct Params {
    int words,n;
    uint8_t const* source;
    uint8_t* destination;
    unsigned* invalid;
  };
  CUTLASS_DEVICE void operator()(Params const& p,char*) {
    for(int word=int(blockIdx.x)*MaxThreadsPerBlock+int(threadIdx.x);
        word<p.words;word+=int(gridDim.x)*MaxThreadsPerBlock) {
      int const first_pair=(word/(p.n/2))*p.n+word%(p.n/2);
      int const source=KPackScalePairCopyPPU::source_index(first_pair);
      uint32_t const a=p.source[source],b=p.source[source+8];
      uint32_t const c=p.source[source+p.n],d=p.source[source+p.n+8];
      if((a|b|c|d)>15) atomicOr(p.invalid,1u);
      reinterpret_cast<uint32_t*>(p.destination)[word]=a|(b<<8)|(c<<16)|(d<<24);
    }
  }
};

template<int InterleaveGroups = 1>
struct KPackIntegerZeroPairCopyPPU {
  static_assert(InterleaveGroups==1 || InterleaveGroups==2 || InterleaveGroups==4);
  static constexpr int MaxThreadsPerBlock=256;
  static constexpr int MinBlocksPerMultiprocessor=1;
  struct Params {
    int pairs,n;
    uint8_t const* source;
    uint8_t* destination;
    unsigned* invalid;
  };
  CUTLASS_DEVICE void operator()(Params const& p,char*) {
    for(int pair=int(blockIdx.x)*MaxThreadsPerBlock+int(threadIdx.x);
        pair<p.pairs;pair+=int(gridDim.x)*MaxThreadsPerBlock) {
      int const source=KPackScalePairCopyPPU::source_index(pair);
      unsigned const lo=p.source[source],hi=p.source[source+8];
      if(lo>15 || hi>15) atomicOr(p.invalid,1u);
      int destination=pair;
      if constexpr (InterleaveGroups>1) {
        int const group=pair/(p.n/2),column_pair=pair%(p.n/2);
        destination=((group/InterleaveGroups)*(p.n/2)+column_pair)*InterleaveGroups+
                    group%InterleaveGroups;
      }
      p.destination[destination]=uint8_t((lo&15)|((hi&15)<<4));
    }
  }
};

template<class Mainloop, bool VectorReduction = false, bool PadGridTo40 = false,
         bool BoundedReduction = false, bool ChunkReduction = false,
         int StaticN = 0, int StaticK = 0, int MinBlocks = 1, int GlobalSlices = 1,
         int FusedStoreWarps = 0, bool PersistentMN = false,
         bool VectorOutput = false, bool DirectOutput = false, int StreamKWorkers = 0,
         bool NFastRaster = false, int StaticM = 0, bool PruneRows = false,
         int CompactOutput = 0, int ReductionStorage = 0, int WarpOrder = 0,
         bool PrefetchReduction = false, bool GroupOutputStores = false,
         bool InlineReduction = false, int RasterGroupM = 1, int StreamKMode = 0,
         int GlobalOutputPadding = 8, bool PersistentPrefetch = false>
struct KPackWarpKKernelPPU {
  using CollectiveMainloop = Mainloop;
  using TileShape = typename Mainloop::TileShape;
  static constexpr int TM = int(cute::size<0>(TileShape{}));
  static constexpr int TN = int(cute::size<1>(TileShape{}));
  static constexpr int MaxThreadsPerBlock = Mainloop::Threads;
  static constexpr int MinBlocksPerMultiprocessor = MinBlocks;
  static constexpr int Values = Mainloop::MAtoms * Mainloop::NAtoms * Mainloop::FragmentValues;
  static constexpr int CohortValues = CompactOutput ? StaticM*TN : Mainloop::OutputThreads*Values;
  static constexpr int SliceValues = Mainloop::NAtoms*Mainloop::FragmentValues;
  static constexpr int SliceWords = Mainloop::OutputThreads*SliceValues;
  static_assert(!DirectOutput || GlobalSlices==1);
  static constexpr int ReductionValues =
      Mainloop::WarpK > 1
        ? (Mainloop::WarpK-1)*(ChunkReduction ? SliceWords : CohortValues)
        : 1;
  static_assert(!BoundedReduction || VectorReduction);
  static_assert(!ChunkReduction || (VectorReduction && !BoundedReduction));
  static_assert(!ChunkReduction || (Mainloop::WarpK & (Mainloop::WarpK-1)) == 0);
  static_assert(GlobalSlices==1 || GlobalSlices==2 || GlobalSlices==4 || GlobalSlices==8);
  static_assert(!PersistentMN || GlobalSlices==1);
  static_assert(!PersistentPrefetch ||
      (PersistentMN && DirectOutput && Mainloop::WarpK==1 &&
       GlobalSlices==1 && StreamKWorkers==0),
      "persistent prefetch requires whole-K, warp-K1 direct output");
  static_assert(StreamKWorkers>=0);
  static_assert(StreamKMode>=0 && StreamKMode<=3);
  static_assert(!StreamKMode || StreamKWorkers>0);
  static_assert(GlobalOutputPadding==0 || GlobalOutputPadding==8);
  static_assert(GlobalOutputPadding==8 || GlobalSlices>1 || StreamKWorkers>0);
  static_assert(!StreamKWorkers || (GlobalSlices==1 && !PersistentMN));
  static_assert(!NFastRaster || PadGridTo40 || PersistentMN || StreamKWorkers>0,
                "N-fast raster requires the flattened tile grid");
  static_assert(RasterGroupM>=1 && RasterGroupM<=16);
  static_assert(RasterGroupM==1 || NFastRaster,
                "grouped M raster requires the flattened N-fast grid");
  static_assert(!PruneRows || (StaticM>0 && StaticM<=TM),
                "pruned output rows require a single statically admitted M tile");
  static_assert(CompactOutput>=0 && CompactOutput<=2);
  static_assert(!CompactOutput ||
      (TM==16 && Mainloop::WarpM==1 && Mainloop::InstructionM==16 &&
       StaticM>0 && StaticM<=16 && PruneRows && VectorReduction && !ChunkReduction &&
       GlobalSlices==1 && StreamKWorkers==0),
      "compact output is a statically admitted single-M16-tile specialization");
  static_assert(CompactOutput!=2 || DirectOutput);
  static_assert(ReductionStorage>=0 && ReductionStorage<=2);
  static_assert(!ReductionStorage ||
      (Mainloop::WarpK>1 && !ChunkReduction && GlobalSlices==1 && StreamKWorkers==0),
      "disjoint reduction currently admits the whole-K, flat cohort reduction");
  static_assert(FusedStoreWarps>=0 && FusedStoreWarps*32<=MaxThreadsPerBlock);
  static_assert(WarpOrder>=0 && WarpOrder<=3);
  static_assert(!WarpOrder || Mainloop::WarpM==1,
                "warp remapping currently admits one M warp cohort");
  static_assert(WarpOrder!=2 || (Mainloop::WarpN&(Mainloop::WarpN-1))==0);
  static_assert(WarpOrder!=3 || (Mainloop::WarpK&(Mainloop::WarpK-1))==0);
  static_assert(!PrefetchReduction ||
      (VectorReduction && !BoundedReduction && !ChunkReduction && Mainloop::WarpK>1));
  static_assert(!InlineReduction ||
      (VectorReduction && !BoundedReduction && !ChunkReduction &&
       !PrefetchReduction && Mainloop::WarpK>1));
  static_assert(!GroupOutputStores || DirectOutput);

  CUTLASS_HOST_DEVICE static constexpr uint32_t logical_thread(uint32_t physical) {
    if constexpr (WarpOrder==0) return physical;
    uint32_t const warp=physical/32;
    uint32_t n=warp%Mainloop::WarpN,k=warp/Mainloop::WarpN;
    if constexpr (WarpOrder==1) {
      n=warp/Mainloop::WarpK;
      k=warp%Mainloop::WarpK;
    } else if constexpr (WarpOrder==2) {
      n^=k&(Mainloop::WarpN-1);
    } else if constexpr (WarpOrder==3) {
      k^=n&(Mainloop::WarpK-1);
    }
    return (k*Mainloop::WarpN+n)*32+physical%32;
  }
  struct Params {
    typename Mainloop::Params mainloop;
    half_t* output;
    cutlass::FastDivmod m_tiles;
    int tile_count;
    float* partials=nullptr;
    int32_t* counters=nullptr;
    KPackStreamKSchedulePPU streamk{};
  };
  union TileStorage {
    typename Mainloop::SharedStorage mainloop;
    alignas(128) half_t output[TM * (TN + 8)];
    alignas(128) float fp32_output[
        GlobalSlices>1 || StreamKWorkers>0 ? TM*(TN+GlobalOutputPadding) : 1];
    typename fixed_splitk::LastArriverM1Fp16Completion<8>::SharedStorage completion;
  };
  union AliasedStorage {
    TileStorage tile;
    alignas(128) float partial[ReductionValues];
  };
  struct DisjointStorage {
    TileStorage tile;
    alignas(128) float partial[ReductionValues];
  };
  using SharedStorage=std::conditional_t<ReductionStorage!=0,DisjointStorage,AliasedStorage>;
  static constexpr int SharedStorageSize = sizeof(SharedStorage);

  CUTLASS_DEVICE static void map_tile(Params const& p,int task,int& tile_m,int& tile_n) {
    if constexpr (NFastRaster) {
      uint32_t const n_tiles=StaticN>0 ? StaticN/TN : p.mainloop.n/TN;
      uint32_t const m=StaticM>0 ? StaticM : p.mainloop.m;
      auto const tile=grouped_mn_tile<RasterGroupM>(uint32_t(task),(m+TM-1)/TM,n_tiles);
      tile_m=int(tile.m);
      tile_n=int(tile.n);
    } else {
      p.m_tiles(tile_n,tile_m,task);
    }
  }

  static constexpr bool partial_vectors_have_one_row() {
    for(int lane=0;lane<32;++lane)
      for(int v=0;v<Mainloop::FragmentValues;v+=4)
        for(int j=1;j<4;++j)
          if(marlin_ppu_detail::output_row<Mainloop::InstructionM>(lane,v)!=
             marlin_ppu_detail::output_row<Mainloop::InstructionM>(lane,v+j)) return false;
    return true;
  }

  CUTLASS_DEVICE static bool output_value_is_live(int output_tid,int value,int ma_offset=0) {
    static_assert(!(PruneRows || Mainloop::PaddedOutputRows) || partial_vectors_have_one_row(),
                  "a masked FP32 vector must belong to one output row");
    if constexpr (!PruneRows && !Mainloop::PaddedOutputRows) return true;
    int const row=(output_tid/(32*Mainloop::WarpN))*Mainloop::WarpTileM+
        (ma_offset+value/SliceValues)*Mainloop::InstructionM+
        marlin_ppu_detail::output_row<Mainloop::InstructionM>(
            output_tid%32,value%Mainloop::FragmentValues);
    return row<(PruneRows ? StaticM : TM);
  }

  CUTLASS_DEVICE static int partial_vector_position(int output_tid,int value) {
    if constexpr (CompactOutput) {
      return 4*marlin_ppu_detail::compact_partial_vector_slot<Mainloop::InstructionM>(
          StaticM,Mainloop::NAtoms,output_tid/32,output_tid%32,
          value/Mainloop::FragmentValues,value%Mainloop::FragmentValues);
    }
    return ((value/4)*Mainloop::OutputThreads+output_tid)*4;
  }

  CUTLASS_DEVICE static void add_partial_vector(
      float* values, float const* source) {
    // Keep the shared vector's temporary values beside their FP32 additions.
    // This is an instruction scheduling experiment, not a fused hardware op.
    uint32_t const address=uint32_t(__cvta_generic_to_shared(source));
    asm volatile(
        "{ .reg .f32 peer0,peer1,peer2,peer3;\n"
        "ld.shared.v4.b32 {peer0,peer1,peer2,peer3},[%4];\n"
        "add.rn.f32 %0,%0,peer0;\n"
        "add.rn.f32 %1,%1,peer1;\n"
        "add.rn.f32 %2,%2,peer2;\n"
        "add.rn.f32 %3,%3,peer3;\n"
        "}\n"
        : "+f"(values[0]),"+f"(values[1]),"+f"(values[2]),"+f"(values[3])
        : "r"(address) : "memory");
  }

  CUTLASS_DEVICE static void write_slice(
      SharedStorage& shared, float const* values, int slot, int output_tid,int ma) {
    #pragma unroll
    for(int i=0;i<SliceValues;i+=4) {
      if(!output_value_is_live(output_tid,i,ma)) continue;
      int const position=((i/4)*Mainloop::OutputThreads+output_tid)*4;
      *reinterpret_cast<float4*>(&shared.partial[slot*SliceWords+position])=
          make_float4(values[i],values[i+1],values[i+2],values[i+3]);
    }
  }

  CUTLASS_DEVICE static void add_slice(
      SharedStorage const& shared, float* values, int slot, int output_tid,int ma) {
    #pragma unroll
    for(int i=0;i<SliceValues;i+=4) {
      if(!output_value_is_live(output_tid,i,ma)) continue;
      int const position=((i/4)*Mainloop::OutputThreads+output_tid)*4;
      float4 const value=*reinterpret_cast<float4 const*>(
          &shared.partial[slot*SliceWords+position]);
      values[i]+=value.x;
      values[i+1]+=value.y;
      values[i+2]+=value.z;
      values[i+3]+=value.w;
    }
  }

  CUTLASS_DEVICE static void reduce_chunks(
      SharedStorage& shared, float* values, int warp_k, int output_tid) {
    #pragma unroll
    for(int ma=0;ma<Mainloop::MAtoms;++ma) {
      float* const chunk=values+ma*SliceValues;
      if constexpr (Mainloop::WarpK<=4) {
        if(warp_k!=0) write_slice(shared,chunk,warp_k-1,output_tid,ma);
        __syncthreads();
        if(warp_k==0) {
          #pragma unroll
          for(int peer=0;peer<Mainloop::WarpK-1;++peer)
            add_slice(shared,chunk,peer,output_tid,ma);
        }
      } else {
        #pragma unroll
        for(int active=Mainloop::WarpK;active>1;active/=2) {
          int const half=active/2,first_slot=Mainloop::WarpK-active;
          // Each level writes fresh slots, so it cannot overwrite a previous
          // level's in-flight reads. The barrier below publishes all writers.
          if(warp_k>=half && warp_k<active)
            write_slice(shared,chunk,first_slot+warp_k-half,output_tid,ma);
          __syncthreads();
          if(warp_k<half) add_slice(shared,chunk,first_slot+warp_k,output_tid,ma);
        }
      }
      // The next M16 slice reuses the same scratch.
      if(!DirectOutput || ma+1<Mainloop::MAtoms) __syncthreads();
    }
  }

  static constexpr bool packed_output_map_is_adjacent() {
    for(int lane=0;lane<32;lane+=2)
      for(int v=0;v<Mainloop::FragmentValues;v+=2) {
        if(marlin_ppu_detail::output_row<Mainloop::InstructionM>(lane,v)!=
           marlin_ppu_detail::output_row<Mainloop::InstructionM>(lane+1,v+1)) return false;
        for(int j=0;j<2;++j) {
          int col=marlin_ppu_detail::output_col_offset<Mainloop::InstructionM>(lane,v+j);
          if(col%2 || col+1!=
             marlin_ppu_detail::output_col_offset<Mainloop::InstructionM>(lane+1,v+j))
            return false;
        }
      }
    return true;
  }

  template<bool MaskEarly = false>
  CUTLASS_DEVICE static void store_packed_output(
      half_t* destination,typename Mainloop::Accumulator const& acc,
      int lane,int warp_n,int stride,int rows) {
    static_assert(packed_output_map_is_adjacent());
    static_assert(!GroupOutputStores || partial_vectors_have_one_row());
    constexpr int GroupValues=GroupOutputStores ? 4 : 2;
    // Two values in one lane are four columns apart. Convert first, then
    // exchange packed halves between adjacent lanes to obtain contiguous C.
    #pragma unroll
    for(int ma=0;ma<Mainloop::MAtoms;++ma)
      #pragma unroll
      for(int na=0;na<Mainloop::NAtoms;++na)
        #pragma unroll
        for(int v=0;v<Mainloop::FragmentValues;v+=GroupValues) {
          int const row=Mainloop::warp_m()*Mainloop::WarpTileM+ma*Mainloop::InstructionM+
              marlin_ppu_detail::output_row<Mainloop::InstructionM>(lane,v);
          if constexpr (MaskEarly) {
            if(row>=rows) continue;
          }
          auto const& values=acc.tile[ma][na].value;
          uint32_t const mask=MaskEarly ? __activemask() : 0xffffffffu;
          uint32_t pairs[GroupValues/2];
          int columns[GroupValues/2];
          #pragma unroll
          for(int j=0;j<GroupValues/2;++j) {
            int const value=v+2*j;
            __half2 const converted=__float22half2_rn(make_float2(values[value],values[value+1]));
            uint32_t const packed=reinterpret_cast<uint32_t const&>(converted);
            uint32_t const peer=__shfl_xor_sync(mask,packed,1);
            pairs[j]=__byte_perm(packed,peer,(lane&1) ? 0x3276 : 0x5410);
            columns[j]=warp_n*Mainloop::NAtoms*16+na*16+
                marlin_ppu_detail::output_col_offset<Mainloop::InstructionM>(lane&~1,value+(lane&1));
          }
          if(row<rows) {
            #pragma unroll
            for(int j=0;j<GroupValues/2;++j)
              *reinterpret_cast<uint32_t*>(destination+row*stride+columns[j])=pairs[j];
          }
        }
  }

  template<class Output,int Padding = 8>
  CUTLASS_DEVICE static void stage_output(
      Output* destination, typename Mainloop::Accumulator const& acc, int lane, int warp_n) {
    if constexpr (VectorOutput && std::is_same_v<Output,half_t>) {
      store_packed_output(destination,acc,lane,warp_n,TN+Padding,PruneRows ? StaticM : TM);
    } else {
    #pragma unroll
    for(int ma=0;ma<Mainloop::MAtoms;++ma)
      #pragma unroll
      for(int na=0;na<Mainloop::NAtoms;++na)
        #pragma unroll
        for(int v=0;v<Mainloop::FragmentValues;++v) {
          int const row=Mainloop::warp_m()*Mainloop::WarpTileM+ma*Mainloop::InstructionM+
                        marlin_ppu_detail::output_row<Mainloop::InstructionM>(lane,v);
          int const col=warp_n*(Mainloop::NAtoms*16)+na*16+
                        marlin_ppu_detail::output_col_offset<Mainloop::InstructionM>(lane,v);
          if((!Mainloop::PaddedOutputRows || row<TM) && (!PruneRows || row<StaticM))
            destination[row*(TN+Padding)+col]=Output(acc.tile[ma][na].value[v]);
        }
    }
  }

  template<int Parts = GlobalSlices>
  CUTLASS_DEVICE static void complete_global(
      Params const& p, typename Mainloop::Params const& problem, SharedStorage& shared,
      typename Mainloop::Accumulator const& acc, int tid, int warp_k, int lane,
      int warp_n, int tile_n, int slice, int m_base=0, int boundary_slot=0) {
    if(warp_k==0)
      stage_output<float,GlobalOutputPadding>(shared.tile.fp32_output,acc,lane,warp_n);
    __syncthreads();
    int64_t const stride=StreamKWorkers ? int64_t(StreamKWorkers)*TM*TN
                                       : int64_t(problem.m)*problem.n;
    int64_t const tile_offset=StreamKWorkers ? int64_t(boundary_slot)*TM*TN
                                            : int64_t(tile_n)*TN;
    int const row_stride=StreamKWorkers ? TN : problem.n;
    int const counter_index=StreamKWorkers ? boundary_slot : tile_n;
    constexpr int StoreThreads=FusedStoreWarps ? FusedStoreWarps*32 : MaxThreadsPerBlock;
    if(tid<StoreThreads) {
      #pragma unroll
      for(int i=tid;i<TM*(TN/4);i+=StoreThreads) {
        int const row=i/(TN/4),column=(i%(TN/4))*4;
        if(m_base+row<problem.m) {
          int64_t const offset=int64_t(slice)*stride+tile_offset+int64_t(row)*row_stride+column;
          *reinterpret_cast<float4*>(p.partials+offset)=
              *reinterpret_cast<float4 const*>(
                  shared.tile.fp32_output+row*(TN+GlobalOutputPadding)+column);
        }
      }
    }

    // Reuse the production actual-last publication/acquire protocol. Every
    // writer fences before the fetch-old arrival; no CTA waits for a peer.
    __syncthreads();
    if(tid<StoreThreads) __threadfence();
    __syncthreads();
    if(tid==0) shared.tile.completion.old_count=atomicAdd(p.counters+counter_index,int32_t(1));
    __syncthreads();
    if(!fixed_splitk::completion_arrival_is_last(
          uint32_t(shared.tile.completion.old_count),Parts)) return;
    if(tid==0)
      shared.tile.completion.published_count=
          fixed_splitk::LastArriverM1Fp16Completion<8>::load_acquire(p.counters+counter_index);
    __syncthreads();
    if(shared.tile.completion.published_count!=Parts) return;

    #pragma unroll
    for(int i=tid;i<TM*(TN/8);i+=MaxThreadsPerBlock) {
      int const row=i/(TN/8),column=(i%(TN/8))*8;
      if(m_base+row<problem.m) {
        int64_t const offset=tile_offset+int64_t(row)*row_stride+column;
        Array<float,8> sum;
        sum.clear();
        #pragma unroll
        for(int peer=0;peer<Parts;++peer) {
          #pragma unroll
          for(int j=0;j<8;++j) {
            float value;
            asm volatile("ld.global.cg.f32 %0, [%1];"
                         : "=f"(value)
                         : "l"(p.partials+int64_t(peer)*stride+offset+j) : "memory");
            sum[j]+=value;
          }
        }
        AlignedArray<half_t,8> output;
        #pragma unroll
        for(int j=0;j<8;++j) output[j]=half_t(sum[j]);
        int64_t const output_offset=int64_t(m_base+row)*problem.n+tile_n*TN+column;
        *reinterpret_cast<AlignedArray<half_t,8>*>(p.output+output_offset)=output;
      }
    }
    __syncthreads();
    if(tid==0) atomicExch(p.counters+counter_index,int32_t(0));
  }

  CUTLASS_DEVICE static void run_tile(
      Params const& p,SharedStorage& shared,int task,
      int k_begin=0,int k_count=0,int peer=0,int peers=1,int boundary_slot=0,
      int next_task=-1,bool primed=false) {
    typename Mainloop::ThreadIndex const tid = logical_thread(threadIdx.x);
    int const lane = tid % 32;
    int const warp_k = Mainloop::k_cohort(tid);
    int const output_tid = tid % Mainloop::OutputThreads;
    int const warp_n = output_tid / 32 % Mainloop::WarpN;
    int tile_m = int(blockIdx.x), tile_n = int(blockIdx.y), slice=0;
    if constexpr (StreamKWorkers>0) {
      map_tile(p,task,tile_m,tile_n);
      slice=peer;
    } else if constexpr (PersistentMN) {
      map_tile(p,task,tile_m,tile_n);
    } else if constexpr (GlobalSlices>1) {
      // Query admits one M tile. Interleave K peers rather than padding each
      // peer's grid separately.
      if(task>=p.tile_count*GlobalSlices) return;
      tile_m=0;
      tile_n=task/GlobalSlices;
      slice=task%GlobalSlices;
    } else if constexpr (PadGridTo40) {
      if (int(blockIdx.x) >= p.tile_count) return;
      map_tile(p,int(blockIdx.x),tile_m,tile_n);
    }
    int const m_base = StaticM>0 && StaticM<=TM ? 0 : tile_m*TM;
    int const n_base = tile_n * TN;
    auto problem=p.mainloop;
    if constexpr (StaticM>0) problem.m=StaticM;
    if constexpr (StaticN>0) problem.n=StaticN;
    if constexpr (StaticK>0) problem.k=StaticK;
    typename Mainloop::Accumulator acc;
    if constexpr (StreamKWorkers>0) {
      if constexpr (StreamKMode>0) {
        if(peers==1)
          Mainloop::template run<1,ReductionStorage!=2>(
              problem,shared.tile.mainloop,acc,m_base,n_base,tid,0);
        else
          Mainloop::run_range(problem,shared.tile.mainloop,acc,m_base,n_base,tid,k_begin,k_count);
      } else {
        Mainloop::run_range(problem,shared.tile.mainloop,acc,m_base,n_base,tid,k_begin,k_count);
      }
    } else if constexpr (PersistentPrefetch) {
      typename Mainloop::PipelineContinuation next{0,0,next_task>=0,primed};
      if(next.valid) {
        int next_m,next_n;
        map_tile(p,next_task,next_m,next_n);
        next.m_base=next_m*TM;
        next.n_base=next_n*TN;
      }
      Mainloop::template run_range<false,true>(
          problem,shared.tile.mainloop,acc,m_base,n_base,tid,0,
          problem.k/int(cute::size<2>(TileShape{})),next);
    } else
      Mainloop::template run<GlobalSlices,ReductionStorage!=2>(
          problem,shared.tile.mainloop,acc,m_base,n_base,tid,slice);
    auto* values = reinterpret_cast<float*>(&acc);
    if constexpr (Mainloop::WarpK > 1) {
      if constexpr (ChunkReduction) {
        reduce_chunks(shared,values,warp_k,output_tid);
      } else {
      if (warp_k != 0) {
        #pragma unroll
        for (int i = 0; i < Values; i += 4) {
          if(!output_value_is_live(output_tid,i)) continue;
          int const position = VectorReduction
              ? partial_vector_position(output_tid,i) : output_tid*Values+i;
          *reinterpret_cast<float4*>(&shared.partial[(warp_k - 1) * CohortValues + position]) =
              make_float4(values[i], values[i+1], values[i+2], values[i+3]);
        }
      }
      __syncthreads();
      if (warp_k == 0) {
        if constexpr (InlineReduction) {
          #pragma unroll
          for(int peer=0;peer<Mainloop::WarpK-1;++peer)
            #pragma unroll
            for(int i=0;i<Values;i+=4)
              if(output_value_is_live(output_tid,i))
                add_partial_vector(values+i,
                    &shared.partial[peer*CohortValues+partial_vector_position(output_tid,i)]);
        } else if constexpr (PrefetchReduction) {
          float4 pending[Mainloop::WarpK-1][Values/4];
          #pragma unroll
          for(int peer=0;peer<Mainloop::WarpK-1;++peer)
            #pragma unroll
            for(int i=0;i<Values;i+=4)
              if(output_value_is_live(output_tid,i))
                pending[peer][i/4]=*reinterpret_cast<float4 const*>(
                    &shared.partial[peer*CohortValues+partial_vector_position(output_tid,i)]);
          asm volatile("" ::: "memory");
          #pragma unroll
          for(int peer=0;peer<Mainloop::WarpK-1;++peer)
            #pragma unroll
            for(int i=0;i<Values;i+=4) {
              if(!output_value_is_live(output_tid,i)) continue;
              auto const value=pending[peer][i/4];
              values[i]+=value.x;
              values[i+1]+=value.y;
              values[i+2]+=value.z;
              values[i+3]+=value.w;
            }
        } else if constexpr (BoundedReduction) {
          // Keep one M16 fragment live across the peer loop. Fully unrolling
          // peers and the entire tile makes HGGC retain >128 registers at M64.
          constexpr int Chunk = Mainloop::NAtoms*Mainloop::FragmentValues;
          #pragma unroll
          for (int base=0;base<Values;base+=Chunk) {
            #pragma unroll 1
            for (int peer=0;peer<Mainloop::WarpK-1;++peer) {
              #pragma unroll
              for (int i=base;i<base+Chunk;i+=4) {
                if(!output_value_is_live(output_tid,i)) continue;
                int const position=partial_vector_position(output_tid,i);
                float4 const value=*reinterpret_cast<float4 const*>(
                    &shared.partial[peer*CohortValues+position]);
                values[i]+=value.x;
                values[i+1]+=value.y;
                values[i+2]+=value.z;
                values[i+3]+=value.w;
              }
            }
          }
        } else {
        #pragma unroll
        for (int peer = 0; peer < Mainloop::WarpK - 1; ++peer) {
          if constexpr (VectorReduction) {
            #pragma unroll
            for (int i = 0; i < Values; i += 4) {
              if(!output_value_is_live(output_tid,i)) continue;
              int const position = partial_vector_position(output_tid,i);
              float4 const value = *reinterpret_cast<float4 const*>(
                  &shared.partial[peer*CohortValues+position]);
              values[i] += value.x;
              values[i+1] += value.y;
              values[i+2] += value.z;
              values[i+3] += value.w;
            }
          } else {
            #pragma unroll
            for (int i = 0; i < Values; ++i)
              if(output_value_is_live(output_tid,i))
                values[i] += shared.partial[peer * CohortValues + output_tid * Values + i];
          }
        }
        }
      }
      if constexpr (!DirectOutput && ReductionStorage!=2) __syncthreads();
      }
    }
    if constexpr (StreamKWorkers>0) {
      if(peers>1) {
        complete_global<2>(p,problem,shared,acc,tid,warp_k,lane,warp_n,
                           tile_n,slice,m_base,boundary_slot);
        return;
      }
    }
    if constexpr (GlobalSlices>1) {
      complete_global(p,problem,shared,acc,tid,warp_k,lane,warp_n,tile_n,slice);
      return;
    }
    if constexpr (DirectOutput) {
      if(warp_k==0)
        store_packed_output<(CompactOutput==2)>(p.output+int64_t(m_base)*problem.n+n_base,acc,lane,warp_n,
                            problem.n,problem.m-m_base<TM ? problem.m-m_base : TM);
      return;
    }
    if(warp_k==0) stage_output(shared.tile.output,acc,lane,warp_n);
    __syncthreads();
    using Vector = typename Mainloop::Vector;
    auto* output = reinterpret_cast<Vector*>(p.output);
    auto const* staged = reinterpret_cast<Vector const*>(shared.tile.output);
    #pragma unroll
    for (auto i = tid; i < TM * (TN / 8); i += MaxThreadsPerBlock) {
      int row = i / (TN / 8), chunk = i % (TN / 8);
      if (m_base + row < problem.m)
        output[(m_base + row) * (problem.n / 8) + n_base / 8 + chunk] =
            staged[row * ((TN + 8) / 8) + chunk];
    }
  }

  CUTLASS_DEVICE void operator()(Params const& p, char* smem) {
    auto& shared=*reinterpret_cast<SharedStorage*>(smem);
    if constexpr (StreamKWorkers>0) {
      uint32_t const worker=blockIdx.x;
      int const tile_base=StreamKMode>=2 ? p.tile_count-int(p.streamk.tiles) : 0;
      // Mode 3 runs this prefix in a separate ordinary whole-K kernel.
      if constexpr (StreamKMode==2) {
        #pragma unroll 1
        for(int task=int(worker);task<tile_base;task+=StreamKWorkers) {
          run_tile(p,shared,task);
          __syncthreads();
        }
      }
      uint32_t cursor=p.streamk.begin(worker);
      uint32_t const end=p.streamk.begin(worker+1);
      #pragma unroll 1
      while(cursor<end) {
        auto const work=p.streamk.next(worker,cursor);
        run_tile(p,shared,tile_base+int(work.tile),int(work.k_begin),int(work.k_count),
                 int(work.peer),int(work.peers),int(work.slot));
        __syncthreads();
        cursor+=work.k_count;
      }
    } else if constexpr (PersistentMN) {
      #pragma unroll 1
      for(int task=int(blockIdx.x);task<p.tile_count;task+=int(gridDim.x)) {
        if constexpr (PersistentPrefetch) {
          int const successor=task+int(gridDim.x);
          run_tile(p,shared,task,0,0,0,1,0,
                   successor<p.tile_count ? successor : -1,task!=int(blockIdx.x));
        } else {
          run_tile(p,shared,task);
        }
        // Global C stores have consumed the staged output before the next
        // tile's mainloop reuses the same shared storage.
        __syncthreads();
      }
    } else {
      run_tile(p,shared,int(blockIdx.x));
    }
  }
};

}  // namespace cutlass::gemm::kernel
