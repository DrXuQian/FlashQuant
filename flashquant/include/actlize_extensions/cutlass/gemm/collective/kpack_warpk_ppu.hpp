// Copyright (c) 2026, quactlize contributors.
// SPDX-License-Identifier: BSD-3-Clause
#pragma once

#include "cutlass/numeric_types.h"
#include "cutlass/arch/barrier.h"
#include "cute/tensor.hpp"
#include "cute/atom/mma_traits_ppu0010.hpp"
#include "q4_kpack4_offline.hpp"
#include "marlin_format_ppu.hpp"
#include "actlize_extensions/cutlass/gemm/collective/marlin_mma_ppu.hpp"
#include "actlize_extensions/cutlass/gemm/kernel/kpack_streamk_schedule.hpp"

namespace cutlass::gemm::collective {

template<bool Enabled,int Vectors>
struct KPackExpandedBStoragePPU {};

template<int Vectors>
struct KPackExpandedBStoragePPU<true,Vectors> {
  alignas(128) marlin_ppu_detail::Vector128 expanded_b[Vectors];
};

template<bool Enabled,int Stages,int Vectors>
struct KPackIntegerZeroStoragePPU {};

template<int Stages,int Vectors>
struct KPackIntegerZeroStoragePPU<true,Stages,Vectors> {
  alignas(128) marlin_ppu_detail::Vector128 zeros[Stages][Vectors];
};

template<int TM, int TN, int TK, int WN, int WK, int Stages,
         bool NativeA = false, bool ClassicWeights = false, bool NativeB = false,
         bool ChunkA = false, bool StageCycles = false, int MmaM8 = 0,
         bool RegisterPrefetch = false, bool PairedScales = false,
         bool FullRegisterPipeline = false, int MmaRows = 16,
         int WM = TM, bool UnrollCycles = false,
         int CompilerFence = 0, bool OpaqueCoordinates = false,
         bool SharedB = false, bool UnsignedIndices = false,
         bool InterleaveA = false, bool TailM8 = false, bool CacheScales = false,
         bool SkipStage2Barrier = false, int DirectA = 0, int CohortPipeline = 0,
         int BProducerWarp = 0, bool IntegerZero = false, bool ZeroWordLoad = false,
         bool SingleZeroBias = false, bool InterleaveZeroGroups = false,
         bool PairedZeroBias = false, bool CacheZeroBias = false,
         bool PermuteZeroBias = false, bool PreparedZeroBias = false,
         bool ByteZeroWords = false>
struct NativeInt4WarpKCollectivePPU {
  using TileShape = cute::Shape<cute::Int<TM>, cute::Int<TN>, cute::Int<TK>>;
  using ElementA = cutlass::half_t;
  using ElementB = cutlass::int4b_t;
  using ElementScale = cutlass::half_t;
  using ElementAccumulator = float;
  using Vector = marlin_ppu_detail::Vector128;
  using FragmentA = marlin_ppu_detail::FragmentA;
  using FragmentC = marlin_ppu_detail::FragmentCFor<MmaRows>;
  using ThreadIndex=std::conditional_t<UnsignedIndices,uint32_t,int>;
  static constexpr int InstructionM=MmaRows;
  static constexpr int FragmentValues=sizeof(FragmentC)/sizeof(float);
  static constexpr int AStorageM=TM>128 ? ((TM+127)/128)*128 : ((TM+15)/16)*16;
  static constexpr int ACubeM=AStorageM<128 ? AStorageM : 128;
  static constexpr int ACubes=AStorageM/ACubeM;
  static constexpr int BStorageN=NativeB && !ClassicWeights ? ((TN+63)/64)*64 : TN;
  static constexpr int PipelineCohorts=CohortPipeline>=3 ? 2 : 1;
  static constexpr int PipelineK=WK*PipelineCohorts;
  static constexpr int BCubeK=CohortPipeline ? PipelineK : (TK<512 ? TK : 512);
  static constexpr int BKCubes=(TK+BCubeK-1)/BCubeK;
  static constexpr int WarpTileM=WM;
  static constexpr int WarpM=TM/WM;
  static constexpr int WarpN = TN / WN;
  static constexpr int WarpK = TK / WK;
  static constexpr int Threads = 32 * WarpM * WarpN * WarpK;
  static constexpr int OutputThreads = 32 * WarpM * WarpN;
  static constexpr int PipelineThreads=OutputThreads*PipelineCohorts;
  static constexpr int MAtoms = (WM+InstructionM-1)/InstructionM;
  static constexpr bool PaddedOutputRows=WM%InstructionM!=0;
  static constexpr int NAtoms = WN / 16;
  static constexpr int AStride = TK / 8;
  static constexpr int AVectors = DirectA>=3 ? 1 : AStorageM*AStride;
  static constexpr int BStride = TN + 8;
  static constexpr int BVectors = NativeB && !ClassicWeights
      ? BKCubes*BCubeK*BStorageN/32
      : ClassicWeights ? TK*BStorageN/32 : (TK/4)*BStride/8;
  static constexpr int MetadataColumnsPerVector = PreparedZeroBias ? 4 : 8;
  static constexpr int SVectors = (TK / 32) * TN / MetadataColumnsPerVector;
  static constexpr int BThreads=32*WarpN*WarpK;
  static constexpr int ExpandedBVectors=(WK/16)*NAtoms*BThreads;
  static constexpr uint64_t MappingId = ClassicWeights
      ? 0x5741344d4c000001ull : q4_kpack4::kMappingId;
  static_assert((InstructionM==8 || InstructionM==16) && TM % WM == 0);
  static_assert(WM%InstructionM==0 || (TailM8 && InstructionM==16 && WM%16==8));
  static_assert(!TailM8 || (InstructionM==16 && WM%16==8 && WarpM==1 && MmaM8==0),
                "the mixed M8 tail currently admits one M warp cohort");
  static_assert(TN % WN == 0 && WN % 16 == 0);
  static_assert(TK % WK == 0 && WK % 32 == 0);
  static_assert(TK>=64 && TK%64==0);
  static_assert((TK & (TK-1))==0 || (NativeA && NativeB && !ClassicWeights),
                "non-power-of-two K tiles require the opaque native readers");
  static_assert(Threads >= 64 && Threads <= 1024 && Stages >= 1 && Stages <= 4);
  static_assert(Stages>1 || (NativeA && NativeB && !ClassicWeights && !FullRegisterPipeline),
                "one-stage tiles use the synchronous native K-pack pipeline");
  static_assert(NAtoms <= 8);
  static_assert(!NativeB || (BStorageN % 64 == 0 && BCubeK / 4 <= 128));
  static_assert(MmaM8>=0 && MmaM8<=2);
  static_assert(CompilerFence>=0 && CompilerFence<=2);
  static_assert(!CompilerFence || (!FullRegisterPipeline && !RegisterPrefetch));
  static_assert(CompilerFence!=1 || ChunkA);
  static_assert(!SharedB || (!FullRegisterPipeline && !RegisterPrefetch && !CompilerFence),
                "shared B uses the staged collective pipeline");
  static_assert(!InterleaveA || FullRegisterPipeline,
                "interleaved A refill requires the register pipeline");
  static_assert(!SkipStage2Barrier || (FullRegisterPipeline && Stages==2));
  static_assert(DirectA>=0 && DirectA<=4);
  static_assert(!DirectA || (!FullRegisterPipeline && !SharedB),
                "direct A currently uses the staged collective");
  static_assert(CohortPipeline>=0 && CohortPipeline<=4);
  static_assert(!CohortPipeline ||
      (NativeA && NativeB && !ClassicWeights && WarpM==1 && WK%64==0 &&
       PipelineK<=512 && WarpK%PipelineCohorts==0 &&
       Stages>1 && !FullRegisterPipeline && !SharedB && !DirectA),
      "cohort pipelines require disjoint whole native A/B cubes and one M cohort");
  static_assert(!CohortPipeline ||
      WarpK/PipelineCohorts+cutlass::arch::NamedBarrier::ReservedNamedBarrierCount<=
            cutlass::arch::NamedBarrier::HardwareMaxNumNamedBarriers);
  static_assert(BProducerWarp>=0 && BProducerWarp<Threads/32);
  static_assert(!BProducerWarp || (NativeB && !ClassicWeights && !CohortPipeline),
                "B producer rotation currently uses the full native stage");
  static_assert(!IntegerZero || (PairedScales && NativeB && !ClassicWeights && TN%32==0),
                "integer-zero metadata currently uses native K-pack and whole N32 copy vectors");
  static_assert(!ZeroWordLoad || IntegerZero);
  static_assert(!SingleZeroBias || IntegerZero);
  static_assert(!PairedZeroBias || (IntegerZero && SingleZeroBias));
  static_assert(!CacheZeroBias || (IntegerZero && SingleZeroBias));
  static_assert(!PreparedZeroBias || (IntegerZero && PairedScales && !InterleaveZeroGroups),
                "prepared zero biases use row-major paired scale/bias records");
  static_assert(!ByteZeroWords || (IntegerZero && PairedScales && !PreparedZeroBias),
                "byte zero words and merged scale/bias records are distinct encodings");
  static constexpr int ZeroGroupInterleave=ByteZeroWords ? 2 :
      (InterleaveZeroGroups ? (TK%128==0 ? 4 : 2) : 1);
  static constexpr int ZeroColumnsPerVector=ByteZeroWords ? 16 : 32;
  static_assert(!PermuteZeroBias || (IntegerZero && ZeroWordLoad && ZeroGroupInterleave==4),
                "byte-permuted biases require quartet-word integer-zero metadata");
  static_assert(!InterleaveZeroGroups || (IntegerZero && TK%64==0),
                "zero interleaving copies complete group32 pairs or quartets");

