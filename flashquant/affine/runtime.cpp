#include "internal.hpp"
#include "format.hpp"
#include <climits>
#include <memory>
#include <string>

namespace {
using namespace quactlize::affine;
thread_local std::string error;

template<class Action>
int checked(Action action) {
    try {
        action();
        error.clear();
        return 0;
    } catch (std::exception const& exception) {
        error = exception.what();
        return 20;
    }
}

Entry const& entry_for(qwa_problem_v1 const* p) {
    require(p && p->version == 1 && p->size == sizeof(*p), "invalid W4A16 problem ABI");
    require(p->m > 0 && p->n > 0 && p->k > 0 && p->n % 256 == 0 && p->k % 256 == 0,
            "W4A16 requires positive M and N/K multiples of 256");
    require(int64_t(p->m) * p->n <= INT_MAX && int64_t(p->m) * p->k <= INT_MAX &&
            int64_t(p->n) * p->k <= INT_MAX, "W4A16 extent exceeds indexing range");
    require(p->group_size == 32 && (p->zero_mode == 0 || p->zero_mode == 1),
            "unsupported W4A16 quantization contract");
    require(p->split == 1 || p->split == 2 || p->split == 4 || p->split == 8, "unsupported W4A16 split");
    int const config=p->config==-1 ? default_config(*p) : p->config;
    require(config>=0,"no native W4A16 default is compiled for this contract");
    for (int i = 0; i < entry_count; ++i)
        if (entries[i].config.id == config) {
            require(entries[i].zero_mode==p->zero_mode,"candidate quantization mode does not match");
            return entries[i];
        }
    throw std::invalid_argument("W4A16 candidate is not compiled");
}

bool aligned(void const* pointer, uintptr_t alignment) {
    return pointer && reinterpret_cast<uintptr_t>(pointer) % alignment == 0;
}

bool overlap(void const* a, uint64_t as, void const* b, uint64_t bs) {
    auto x = reinterpret_cast<uintptr_t>(a), y = reinterpret_cast<uintptr_t>(b);
    return x <= y ? y - x < as : x - y < bs;
}

}

extern "C" int quactlize_ppu_w4a16_config_count_v1() {
    return quactlize::affine::entry_count;
}

extern "C" uint64_t quactlize_ppu_w4a16_mapping_v1() {
    return quactlize::affine::kWeightMappingId;
}

extern "C" int quactlize_ppu_w4a16_config_v1(int index, qwa_config_v1* out) {
    return checked([&] {
        require(out && index >= 0 && index < entry_count, "invalid W4A16 candidate index");
        *out = entries[index].config;
    });
}

extern "C" int quactlize_ppu_w4a16_config_zero_mode_v1(int index, int32_t* out) {
    return checked([&] {
        require(out && index>=0 && index<entry_count,"invalid W4A16 candidate index");
        *out=entries[index].zero_mode;
    });
}

extern "C" int quactlize_ppu_w4a16_query_v1(qwa_problem_v1 const* p, qwa_info_v1* out) {
    return checked([&] {
        require(out, "null W4A16 query output");
        *out = entry_for(p).query(*p);
    });
}

extern "C" int quactlize_ppu_w4a16_select_v1(qwa_problem_v1 const* p, qwa_config_v1* out) {
    return checked([&] {
        require(out,"null W4A16 selection output");
        auto const& entry=entry_for(p);
        entry.query(*p);
        *out=entry.config;
    });
}

extern "C" int quactlize_ppu_w4a16_prepare_v1(
        qwa_problem_v1 const* p, qwa_buffers_v1 const* b, void** out) {
    if (out) *out = nullptr;
    return checked([&] {
        require(out && b && b->version == 1 && b->size == sizeof(*b), "invalid W4A16 prepare ABI");
        auto const& entry = entry_for(p);
        auto info = entry.query(*p);
        require(aligned(b->input, 16) && aligned(b->weight, 16) && aligned(b->scales, 16) &&
                aligned(b->output, 16) && (p->zero_mode ? aligned(b->zeros,16) : !b->zeros),
                "invalid W4A16 pointers");
        require(b->workspace_bytes >= info.workspace_bytes &&
                (!info.workspace_bytes || aligned(b->workspace, 256)), "insufficient W4A16 workspace");
        require(!info.workspace_bytes ||
                (!overlap(b->workspace,info.workspace_bytes,b->input,uint64_t(p->m)*p->k*2) &&
                 !overlap(b->workspace,info.workspace_bytes,b->weight,uint64_t(p->n)*p->k/2) &&
                 !overlap(b->workspace,info.workspace_bytes,b->scales,uint64_t(p->n)*p->k/16) &&
                 (!p->zero_mode || !overlap(b->workspace,info.workspace_bytes,b->zeros,uint64_t(p->n)*p->k/32))),
                "W4A16 workspace aliases an input");
        uint64_t output_bytes = uint64_t(p->m) * p->n * 2;
        require(!overlap(b->output, output_bytes, b->input, uint64_t(p->m) * p->k * 2) &&
                !overlap(b->output, output_bytes, b->weight, uint64_t(p->n) * p->k / 2) &&
                !overlap(b->output, output_bytes, b->scales, uint64_t(p->n) * p->k / 16) &&
                (!p->zero_mode || !overlap(b->output,output_bytes,b->zeros,uint64_t(p->n)*p->k/32)) &&
                (!info.workspace_bytes || !overlap(b->output, output_bytes, b->workspace, info.workspace_bytes)),
                "W4A16 output aliases an input or workspace");
        *out = entry.prepare(*p, *b);
    });
}

extern "C" int quactlize_ppu_w4a16_run_v1(void* handle, void* stream) {
    if (!handle) {
        error = "null W4A16 plan";
        return 20;
    }
    int status = static_cast<quactlize::affine::Plan*>(handle)->run(stream);
    if (status) error = "W4A16 CUTLASS launch failed";
    return status;
}

extern "C" void quactlize_ppu_w4a16_destroy_v1(void* handle) {
    delete static_cast<quactlize::affine::Plan*>(handle);
}

extern "C" char const* quactlize_ppu_w4a16_error_v1() {
    return error.c_str();
}
