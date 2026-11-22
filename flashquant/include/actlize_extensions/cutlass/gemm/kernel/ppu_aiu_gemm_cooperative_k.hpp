// Copyright (c) 2026, quactlize contributors.
// SPDX-License-Identifier: BSD-3-Clause
#pragma once
#include "cute/tensor.hpp"
#include "cutlass/numeric_types.h"

namespace cutlass::gemm::kernel {

template<class Mainloop, int Cohorts>
struct GemmUniversalMixedInputCooperativeK {
  using CollectiveMainloop = Mainloop;
  using TileShape = typename Mainloop::TileShape;
  using TiledMma = typename Mainloop::TiledMma;
  using ProblemShape = cute::Shape<int,int,int,int>;
  using Accumulator = decltype(cute::partition_fragment_C(
      TiledMma{}, cute::take<0,2>(TileShape{})));
  static constexpr int TM = int(cute::size<0>(TileShape{}));
  static constexpr int TN = int(cute::size<1>(TileShape{}));
  static constexpr int TK = int(cute::size<2>(TileShape{}));
  static constexpr int CohortThreads = int(cute::size(TiledMma{}));
  static constexpr int Values = int(cute::size(Accumulator{}));
  static constexpr int MaxThreadsPerBlock = Cohorts * CohortThreads;
  static constexpr int MinBlocksPerMultiprocessor = 1;
  static_assert(Cohorts == 2 || Cohorts == 4 || Cohorts == 8);
  static_assert(MaxThreadsPerBlock <= 1024);
  static_assert(Values * CohortThreads == TM * TN);
  static_assert(Values % 4 == 0);

  struct Params {
    ProblemShape problem_shape;
    typename Mainloop::Params mainloop;
    half_t* output;
  };
  struct alignas(128) CohortStorage { typename Mainloop::SharedStorage mainloop; };
  union SharedStorage {
    CohortStorage cohorts[Cohorts];
    alignas(128) float partial[(Cohorts - 1) * TM * TN];
    alignas(128) half_t output[TM * (TN + 8)];
  };
  static constexpr int SharedStorageSize = sizeof(SharedStorage);

  CUTLASS_DEVICE void operator()(Params const& p, char* smem) {
    using namespace cute;
    auto& shared = *reinterpret_cast<SharedStorage*>(smem);
    int const tid = int(threadIdx.x);
    int const cohort = tid / CohortThreads;
    int const local_tid = tid % CohortThreads;
    auto [M,N,K,L] = p.problem_shape;
    (void)L;
    auto const block_coord = make_coord(int(blockIdx.x),int(blockIdx.y),_,Int<0>{});
    Mainloop mainloop;
    auto load_inputs = mainloop.load_init(p.problem_shape,block_coord,p.mainloop);
    Tensor gA = get<0>(load_inputs);
    auto const k_shape = shape<2>(gA);
    int const count = K / TK / Cohorts;
    auto iter = make_coord_iterator(idx2crd(cohort * count,k_shape), k_shape);
    TiledMma tiled_mma;
    auto acc = partition_fragment_C(tiled_mma,take<0,2>(TileShape{}));
    clear(acc);
    mainloop(p.mainloop,load_inputs,acc,iter,count,local_tid,
             reinterpret_cast<char*>(&shared.cohorts[cohort].mainloop),
             cohort * (CohortThreads / 32));
    if (cohort != 0) {
      CUTLASS_PRAGMA_UNROLL
      for (int i = 0; i < Values; i += 4) {
        int offset = (cohort-1)*TM*TN + ((i/4)*CohortThreads+local_tid)*4;
        *reinterpret_cast<float4*>(&shared.partial[offset]) =
            make_float4(acc(i),acc(i+1),acc(i+2),acc(i+3));
      }
    }
    __syncthreads();
    if (cohort == 0) {
      CUTLASS_PRAGMA_UNROLL
      for (int peer = 0; peer < Cohorts - 1; ++peer)
        CUTLASS_PRAGMA_UNROLL
        for (int i = 0; i < Values; i += 4) {
          int offset = peer*TM*TN + ((i/4)*CohortThreads+local_tid)*4;
          float4 const value = *reinterpret_cast<float4 const*>(&shared.partial[offset]);
          acc(i) += value.x;
          acc(i+1) += value.y;
          acc(i+2) += value.z;
          acc(i+3) += value.w;
        }
    }
    __syncthreads();
    if (cohort == 0) {
      auto thread_mma = tiled_mma.get_thread_slice(local_tid);
      auto identity = make_identity_tensor(make_shape(Int<TM>{},Int<TN>{}));
      auto coords = thread_mma.partition_C(identity);
      CUTLASS_PRAGMA_UNROLL
      for (int i = 0; i < Values; ++i)
        shared.output[int(get<0>(coords(i)))*(TN+8)+int(get<1>(coords(i)))] = half_t(acc(i));
    }
    __syncthreads();
    auto* output = reinterpret_cast<uint4*>(p.output);
    auto const* staged = reinterpret_cast<uint4 const*>(shared.output);
    CUTLASS_PRAGMA_UNROLL
    for (int i = tid; i < TM*(TN/8); i += MaxThreadsPerBlock) {
      int row = i/(TN/8), chunk=i%(TN/8);
      if (int(blockIdx.x)*TM+row < M)
        output[(int(blockIdx.x)*TM+row)*(N/8)+int(blockIdx.y)*(TN/8)+chunk] =
            staged[row*((TN+8)/8)+chunk];
    }
  }
};

}  // namespace cutlass::gemm::kernel