  struct BaseParams {
    int m, n, k;
    half_t const* a;
    uint16_t const* b;
    half_t const* scales;
  };
  struct IntegerZeroParams : BaseParams { uint8_t const* zeros; };
  using Params=std::conditional_t<IntegerZero,IntegerZeroParams,BaseParams>;
  CUTLASS_HOST_DEVICE static Params make_params(
      int m,int n,int k,half_t const* a,uint16_t const* b,half_t const* scales) {
    if constexpr (IntegerZero) return {{m,n,k,a,b,scales},nullptr};
    else return {m,n,k,a,b,scales};
  }
  struct Accumulator { FragmentC tile[MAtoms][NAtoms]; };
  CUTLASS_DEVICE static int warp_m() {
    return ThreadIndex(threadIdx.x)/32/WarpN%WarpM;
  }
  CUTLASS_DEVICE static int k_cohort(ThreadIndex tid) {
    if constexpr (UnsignedIndices && WarpK==1) return 0;
    return tid/OutputThreads;
  }
  using RawB = uint32_t[(WK+63)/64][NAtoms][4];
  using FragmentB = decltype(marlin_ppu_detail::dequantize_biased_int4(uint32_t{}));
  struct BPair { FragmentB b0,b1; };
  struct PlainGroupMetadata { __half2 s0,s1; };
  struct CachedGroupMetadata { __half2 s0,s1; uint32_t zero0,zero1; };
  using ScalePair=cute::conditional_t<CacheZeroBias,CachedGroupMetadata,PlainGroupMetadata>;
  static_assert(sizeof(BPair)==sizeof(Vector));
  static_assert(ExpandedBVectors*sizeof(Vector)==TK*TN*sizeof(half_t));
  struct SharedStorage : KPackExpandedBStoragePPU<SharedB,ExpandedBVectors>,
                         KPackIntegerZeroStoragePPU<IntegerZero && !PreparedZeroBias,Stages,
                                                    (TK/32)*TN/ZeroColumnsPerVector> {
    alignas(128) Vector a[Stages][AVectors];
    alignas(128) Vector b[Stages][BVectors];
    alignas(128) Vector scales[Stages][SVectors];
  };

  CUTLASS_HOST_DEVICE static constexpr int a_index(int row, int chunk, int base = 0) {
    (void)base;
    return row * AStride + (chunk ^ (row & (AStride - 1)));
  }

  template<int CubeRows>
  CUTLASS_DEVICE static void copy_swizzled(
      void* destination, void const* source, int rows, int columns,
      int row, int column) {
    uint32_t const address = uint32_t(__cvta_generic_to_shared(destination));
    asm volatile(
        "ppu.cp.async.aiu.bulk.tensor.shared.global.padz.swzl.2d.b16 "
        "[%0], [%1], {1,%2,%3,0,%4,%5}, {1,%6,64,1};"
        :: "r"(address), "l"(source), "r"(rows), "r"(columns),
           "r"(row), "r"(column), "r"(CubeRows) : "memory");
  }

  CUTLASS_DEVICE static void copy_native_a(
      void* destination, void const* source, int rows, int columns,
      int row, int column) {
    copy_swizzled<ACubeM>(destination,source,rows,columns,row,column);
  }

  CUTLASS_DEVICE static void copy_linear_b(
      void* destination, void const* source, int rows, int columns,
      int row, int column) {
    uint32_t const address = uint32_t(__cvta_generic_to_shared(destination));
    asm volatile(
        "ppu.cp.async.aiu.bulk.tensor.shared.global.padz.linear.stride.2d.b32 "
        "[%0], [%1], {1,%2,%3,0,%4,%5}, {1,%6,%7,1};"
        :: "r"(address), "l"(source), "r"(rows), "r"(columns),
           "r"(row), "r"(column), "r"(TK/16), "r"(TN*2) : "memory");
  }

