"""Check identities for the archived full search space, not the shipping subset."""
from tools.sweep_catalog import CONFIGS, SCHEDULES, COOPERATIVE_K, COHORTS, NATIVE_A, NATIVE_B, CHUNK_A, BOUNDED_REDUCTION, CHUNK_REDUCTION, SPECIALIZATIONS, MIN_BLOCKS, STAGE_CYCLES, GLOBAL_SLICES, FUSED_STORE_WARPS, PERSISTENT_MN, MMA_M8, REGISTER_PREFETCH, PAIRED_SCALES, FULL_REGISTER_PIPELINE, DRIVER_OPTIONS
from tools.sweep_catalog import GRID_MULTIPLE, VECTOR_OUTPUT, DIRECT_OUTPUT, UNROLL_CYCLES
from tools.sweep_catalog import COMPILER_FENCE, OPAQUE_COORDINATES, SHARED_B, UNSIGNED_INDICES
from tools.sweep_catalog import INTERLEAVED_A, STREAM_K_WORKERS, N_FAST_RASTER
from tools.sweep_catalog import STATIC_M, PRUNE_ROWS, TAIL_M8, CACHE_SCALES, COMPACT_OUTPUT
from tools.sweep_catalog import SKIP_STAGE2_BARRIER
from tools.sweep_catalog import REDUCTION_STORAGE
from tools.sweep_catalog import DIRECT_A
from tools.sweep_catalog import COHORT_PIPELINE
from tools.sweep_catalog import WARP_ORDER
from tools.sweep_catalog import B_PRODUCER_WARP
from tools.sweep_catalog import PREFETCH_REDUCTION
from tools.sweep_catalog import GROUP_OUTPUT_STORES
from tools.sweep_catalog import INTEGER_ZERO
from tools.sweep_catalog import ZERO_WORD_LOAD
from tools.sweep_catalog import SINGLE_ZERO_BIAS
from tools.sweep_catalog import INTERLEAVE_ZERO_GROUPS
from tools.sweep_catalog import PAIRED_ZERO_BIAS
from tools.sweep_catalog import ZERO_BIAS_CACHE
from tools.sweep_catalog import PERMUTE_ZERO_BIAS
from tools.sweep_catalog import PREPARED_ZERO_BIAS
from tools.sweep_catalog import BYTE_ZERO_WORDS
from tools.sweep_catalog import INLINE_REDUCTION
from tools.sweep_catalog import RASTER_GROUP_M
from tools.sweep_catalog import STREAM_K_MODE
from tools.sweep_catalog import GLOBAL_OUTPUT_PADDING
from tools.sweep_catalog import PERSISTENT_PREFETCH


def test_affine_candidate_registry():
    identities = [(config, SCHEDULES.get(index, (0, 0)), COOPERATIVE_K.get(index), COHORTS.get(index),
                   index in NATIVE_A, index in NATIVE_B, index in CHUNK_A,
                   index in BOUNDED_REDUCTION, index in CHUNK_REDUCTION,
                   DRIVER_OPTIONS.get(index,(0,0)),SPECIALIZATIONS.get(index,(0,0)),
                   MIN_BLOCKS.get(index,1),index in STAGE_CYCLES,GLOBAL_SLICES.get(index,1),
                   FUSED_STORE_WARPS.get(index,0),index in PERSISTENT_MN,MMA_M8.get(index,0),
                   index in REGISTER_PREFETCH,index in PAIRED_SCALES,index in FULL_REGISTER_PIPELINE,
                   GRID_MULTIPLE.get(index,40),index in VECTOR_OUTPUT,index in DIRECT_OUTPUT,
                   index in UNROLL_CYCLES,COMPILER_FENCE.get(index,0),index in OPAQUE_COORDINATES,
                   index in SHARED_B,index in UNSIGNED_INDICES,index in INTERLEAVED_A,
                   STREAM_K_WORKERS.get(index,0),index in N_FAST_RASTER,
                   STATIC_M.get(index,0),index in PRUNE_ROWS,index in TAIL_M8,index in CACHE_SCALES,
                   COMPACT_OUTPUT.get(index,0),index in SKIP_STAGE2_BARRIER,
                   REDUCTION_STORAGE.get(index,0),DIRECT_A.get(index,0),
                   COHORT_PIPELINE.get(index,0),WARP_ORDER.get(index,0),
                   B_PRODUCER_WARP.get(index,0),index in PREFETCH_REDUCTION,
                   index in GROUP_OUTPUT_STORES,index in INTEGER_ZERO,index in ZERO_WORD_LOAD,
                   index in SINGLE_ZERO_BIAS,index in INTERLEAVE_ZERO_GROUPS,
                   index in PAIRED_ZERO_BIAS,index in ZERO_BIAS_CACHE,
                   index in PERMUTE_ZERO_BIAS,index in PREPARED_ZERO_BIAS,
                   index in BYTE_ZERO_WORDS,index in INLINE_REDUCTION,RASTER_GROUP_M.get(index,1),
                   STREAM_K_MODE.get(index,0),GLOBAL_OUTPUT_PADDING.get(index,8),
                   index in PERSISTENT_PREFETCH)
                  for index, config in enumerate(CONFIGS)]
    assert len(identities) == len(set(identities))
    assert (64, 128, 64, 64, 32, 3) in CONFIGS
    for index,(tm, tn, tk, wm, wn, stages) in enumerate(CONFIGS):
        assert tm % wm == tn % wn == 0
        assert wn * tk * 4 >= 4096
        assert stages >= 1
        if index in CHUNK_REDUCTION:
            assert index not in INLINE_REDUCTION
        if index in SKIP_STAGE2_BARRIER:
            assert stages==2 and index in FULL_REGISTER_PIPELINE
        if index in PERSISTENT_PREFETCH:
            assert index in PERSISTENT_MN and index in DIRECT_OUTPUT
            assert index in FULL_REGISTER_PIPELINE and COOPERATIVE_K[index]==tk
            assert GLOBAL_SLICES.get(index,1)==1 and not STREAM_K_WORKERS.get(index,0)
            assert SPECIALIZATIONS[index][1]//tk%stages==0
        assert 1<=RASTER_GROUP_M.get(index,1)<=16
        if RASTER_GROUP_M.get(index,1)>1:
            assert index in N_FAST_RASTER
        assert 0<=STREAM_K_MODE.get(index,0)<=3
        if STREAM_K_MODE.get(index,0)>0:
            assert STREAM_K_WORKERS.get(index,0)>0 and index not in PERSISTENT_MN
        assert GLOBAL_OUTPUT_PADDING.get(index,8) in (0,8)
        if GLOBAL_OUTPUT_PADDING.get(index,8)==0:
            assert GLOBAL_SLICES.get(index,1)>1 or STREAM_K_WORKERS.get(index,0)>0
        if index in COOPERATIVE_K:
            assert wm%8==0
            assert wm<16 or wm%16==0 or index in TAIL_M8
        if stages==1:
            assert index in COOPERATIVE_K and index in NATIVE_A and index in NATIVE_B
            assert index not in FULL_REGISTER_PIPELINE
