#pragma once
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t version, size;
    // zero_mode: 0 = symmetric center 8; 1 = per-group uint4 integer zero.
    // config=-1 selects the native default during query/prepare (split=1).
    int32_t m, n, k, group_size, config, split, zero_mode;
} qwa_problem_v1;

typedef struct {
    uint32_t version, size;
    // zeros is null for mode 0; mode 1 uses uint8[K/32,N] values in [0,15].
    // prepare packs zeros into workspace; run never reads this source buffer.
    // Keep workspace exclusive to this plan until destroy; prepare populates
    // candidate-specific metadata that must survive subsequent run/replay calls.
    void const *input, *weight, *scales, *zeros;
    void *output, *workspace;
    uint64_t workspace_bytes;
    void *stream;
} qwa_buffers_v1;

typedef struct {
    uint32_t version, size;
    int32_t id, tm, tn, tk, wm, wn, stages;
} qwa_config_v1;

typedef struct {
    uint32_t version, size;
    uint64_t workspace_bytes, shared_bytes;
    int32_t threads, reserved;
} qwa_info_v1;

int quactlize_ppu_w4a16_config_count_v1(void);
uint64_t quactlize_ppu_w4a16_mapping_v1(void);
int quactlize_ppu_w4a16_config_v1(int, qwa_config_v1*);
int quactlize_ppu_w4a16_config_zero_mode_v1(int, int32_t*);
int quactlize_ppu_w4a16_pack_host_v1(uint8_t const*, int32_t, int32_t, void*, uint64_t);
int quactlize_ppu_w4a16_select_v1(qwa_problem_v1 const*, qwa_config_v1*);
int quactlize_ppu_w4a16_query_v1(qwa_problem_v1 const*, qwa_info_v1*);
int quactlize_ppu_w4a16_prepare_v1(qwa_problem_v1 const*, qwa_buffers_v1 const*, void**);
int quactlize_ppu_w4a16_run_v1(void*, void*);
void quactlize_ppu_w4a16_destroy_v1(void*);
char const* quactlize_ppu_w4a16_error_v1(void);

#ifdef __cplusplus
}
static_assert(sizeof(qwa_problem_v1) == 36, "W4A16 problem ABI drift");
static_assert(sizeof(qwa_buffers_v1) == 72, "W4A16 buffers ABI drift");
static_assert(sizeof(qwa_config_v1) == 36, "W4A16 config ABI drift");
static_assert(sizeof(qwa_info_v1) == 32, "W4A16 info ABI drift");
#endif