  CUTLASS_DEVICE static void load_native_b(
      uint32_t (&words)[4], void const* cube, int row, int channel_bytes) {
    uint32_t const address = uint32_t(__cvta_generic_to_shared(cube));
    if constexpr (OpaqueCoordinates)
      asm volatile("" : "+r"(row), "+r"(channel_bytes));
    asm volatile(
        "ppu.ldmatrix.sync.aligned.m16n16.x1.swzl.trans.shared.b16 "
        "{%0,%1,%2,%3}, [%4], {0,%5,1,%6,1,%7};"
        : "=r"(words[0]), "=r"(words[1]), "=r"(words[2]), "=r"(words[3])
        : "r"(address), "r"(row), "r"(BCubeK/4), "r"(channel_bytes));
  }

  CUTLASS_DEVICE static void load_swizzled_a(
      FragmentA& result, void const* cube, int row, int channel_bytes) {
    // Paired with the opaque AIU swzl writer, not a software XOR layout.
    auto* words = reinterpret_cast<uint32_t*>(&result);
    uint32_t const address = uint32_t(__cvta_generic_to_shared(cube));
    if constexpr (OpaqueCoordinates)
      asm volatile("" : "+r"(row), "+r"(channel_bytes));
    asm volatile(
        "ppu.ldmatrix.sync.aligned.m8n8.x4.swzl.shared.b16 "
        "{%0,%1,%2,%3}, [%4], {0,%5,1,%6,1,%7};"
        : "=r"(words[0]), "=r"(words[1]), "=r"(words[2]), "=r"(words[3])
        : "r"(address), "r"(row), "r"(ACubeM), "r"(channel_bytes));
  }

  CUTLASS_DEVICE static void copy_stage(
      Params const& p, SharedStorage& shared, int stage, int tile,
      int m_base, int n_base, ThreadIndex tid) {
    if (tile < p.k / TK) {
      auto const* a = reinterpret_cast<Vector const*>(p.a);
      auto const* b = reinterpret_cast<Vector const*>(p.b);
      auto const* scales = reinterpret_cast<Vector const*>(p.scales);
      constexpr int CopyK=CohortPipeline ? PipelineK : TK;
      static_assert(!(InterleaveZeroGroups || ByteZeroWords) ||
                    CopyK%(32*ZeroGroupInterleave)==0,
                    "a copy cohort must contain whole interleaved zero groups");
      constexpr int CopyThreads=CohortPipeline ? PipelineThreads : Threads;
      constexpr int CopyBCubes=CohortPipeline ? 1 : BKCubes;
      constexpr int CopySVectors=(CopyK/32)*TN/MetadataColumnsPerVector;
      auto const copy_tid=CohortPipeline ? tid%PipelineThreads : tid;
      ThreadIndex const copy_group=CohortPipeline ? tid/PipelineThreads : 0;
      if constexpr (DirectA<2) {
      if constexpr (NativeA) {
        // Each physical warp issues distinct 64-wide opaque A cubes. All
        // threads still commit/wait, preserving the stage-ring cadence.
        #pragma unroll
        for (auto slab=copy_tid/32;slab<(CopyK/64)*ACubes;slab+=CopyThreads/32) {
          auto const cube=copy_group*(CopyK/64)*ACubes+slab;
          copy_native_a(&shared.a[stage][cube*ACubeM*8],p.a,p.m,p.k,
                        m_base+(cube%ACubes)*ACubeM,tile*TK+(cube/ACubes)*64);
        }
      } else {
        #pragma unroll
        for (auto i = tid; i < AVectors; i += Threads) {
          int row = i / AStride, chunk = i % AStride;
          if (m_base + row < p.m) {
            marlin_ppu_detail::cp_async_16(
                &shared.a[stage][a_index(row, chunk)],
                &a[(m_base + row) * (p.k / 8) + tile * AStride + chunk]);
          } else {
            shared.a[stage][a_index(row, chunk)] = Vector{0,0,0,0};
          }
        }
      }
      }
      if constexpr (NativeB) {
        if constexpr (ClassicWeights) {
          if (tid / 32 == 0)
            copy_linear_b(shared.b[stage],p.b,p.k/16,p.n*2,tile*(TK/16),n_base*2);
        } else {
          auto const b_warp=BProducerWarp
              ? (copy_tid/32+CopyThreads/32-BProducerWarp)%(CopyThreads/32) : copy_tid/32;
          #pragma unroll
          for (auto slab=b_warp;slab<(BStorageN/64)*CopyBCubes;slab+=CopyThreads/32) {
            auto const nc=BStorageN==64 ? 0 : slab/CopyBCubes;
            auto const kc=(BStorageN==64 ? slab : slab%CopyBCubes)+copy_group*CopyBCubes;
            auto const cube=CohortPipeline ? nc*BKCubes+kc : slab;
            copy_swizzled<BCubeK/4>(
                &shared.b[stage][cube*(BCubeK/4)*8],p.b,p.k/4,p.n,
                tile*(TK/4)+kc*(BCubeK/4),n_base+nc*64);
          }
        }
      } else {
        constexpr int BSourceVectors = (TK / 4) * (TN / 8);
        #pragma unroll
        for (auto i = tid; i < BSourceVectors; i += Threads) {
          if constexpr (ClassicWeights) {
            int ktile = i / (TN / 2), inner = i % (TN / 2);
            marlin_ppu_detail::cp_async_16(
                &shared.b[stage][i],
                &b[(tile * (TK / 16) + ktile) * (p.n / 2) + n_base / 2 + inner]);
          } else {
            int row = i / (TN / 8), chunk = i % (TN / 8);
            marlin_ppu_detail::cp_async_16(
                &shared.b[stage][row * (BStride / 8) + chunk],
                &b[(tile * (TK / 4) + row) * (p.n / 8) + n_base / 8 + chunk]);
          }
        }
      }
      #pragma unroll
      for (auto local=copy_tid;local<CopySVectors;local+=CopyThreads) {
        auto const i=copy_group*CopySVectors+local;
        int group = i / (TN / MetadataColumnsPerVector);
        int chunk = i % (TN / MetadataColumnsPerVector);
        marlin_ppu_detail::cp_async_16(
            &shared.scales[stage][i],
            &scales[(tile * (TK / 32) + group) * (p.n / MetadataColumnsPerVector) +
                    n_base / MetadataColumnsPerVector + chunk]);
      }
      if constexpr (IntegerZero && !PreparedZeroBias) {
        constexpr int CopyZVectors=(CopyK/32)*TN/ZeroColumnsPerVector;
        constexpr int GroupsPerWord=ZeroGroupInterleave;
        constexpr int ColumnsPerVector=ZeroColumnsPerVector/GroupsPerWord;
        auto const* zeros=reinterpret_cast<Vector const*>(p.zeros);
        #pragma unroll
        for(auto local=copy_tid;local<CopyZVectors;local+=CopyThreads) {
          auto const i=copy_group*CopyZVectors+local;
          int const group=i/(TN/ColumnsPerVector),chunk=i%(TN/ColumnsPerVector);
          marlin_ppu_detail::cp_async_16(
              &shared.zeros[stage][i],
              &zeros[(tile*(TK/(32*GroupsPerWord))+group)*(p.n/ColumnsPerVector)+
                     n_base/ColumnsPerVector+chunk]);
        }
      }
    }
    marlin_ppu_detail::cp_async_commit();
  }

