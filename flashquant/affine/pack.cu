#include "api.h"
#include "format.hpp"
#include <climits>
#include <vector>
#include <exception>

extern "C" int quactlize_ppu_w4a16_pack_host_v1(
        uint8_t const* codes, int32_t n, int32_t k, void* output, uint64_t bytes) {
    if (!codes || !output || n <= 0 || k <= 0 || n % 256 || k % 256 ||
        int64_t(n) * k > INT_MAX || bytes != uint64_t(n) * k / 2) return 20;
    auto source = reinterpret_cast<uintptr_t>(codes), destination = reinterpret_cast<uintptr_t>(output);
    if ((source <= destination && destination - source < uint64_t(n) * k) ||
        (destination < source && source - destination < bytes)) return 20;
    try {
        if constexpr (quactlize::affine::kClassicWeights) {
            std::vector<uint8_t> logical(uint64_t(n) * k);
            for (int row = 0; row < k; ++row)
                for (int column = 0; column < n; ++column)
                    logical[uint64_t(row) * n + column] = codes[uint64_t(column) * k + row];
            return quactlize::marlin::pack_biased_int4_bytes(
                logical.data(),logical.size(),static_cast<uint8_t*>(output),bytes,k,n) ? 0 : 20;
        }
        std::vector<uint8_t> native(bytes);
        for (uint64_t index = 0; index < uint64_t(n) * k; index += 2) {
            if (codes[index] > 15 || codes[index + 1] > 15) return 20;
            native[index / 2] = codes[index] | (codes[index + 1] << 4);
        }
        return q4_kpack4::prepare(native.data(), static_cast<uint8_t*>(output), n, k);
    } catch (std::exception const&) {
        return 20;
    }
}
