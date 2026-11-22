/***************************************************************************************************
 * Copyright (c) 2026, quactlize contributors.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Authoritative output-coordinate map for the standalone Marlin PPU kernel.
 **************************************************************************************************/
#pragma once

#include "cutlass/cutlass.h"

namespace cutlass::gemm::kernel::marlin_ppu_detail {

// The K0 cohort is the only cohort that hands off or writes output.  Keep its
// map host/device constexpr so production and the exhaustive L179 proof share
// one seam rather than maintaining two mutually-consistent implementations.
template <int InstructionM>
CUTLASS_HOST_DEVICE constexpr int output_row(int lane, int value) {
  static_assert(InstructionM == 8 || InstructionM == 16);
  return lane / 4 +
         (InstructionM == 16 ? (((value >> 2) & 1) << 3) : 0);
}

template <int TileN, int NBlocksPerWarp = 4>
CUTLASS_HOST_DEVICE constexpr int output_n_base(
    int n_tile, int output_thread, int n_block) {
  static_assert(TileN >= 64 && TileN % 64 == 0);
  static_assert(NBlocksPerWarp == 4 || NBlocksPerWarp == 8);
  int const warp_n = output_thread / 32;
  return n_tile * TileN +
         (warp_n * NBlocksPerWarp + n_block) * 16;
}

template <int InstructionM>
CUTLASS_HOST_DEVICE constexpr int output_col_offset(int lane, int value) {
  static_assert(InstructionM == 8 || InstructionM == 16);
  return lane % 4 + ((value % 4) << 2);
}

// One slot holds four FP32 values from one output row. Call only for live
// rows, with value at the start of a four-value fragment group.
template <int InstructionM>
CUTLASS_HOST_DEVICE constexpr int compact_partial_vector_slot(
    int rows, int n_atoms, int warp_n, int lane, int n_atom, int value) {
  return ((warp_n * n_atoms + n_atom) * rows + output_row<InstructionM>(lane, value)) * 4 +
         output_col_offset<InstructionM>(lane, 0);
}

}  // namespace cutlass::gemm::kernel::marlin_ppu_detail
