#pragma once
#include "q4_kpack4_offline.hpp"
#include "marlin_format_ppu.hpp"

#ifndef QUACTLIZE_W4A16_CLASSIC_WEIGHTS
#define QUACTLIZE_W4A16_CLASSIC_WEIGHTS 0
#endif

namespace quactlize::affine {
inline constexpr bool kClassicWeights = QUACTLIZE_W4A16_CLASSIC_WEIGHTS != 0;
inline constexpr uint64_t kWeightMappingId =
    kClassicWeights ? 0x5741344d4c000001ull : q4_kpack4::kMappingId;
}
