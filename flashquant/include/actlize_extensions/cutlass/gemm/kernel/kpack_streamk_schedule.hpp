/***************************************************************************************************
 * Copyright (c) 2026, quactlize contributors.
 * SPDX-License-Identifier: BSD-3-Clause
 **************************************************************************************************/
#pragma once

#include <cstdint>
#include <limits>

#if defined(CUTLASS_HOST_DEVICE)
#define QUACTLIZE_STREAMK_HD CUTLASS_HOST_DEVICE
#elif defined(__CUDACC__) || defined(__HGGCCC__)
#define QUACTLIZE_STREAMK_HD __host__ __device__
#else
#define QUACTLIZE_STREAMK_HD
#endif

namespace cutlass::gemm::kernel {

struct KPackTileCoordinatePPU {
  uint32_t m, n;
};

struct KPackMNCopyPPU {
  uint32_t k;
  bool next;
};

// The register pipeline issues Prime initial copies and then one future
// copy per consumed K tile. At an MN boundary, its last Prime copies can
// prime the successor, provided the stage ring returns to stage zero.
struct KPackMNPipelinePPU {
  QUACTLIZE_STREAMK_HD static constexpr uint32_t prime(uint32_t stages) {
    return stages>2 ? stages-1 : 2;
  }
  QUACTLIZE_STREAMK_HD static constexpr bool aligned(uint32_t k_tiles,uint32_t stages) {
    return stages>1 && k_tiles>=prime(stages) && k_tiles%stages==0;
  }
  QUACTLIZE_STREAMK_HD static constexpr KPackMNCopyPPU copy(
      uint32_t k,uint32_t k_tiles,bool has_next) {
    return has_next && k>=k_tiles ? KPackMNCopyPPU{k-k_tiles,true}
                                 : KPackMNCopyPPU{k,false};
  }
};

// Inputs describe a valid nonempty MN tile grid. Group adjacent M tiles
// inside each N column, including a shorter final M group.
template<uint32_t GroupM>
QUACTLIZE_STREAMK_HD constexpr KPackTileCoordinatePPU grouped_mn_tile(
    uint32_t tile,uint32_t m_tiles,uint32_t n_tiles) {
  static_assert(GroupM>=1 && GroupM<=16);
  if constexpr (GroupM==1) {
    return {tile/n_tiles,tile%n_tiles};
  } else {
    uint32_t const group_span=GroupM*n_tiles;
    uint32_t const first_m=(tile/group_span)*GroupM;
    uint32_t const within=tile%group_span;
    if(first_m+GroupM<=m_tiles)
      return {first_m+within%GroupM,within/GroupM};
    uint32_t const remaining=m_tiles-first_m;
    return {first_m+within%remaining,within/remaining};
  }
}

struct KPackStreamKWorkPPU {
  uint32_t tile=0, k_begin=0, k_count=0;
  uint32_t peer=0, peers=0, slot=0;
};

// Coordinates count complete mainloop K tiles, never bytes or weight groups.
// Nonempty worker intervals give each split output tile consecutive owners.
// Its first owner identifies a unique worker boundary, so scratch is bounded
// by worker count rather than matrix area.
struct KPackStreamKSchedulePPU {
  uint32_t tiles=0, k_tiles=0, workers=0, units=0;

  QUACTLIZE_STREAMK_HD static constexpr KPackStreamKSchedulePPU make(
      uint32_t tiles,uint32_t k_tiles,uint32_t workers) {
    uint64_t const units=uint64_t(tiles)*k_tiles;
    if(!tiles || !k_tiles || !workers || units<workers ||
       units>std::numeric_limits<uint32_t>::max()/workers) return {};
    return {tiles,k_tiles,workers,uint32_t(units)};
  }
  QUACTLIZE_STREAMK_HD constexpr bool valid() const { return units!=0; }
  static constexpr KPackStreamKSchedulePPU make_tail(
      uint32_t tiles,uint32_t k_tiles,uint32_t workers) {
    if(!workers) return {};
    uint32_t const tail_tiles=tiles<workers ? tiles : workers+tiles%workers;
    return make(tail_tiles,k_tiles,workers);
  }
  QUACTLIZE_STREAMK_HD constexpr uint32_t begin(uint32_t worker) const {
    return units*worker/workers;
  }
  QUACTLIZE_STREAMK_HD constexpr uint32_t owner(uint32_t unit) const {
    return ((unit+1)*workers-1)/units;
  }
  QUACTLIZE_STREAMK_HD constexpr KPackStreamKWorkPPU next(
      uint32_t worker,uint32_t cursor) const {
    if(worker>=workers || cursor<begin(worker) || cursor>=begin(worker+1)) return {};
    uint32_t const tile=cursor/k_tiles, first=owner(tile*k_tiles);
    uint32_t const last=owner((tile+1)*k_tiles-1);
    uint32_t const kb=cursor%k_tiles;
    uint32_t const remaining=begin(worker+1)-cursor;
    uint32_t const count=remaining<k_tiles-kb ? remaining : k_tiles-kb;
    return {tile,kb,count,worker-first,last-first+1,first};
  }
  constexpr uint32_t max_contributors() const {
    uint32_t maximum=0;
    if(valid())
      for(uint32_t tile=0;tile<tiles;++tile) {
        uint32_t const count=owner((tile+1)*k_tiles-1)-owner(tile*k_tiles)+1;
        if(count>maximum) maximum=count;
      }
    return maximum;
  }
};

}  // namespace cutlass::gemm::kernel

#undef QUACTLIZE_STREAMK_HD