  using DirectAMma=cute::MMA_Traits<cute::PPU0010_16x16x16_F32F16F16F32_TN>;
  using DirectALayout=typename DirectAMma::ALayout;
  static constexpr int DirectAtomM=int(cute::size<0>(typename DirectAMma::Shape_MNK{}));
  static constexpr bool direct_a_pairs_are_contiguous() {
    for(int lane=0;lane<int(cute::size<0>(DirectALayout{}));++lane)
      for(int value=0;value<int(cute::size<1>(DirectALayout{}));value+=2) {
        int const first=DirectALayout{}(cute::make_coord(lane,value));
        int const second=DirectALayout{}(cute::make_coord(lane,value+1));
        if(first%DirectAtomM!=second%DirectAtomM ||
           first/DirectAtomM+1!=second/DirectAtomM) return false;
      }
    return true;
  }

  CUTLASS_DEVICE static void load_a_fragment(
      FragmentA& a, SharedStorage& shared, int stage, int group, int part, int ma, int lane,
      Params const* problem=nullptr,int m_base=0,int tile=0) {
    int const fragment_row=warp_m()*WM+ma*InstructionM;
    int const m16_row=(fragment_row/16)*16;
    if constexpr (DirectA) {
      static_assert(direct_a_pairs_are_contiguous());
      auto* words=reinterpret_cast<uint32_t*>(&a);
      auto const* source=reinterpret_cast<uint32_t const*>(problem->a);
      #pragma unroll
      for(int reg=0;reg<int(sizeof(FragmentA)/sizeof(uint32_t));++reg) {
        int const coordinate=DirectALayout{}(cute::make_coord(lane,reg*2));
        int const row=m_base+m16_row+coordinate%DirectAtomM;
        int const column=tile*TK+group*32+part*16+coordinate/DirectAtomM;
        auto const* address=source+(int64_t(row)*problem->k+column)/2;
        if constexpr (DirectA==4)
          words[reg]=row<problem->m ? __ldg(address) : 0;
        else
          words[reg]=row<problem->m ? *address : 0;
      }
    } else if constexpr (NativeA) {
      int const kk=group*32+part*16;
      auto* cube=&shared.a[stage][((kk/64)*ACubes+m16_row/ACubeM)*ACubeM*8];
      load_swizzled_a(a,cube,m16_row%ACubeM,(kk%64)*2);
    } else {
      int row=m16_row+lane%16,chunk=group*4+part*2+lane/16;
      marlin_ppu_detail::ldmatrix_a_m16(a,&shared.a[stage][a_index(row,chunk)]);
    }
    if constexpr (InstructionM==8) {
      // R18 established the actual native swzl A partition on device.
      if((fragment_row/8)%2) {
        a.value[0]=a.value[2];
        a.value[1]=a.value[3];
      }
    }
  }

  CUTLASS_DEVICE static BPair load_b_fragment(
      SharedStorage const& shared, RawB const& native_b, int stage,
      int group, int kg, int part, int warp_n, int lane, int na,ScalePair& cached) {
    int const column=warp_n*WN+na*16+lane/4;
    uint32_t q0,q1;
    if constexpr (ClassicWeights) {
      int const nb=warp_n*NAtoms+na;
      int const vector=(group*2+part)*(TN/2)+(nb/4)*32+lane;
      uint32_t const packed=reinterpret_cast<uint32_t const*>(&shared.b[stage][vector])[nb%4];
      q0=packed;
      q1=packed>>8;
    } else if constexpr (NativeB) {
      auto const& raw=native_b[kg/2][na];
      q0=(group%2 ? raw[1] : raw[0])>>(part*8);
      q1=(group%2 ? raw[3] : raw[2])>>(part*8);
    } else {
      auto const* b=reinterpret_cast<uint16_t const*>(shared.b[stage]);
      int const row=group*8+2*(lane%4);
      uint32_t lo0=b[row*BStride+column]>>(part*8);
      uint32_t hi0=b[(row+1)*BStride+column]>>(part*8);
      uint32_t lo1=b[row*BStride+column+8]>>(part*8);
      uint32_t hi1=b[(row+1)*BStride+column+8]>>(part*8);
      q0=(lo0&255)|((hi0&255)<<16);
      q1=(lo1&255)|((hi1&255)<<16);
    }
    auto const* scales=reinterpret_cast<__half const*>(shared.scales[stage]);
    BPair result;
    uint32_t prepared_scale=0;
    if constexpr (PreparedZeroBias) {
      uint2 metadata={0,0};
      if(!CacheScales || !CacheZeroBias || part==0) {
        int const pair=group*(TN/2)+(warp_n*WN+na*16)/2+lane/4;
        metadata=reinterpret_cast<uint2 const*>(shared.scales[stage])[pair];
        prepared_scale=metadata.x;
      }
      uint32_t bias0,bias1;
      if constexpr (CacheZeroBias) {
        if(part==0) {
          asm volatile("prmt.b32 %0,%1,%1,0x1010;" : "=r"(cached.zero0) : "r"(metadata.y));
          asm volatile("prmt.b32 %0,%1,%1,0x3232;" : "=r"(cached.zero1) : "r"(metadata.y));
        }
        bias0=cached.zero0;
        bias1=cached.zero1;
      } else {
        asm volatile("prmt.b32 %0,%1,%1,0x1010;" : "=r"(bias0) : "r"(metadata.y));
        asm volatile("prmt.b32 %0,%1,%1,0x3232;" : "=r"(bias1) : "r"(metadata.y));
      }
      result.b0=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q0,bias0);
      result.b1=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q1,bias1);
    } else if constexpr (ByteZeroWords) {
      uint32_t bias0,bias1;
      if(!CacheZeroBias || part==0) {
        uint32_t const word_index=(uint32_t(group)/2)*(TN/2)+
            uint32_t(warp_n*WN+na*16)/2+uint32_t(lane)/4;
        uint32_t const word=reinterpret_cast<uint32_t const*>(shared.zeros[stage])[word_index];
        uint32_t const selector0=0x4040u|((uint32_t(group)&1u)*0x202u);
        uint32_t const selector1=selector0|0x101u;
        asm volatile("prmt.b32 %0,%1,0x64,%2;" : "=r"(bias0) : "r"(word),"r"(selector0));
        asm volatile("prmt.b32 %0,%1,0x64,%2;" : "=r"(bias1) : "r"(word),"r"(selector1));
        if constexpr (CacheZeroBias) {
          cached.zero0=bias0;
          cached.zero1=bias1;
        }
      }
      if constexpr (CacheZeroBias) {
        bias0=cached.zero0;
        bias1=cached.zero1;
      }
      result.b0=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q0,bias0);
      result.b1=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q1,bias1);
    } else if constexpr (IntegerZero && PermuteZeroBias) {
      uint32_t word,selector;
      if constexpr (WK>=128) {
        // Retain the validated WK128 lowering; its base group is a quartet.
        int const word_index=(group/4)*(TN/2)+(warp_n*WN+na*16)/2+lane/4;
        word=reinterpret_cast<uint32_t const*>(shared.zeros[stage])[word_index];
        selector=0x4040u|((group%4)*0x101u);
      } else {
        uint32_t const meta_group=uint32_t(group),local_group=uint32_t(kg);
        uint32_t const word_index=(meta_group/4)*(TN/2)+
            uint32_t(warp_n*WN+na*16)/2+uint32_t(lane)/4;
        word=reinterpret_cast<uint32_t const*>(shared.zeros[stage])[word_index]>>
            (8*((meta_group-local_group)%4));
        selector=0x4040u|((local_group%4)*0x101u);
      }
      // Keep the four groups together while masking each column's nibbles.
      // Select the same byte into both halfwords, with the FP16 1024 exponent.
      uint32_t const low=word&0x0f0f0f0fu,high=(word>>4)&0x0f0f0f0fu;
      uint32_t bias0,bias1;
      asm volatile("prmt.b32 %0,%1,0x64,%2;"
          : "=r"(bias0) : "r"(low),"r"(selector));
      asm volatile("prmt.b32 %0,%1,0x64,%2;"
          : "=r"(bias1) : "r"(high),"r"(selector));
      result.b0=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q0,bias0);
      result.b1=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q1,bias1);
    } else if constexpr (IntegerZero) {
      uint32_t packed;
      if(!CacheZeroBias || part==0) {
      int const pair_index=(group*TN+warp_n*WN+na*16+2*(lane/4))/2;
      int const zero_index=InterleaveZeroGroups
          ? (group/ZeroGroupInterleave)*(TN*ZeroGroupInterleave/2)+
            (warp_n*WN+na*16+2*(lane/4))*(ZeroGroupInterleave/2)+group%ZeroGroupInterleave
          : pair_index;
      if constexpr (ZeroWordLoad) {
        if constexpr (ZeroGroupInterleave==4) {
          // Address the word directly: dividing a signed byte expression
          // after adding group%4 prevented reuse between its four consumers.
          int const word_index=(group/4)*(TN/2)+(warp_n*WN+na*16)/2+lane/4;
          uint32_t const word=reinterpret_cast<uint32_t const*>(shared.zeros[stage])[word_index];
          packed=(word>>(8*(group%4)))&255;
        } else {
          uint32_t const word=reinterpret_cast<uint32_t const*>(shared.zeros[stage])[zero_index/4];
          packed=(word>>(8*(zero_index%4)))&255;
        }
      } else {
        packed=reinterpret_cast<uint8_t const*>(shared.zeros[stage])[zero_index];
      }
      if constexpr (CacheZeroBias) {
        if constexpr (PairedZeroBias) {
          uint32_t const repeated=packed*0x10001u;
          cached.zero0=marlin_ppu_detail::lop3<(0xf0&0xcc)|0xaa>(
              repeated,0x000f000f,0x64006400);
          cached.zero1=marlin_ppu_detail::lop3<(0xf0&0xcc)|0xaa>(
              repeated>>4,0x000f000f,0x64006400);
        } else {
          cached.zero0=0x64006400u|((packed&15)*0x10001u);
          cached.zero1=0x64006400u|((packed>>4)*0x10001u);
        }
      }
      }
      if constexpr (CacheZeroBias) {
        // As with the scale cache, part0 initializes each group32 entry
        // before its second K16 consumer. No metadata format change.
        result.b0=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q0,cached.zero0);
        result.b1=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q1,cached.zero1);
      } else if constexpr (PairedZeroBias) {
        // Replicate both nibbles together, then select each column's bias.
        // This retains integer subtraction before FP16 scale multiplication.
        uint32_t const repeated=packed*0x10001u;
        uint32_t const bias0=marlin_ppu_detail::lop3<(0xf0&0xcc)|0xaa>(
            repeated,0x000f000f,0x64006400);
        uint32_t const bias1=marlin_ppu_detail::lop3<(0xf0&0xcc)|0xaa>(
            repeated>>4,0x000f000f,0x64006400);
        result.b0=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q0,bias0);
        result.b1=marlin_ppu_detail::dequantize_integer_zero_int4<true,true>(q1,bias1);
      } else {
        result.b0=marlin_ppu_detail::dequantize_integer_zero_int4<SingleZeroBias>(q0,packed&15);
        result.b1=marlin_ppu_detail::dequantize_integer_zero_int4<SingleZeroBias>(q1,packed>>4);
      }
    } else {
      result={marlin_ppu_detail::dequantize_biased_int4(q0),
              marlin_ppu_detail::dequantize_biased_int4(q1)};
    }
    // Group32 has exactly two K16 consumers. Every caller starts at part0
    // and retains one cache entry per N atom until part1 has consumed it.
    if(!CacheScales || part==0) {
      if constexpr (PreparedZeroBias) {
        __half2 const pair=*reinterpret_cast<__half2 const*>(&prepared_scale);
        cached.s0=__low2half2(pair);
        cached.s1=__high2half2(pair);
      } else if constexpr (PairedScales) {
        int const index=group*TN+warp_n*WN+na*16+2*(lane/4);
        __half2 const pair=*reinterpret_cast<__half2 const*>(scales+index);
        cached.s0=__low2half2(pair);
        cached.s1=__high2half2(pair);
      } else {
        cached.s0=__half2half2(scales[group*TN+column]);
        cached.s1=__half2half2(scales[group*TN+column+8]);
      }
    }
    result.b0.value[0]=__hmul2(result.b0.value[0],cached.s0);
    result.b0.value[1]=__hmul2(result.b0.value[1],cached.s0);
    result.b1.value[0]=__hmul2(result.b1.value[0],cached.s1);
    result.b1.value[1]=__hmul2(result.b1.value[1],cached.s1);
    return result;
  }

  CUTLASS_DEVICE static void mma_fragment(
      FragmentA const& a, FragmentB const& b0, FragmentB const& b1, FragmentC& c,int ma) {
    if constexpr (TailM8) {
      if(ma+1==MAtoms) {
        marlin_ppu_detail::FragmentAFor<8> a8;
        a8.value[0]=a.value[0];
        a8.value[1]=a.value[1];
        marlin_ppu_detail::FragmentCFor<8> c8;
        #pragma unroll
        for(int i=0;i<4;++i) c8.value[i]=c.value[i];
        marlin_ppu_detail::mma_n16<8,0>(a8,b0,b1,c8);
        #pragma unroll
        for(int i=0;i<4;++i) c.value[i]=c8.value[i];
        return;
      }
    }
    if constexpr (InstructionM==8) {
      marlin_ppu_detail::FragmentAFor<8> a8;
      a8.value[0]=a.value[0];
      a8.value[1]=a.value[1];
      marlin_ppu_detail::mma_n16<8,0>(a8,b0,b1,c);
    } else if constexpr (MmaM8) {
      // Two explicit A-register partitions are separate numeric probes until
      // full-output device validation establishes the swzl -> m8 mapping.
      constexpr int second=MmaM8==1 ? 1 : 2;
      marlin_ppu_detail::FragmentAFor<8> a0,a1;
      a0.value[0]=a.value[0];
      a0.value[1]=a.value[second];
      a1.value[0]=a.value[3-second];
      a1.value[1]=a.value[3];
      marlin_ppu_detail::FragmentCFor<8> c0,c1;
      #pragma unroll
      for(int i=0;i<4;++i) {
        c0.value[i]=c.value[i];
        c1.value[i]=c.value[i+4];
      }
      marlin_ppu_detail::mma_n16<8,0>(a0,b0,b1,c0);
      marlin_ppu_detail::mma_n16<8,0>(a1,b0,b1,c1);
      #pragma unroll
      for(int i=0;i<4;++i) {
        c.value[i]=c0.value[i];
        c.value[i+4]=c1.value[i];
      }
    } else {
      marlin_ppu_detail::mma_n16<16,0>(a,b0,b1,c);
    }
  }

  CUTLASS_DEVICE static void load_native_stage(
      RawB& native_b,SharedStorage& shared,int stage,int warp_n,int warp_k) {
      if constexpr (NativeB && !ClassicWeights) {
        #pragma unroll
        for (int chunk=0; chunk<(WK+63)/64; ++chunk)
          #pragma unroll
          for (int na=0; na<NAtoms; ++na) {
            int const column=warp_n*WN+na*16;
            int const kk=((warp_k*WK)/64+chunk)*64;
            auto* cube=&shared.b[stage][((column/64)*BKCubes+kk/BCubeK)*(BCubeK/4)*8];
            load_native_b(native_b[chunk][na],cube,(kk%BCubeK)/4,(column%64)*2);
          }
      }
  }

  CUTLASS_DEVICE static void consume_shared_b(
      SharedStorage& shared,Accumulator& acc,int stage,int lane,int warp_n,int warp_k) {
    int const b_tid=(warp_k*WarpN+warp_n)*32+lane;
    // Cache the existing reader's exact opaque fragment. Every M warp has
    // identical N/K/lane ownership; no reconstructed weight-coordinate map
    // is involved. Distinct (step, na, b_tid) tuples have distinct slots.
    if(warp_m()==0) {
      RawB raw;
      ScalePair scale_cache[NAtoms];
      load_native_stage(raw,shared,stage,warp_n,warp_k);
      #pragma unroll
      for(int step=0;step<WK/16;++step)
        #pragma unroll
        for(int na=0;na<NAtoms;++na) {
          BPair const fragment=load_b_fragment(shared,raw,stage,
              warp_k*(WK/32)+step/2,step/2,step%2,warp_n,lane,na,scale_cache[na]);
          Vector bits;
          __builtin_memcpy(&bits,&fragment,sizeof(bits));
          shared.expanded_b[(step*NAtoms+na)*BThreads+b_tid]=bits;
        }
    }
    __syncthreads();
    #pragma unroll
    for(int step=0;step<WK/16;++step) {
      BPair b[NAtoms];
      #pragma unroll
      for(int na=0;na<NAtoms;++na) {
        Vector const fragment=shared.expanded_b[(step*NAtoms+na)*BThreads+b_tid];
        __builtin_memcpy(&b[na],&fragment,sizeof(fragment));
      }
      #pragma unroll
      for(int ma=0;ma<MAtoms;++ma) {
        FragmentA a;
        load_a_fragment(a,shared,stage,warp_k*(WK/32)+step/2,step%2,ma,lane);
        #pragma unroll
        for(int na=0;na<NAtoms;++na)
          mma_fragment(a,b[na].b0,b[na].b1,acc.tile[ma][na],ma);
      }
    }
    // The next consume_stage wait/barrier protects this single scratch tile.
  }

  struct PipelineContinuation {
    int m_base, n_base;
    bool valid, primed;
  };

  template<bool PrefetchNext>
  CUTLASS_DEVICE static void copy_register_stage(
      Params const& p,SharedStorage& shared,int stage,int tile,
      int m_base,int n_base,ThreadIndex tid,PipelineContinuation const& next) {
    if constexpr (PrefetchNext) {
      auto const target=cutlass::gemm::kernel::KPackMNPipelinePPU::copy(
          uint32_t(tile),uint32_t(p.k/TK),next.valid);
      if(target.next) {
        copy_stage(p,shared,stage,int(target.k),next.m_base,next.n_base,tid);
        return;
      }
    }
    // Out-of-range copies still commit an empty group, as in the original
    // register pipeline, keeping every thread's async group stack aligned.
    copy_stage(p,shared,stage,tile,m_base,n_base,tid);
  }

  struct PipelineRegisters {
    FragmentA a[InterleaveA ? 1 : 2][MAtoms];
    BPair b[NAtoms];
    ScalePair scale_cache[NAtoms];
    RawB raw;
  };

  template<bool PrefetchNext>
  CUTLASS_DEVICE static void consume_register_stage(
      Params const& p,SharedStorage& shared,Accumulator& acc,PipelineRegisters& registers,
      int stage,int iteration,int first_tile,int num_tiles,int m_base,int n_base,
      ThreadIndex tid,int lane,int warp_n,int warp_k,PipelineContinuation const& next) {
    constexpr int Steps=WK/16;
    #pragma unroll
    for(int step=0;step<Steps;++step) {
      bool const next_stage=step==Steps-1;
      bool const has_next=!next_stage || iteration+1<num_tiles;
      int const read_stage=next_stage ? (stage+1)%Stages : stage;
      int const next_step=(step+1)%Steps;
      if(next_stage && has_next) {
        marlin_ppu_detail::cp_async_wait<Stages-2>();
        __syncthreads();
        load_native_stage(registers.raw,shared,read_stage,warp_n,warp_k);
      }
      if constexpr (InterleaveA) {
        #pragma unroll
        for(int ma=0;ma<MAtoms;++ma) {
          #pragma unroll
          for(int na=0;na<NAtoms;++na)
            mma_fragment(registers.a[0][ma],registers.b[na].b0,
                         registers.b[na].b1,acc.tile[ma][na],ma);
          if(has_next)
            load_a_fragment(registers.a[0][ma],shared,read_stage,
                            warp_k*(WK/32)+next_step/2,next_step%2,ma,lane);
        }
      } else {
      if(has_next) {
        #pragma unroll
        for(int ma=0;ma<MAtoms;++ma)
          load_a_fragment(registers.a[(step+1)%2][ma],shared,read_stage,
                          warp_k*(WK/32)+next_step/2,next_step%2,ma,lane);
      }
      #pragma unroll
      for(int na=0;na<NAtoms;++na)
        #pragma unroll
        for(int ma=0;ma<MAtoms;++ma)
          mma_fragment(registers.a[step%2][ma],registers.b[na].b0,
                       registers.b[na].b1,acc.tile[ma][na],ma);
      }
      if(step==Steps-2 && !SkipStage2Barrier) {
        __syncthreads();
        if constexpr (Stages>2)
          copy_register_stage<PrefetchNext>(p,shared,(stage+Stages-1)%Stages,
                     first_tile+iteration+Stages-1,m_base,n_base,tid,next);
      }
      if(has_next) {
        #pragma unroll
        for(int na=0;na<NAtoms;++na)
          registers.b[na]=load_b_fragment(shared,registers.raw,read_stage,
              warp_k*(WK/32)+next_step/2,next_step/2,next_step%2,warp_n,lane,na,
              registers.scale_cache[na]);
      }
    }
    if constexpr (Stages==2) {
      // The next-stage wait/barrier above already publishes every current
      // A-register refill before this overwrite. At the range tail that
      // barrier is absent, so do not issue an unused future copy.
      if constexpr (PrefetchNext) {
        // The range-tail next-stage barrier is absent. Before this valid
        // successor copy, retire every warp's last current-stage read.
        if(next.valid && iteration+1==num_tiles) __syncthreads();
      }
      if(PrefetchNext || !SkipStage2Barrier || iteration+Stages<num_tiles)
        copy_register_stage<PrefetchNext>(
            p,shared,stage,first_tile+iteration+Stages,m_base,n_base,tid,next);
    }
  }

  template<bool PrefetchNext>
  CUTLASS_DEVICE static void run_register_pipeline(
      Params const& p,SharedStorage& shared,Accumulator& acc,
      int first_tile,int num_tiles,int m_base,int n_base,ThreadIndex tid,
      int lane,int warp_n,int warp_k,PipelineContinuation const& next) {
    constexpr int Prime=cutlass::gemm::kernel::KPackMNPipelinePPU::prime(Stages);
    if(!PrefetchNext || !next.primed) {
      #pragma unroll
      for(int stage=0;stage<Prime;++stage)
        copy_stage(p,shared,stage,first_tile+stage,m_base,n_base,tid);
    }
    marlin_ppu_detail::cp_async_wait<Prime-1>();
    __syncthreads();
    PipelineRegisters registers;
    load_native_stage(registers.raw,shared,0,warp_n,warp_k);
    #pragma unroll
    for(int ma=0;ma<MAtoms;++ma)
      load_a_fragment(registers.a[0][ma],shared,0,warp_k*(WK/32),0,ma,lane);
    #pragma unroll
    for(int na=0;na<NAtoms;++na)
      registers.b[na]=load_b_fragment(shared,registers.raw,0,warp_k*(WK/32),
                                      0,0,warp_n,lane,na,registers.scale_cache[na]);
    int const full_cycles=num_tiles/Stages;
    if constexpr (UnrollCycles) {
      #pragma unroll
      for(int cycle=0;cycle<full_cycles;++cycle) {
        #pragma unroll
        for(int stage=0;stage<Stages;++stage)
          consume_register_stage<PrefetchNext>(p,shared,acc,registers,stage,cycle*Stages+stage,
                                 first_tile,num_tiles,m_base,n_base,tid,lane,warp_n,warp_k,next);
      }
    } else {
    #pragma unroll 1
    for(int cycle=0;cycle<full_cycles;++cycle) {
      #pragma unroll
      for(int stage=0;stage<Stages;++stage)
        consume_register_stage<PrefetchNext>(p,shared,acc,registers,stage,cycle*Stages+stage,
                               first_tile,num_tiles,m_base,n_base,tid,lane,warp_n,warp_k,next);
    }
    }
    #pragma unroll
    for(int stage=0;stage<Stages;++stage)
      if(stage<num_tiles%Stages)
        consume_register_stage<PrefetchNext>(p,shared,acc,registers,stage,full_cycles*Stages+stage,
                               first_tile,num_tiles,m_base,n_base,tid,lane,warp_n,warp_k,next);
  }

  CUTLASS_DEVICE static void consume_stage(
      Params const& p, SharedStorage& shared, Accumulator& acc,
      int stage, int future_stage, int tile, int m_base, int n_base,
      ThreadIndex tid, int lane, int warp_n, int warp_k) {
      static_assert(Stages>1);
      marlin_ppu_detail::cp_async_wait<Stages - 2>();
      if constexpr (CohortPipeline==2 || CohortPipeline==4)
        cutlass::arch::NamedBarrier::sync(PipelineThreads,tid/PipelineThreads);
      else
        __syncthreads();
      copy_stage(p, shared, future_stage,
                 tile + Stages - 1, m_base, n_base, tid);
      compute_tile(p,shared,acc,stage,lane,warp_n,warp_k,m_base,tile);
  }

  CUTLASS_DEVICE static void compute_tile(
      Params const& p,SharedStorage& shared,Accumulator& acc,int stage,
      int lane,int warp_n,int warp_k,int m_base,int tile) {
      if constexpr (SharedB) {
        consume_shared_b(shared,acc,stage,lane,warp_n,warp_k);
      } else {
      RawB native_b;
      ScalePair scale_cache[NAtoms];
      load_native_stage(native_b,shared,stage,warp_n,warp_k);
      if constexpr (RegisterPrefetch) {
        // Prefetch the next M16 A fragment before issuing the current MMA.
        // The last M fragment also primes the next K16 step, allowing its
        // shared load to overlap the current tensor work and next B transform.
        FragmentA current_a;
        load_a_fragment(current_a,shared,stage,warp_k*(WK/32),0,0,lane,&p,m_base,tile);
        #pragma unroll
        for(int step=0;step<WK/16;++step) {
          int const kg=step/2,part=step%2,group=warp_k*(WK/32)+kg;
          BPair b[NAtoms];
          #pragma unroll
          for(int na=0;na<NAtoms;++na)
            b[na]=load_b_fragment(shared,native_b,stage,group,kg,part,warp_n,lane,na,scale_cache[na]);
          #pragma unroll
          for(int ma=0;ma<MAtoms;++ma) {
            FragmentA next_a=current_a;
            if(ma+1<MAtoms)
              load_a_fragment(next_a,shared,stage,group,part,ma+1,lane,&p,m_base,tile);
            else if(step+1<WK/16)
              load_a_fragment(next_a,shared,stage,warp_k*(WK/32)+(step+1)/2,
                              (step+1)%2,0,lane,&p,m_base,tile);
            #pragma unroll
            for(int na=0;na<NAtoms;++na)
              mma_fragment(current_a,b[na].b0,b[na].b1,acc.tile[ma][na],ma);
            current_a=next_a;
          }
        }
      } else {
      #pragma unroll
      for (int kg = 0; kg < WK / 32; ++kg) {
        int const group = warp_k * (WK / 32) + kg;
        #pragma unroll
        for (int part = 0; part < 2; ++part) {
          if constexpr (ChunkA) {
            BPair b[NAtoms];
            #pragma unroll
            for (int na=0;na<NAtoms;++na)
              b[na]=load_b_fragment(shared,native_b,stage,group,kg,part,warp_n,lane,na,scale_cache[na]);
            #pragma unroll
            for (int ma=0;ma<MAtoms;++ma) {
              FragmentA a;
              load_a_fragment(a,shared,stage,group,part,ma,lane,&p,m_base,tile);
              #pragma unroll
              for (int na=0;na<NAtoms;++na)
                mma_fragment(a,b[na].b0,b[na].b1,acc.tile[ma][na],ma);
              if constexpr (CompilerFence==1) asm volatile("" ::: "memory");
            }
          } else {
            FragmentA a[MAtoms];
            #pragma unroll
            for (int ma=0;ma<MAtoms;++ma)
              load_a_fragment(a[ma],shared,stage,group,part,ma,lane,&p,m_base,tile);
            #pragma unroll
            for (int na=0;na<NAtoms;++na) {
              auto const b=load_b_fragment(shared,native_b,stage,group,kg,part,warp_n,lane,na,scale_cache[na]);
              #pragma unroll
              for (int ma=0;ma<MAtoms;++ma)
                mma_fragment(a[ma],b.b0,b.b1,acc.tile[ma][na],ma);
            }
          }
          if constexpr (CompilerFence==2) asm volatile("" ::: "memory");
        }
      }
      }
      }
  }

  template<int Partitions = 1, bool FinalBarrier = true>
  CUTLASS_DEVICE static void run(
      Params const& p, SharedStorage& shared, Accumulator& acc,
      int m_base, int n_base, ThreadIndex tid, int partition_idx = 0) {
    int const num_tiles=(p.k/TK)/Partitions;
    run_range<FinalBarrier>(p,shared,acc,m_base,n_base,tid,partition_idx*num_tiles,num_tiles);
  }

  template<bool FinalBarrier = true,bool PrefetchNext = false>
  CUTLASS_DEVICE static void run_range(
      Params const& p,SharedStorage& shared,Accumulator& acc,
      int m_base,int n_base,ThreadIndex tid,int first_tile,int num_tiles,
      PipelineContinuation const& next=PipelineContinuation{}) {
    static_assert(!PrefetchNext || FullRegisterPipeline,
                  "MN continuation is implemented by the register pipeline");
    int const lane = tid % 32;
    int const warp_n = tid / 32 % WarpN;
    int const warp_k = k_cohort(tid);
    #pragma unroll
    for (int ma = 0; ma < MAtoms; ++ma)
      #pragma unroll
      for (int na = 0; na < NAtoms; ++na)
        #pragma unroll
        for (int v = 0; v < FragmentValues; ++v) acc.tile[ma][na].value[v] = 0.f;
    if constexpr (Stages==1) {
      #pragma unroll 1
      for(int tile=0;tile<num_tiles;++tile) {
        copy_stage(p,shared,0,first_tile+tile,m_base,n_base,tid);
        marlin_ppu_detail::cp_async_wait<0>();
        __syncthreads();
        compute_tile(p,shared,acc,0,lane,warp_n,warp_k,m_base,first_tile+tile);
        if(tile+1<num_tiles) __syncthreads();
      }
    } else if constexpr (FullRegisterPipeline) {
      run_register_pipeline<PrefetchNext>(p,shared,acc,first_tile,num_tiles,m_base,n_base,tid,
                            lane,warp_n,warp_k,next);
    } else {
      #pragma unroll
      for (int stage = 0; stage < Stages - 1; ++stage)
        copy_stage(p, shared, stage, first_tile+stage, m_base, n_base, tid);
      if constexpr (StageCycles) {
      int const full_cycles=num_tiles/Stages;
      if constexpr (UnrollCycles) {
        #pragma unroll
        for(int cycle=0;cycle<full_cycles;++cycle) {
          #pragma unroll
          for(int stage=0;stage<Stages;++stage)
            consume_stage(p,shared,acc,stage,(stage+Stages-1)%Stages,
                          first_tile+cycle*Stages+stage,m_base,n_base,tid,lane,warp_n,warp_k);
        }
      } else {
      #pragma unroll 1
      for(int cycle=0;cycle<full_cycles;++cycle) {
        #pragma unroll
        for(int stage=0;stage<Stages;++stage)
          consume_stage(p,shared,acc,stage,(stage+Stages-1)%Stages,
                        first_tile+cycle*Stages+stage,m_base,n_base,tid,lane,warp_n,warp_k);
      }
      }
      #pragma unroll
      for(int stage=0;stage<Stages;++stage)
        if(stage<num_tiles%Stages)
          consume_stage(p,shared,acc,stage,(stage+Stages-1)%Stages,
                        first_tile+full_cycles*Stages+stage,m_base,n_base,tid,lane,warp_n,warp_k);
    } else {
      #pragma unroll 1
      for(int tile=0;tile<num_tiles;++tile)
        consume_stage(p,shared,acc,tile%Stages,(tile+Stages-1)%Stages,first_tile+tile,
                      m_base,n_base,tid,lane,warp_n,warp_k);
      }
    }
    if constexpr (!PrefetchNext) marlin_ppu_detail::cp_async_wait<0>();
    if constexpr (FinalBarrier) __syncthreads();
  }
};

}  // namespace cutlass::gemm::collective
