CONFIGS = (
    (16, 64, 64, 16, 32, 3),
    (16, 128, 64, 16, 32, 3),
    (16, 128, 128, 16, 32, 3),
    (16, 128, 256, 16, 32, 3),
    (32, 128, 64, 32, 32, 3),
    (64, 128, 64, 64, 32, 3),
    (128, 128, 64, 64, 32, 3),
    (128, 256, 64, 64, 32, 3),
    (128, 256, 64, 64, 64, 3),
    (64, 128, 128, 32, 32, 3),
    (8, 64, 128, 8, 16, 2),
    (16, 64, 128, 16, 16, 2),
    (64, 128, 256, 64, 16, 2),
    (128, 64, 128, 128, 32, 2),
    (64, 64, 128, 64, 32, 2),
    (128, 128, 128, 64, 32, 2),
    (128, 128, 128, 128, 32, 2),
    (32, 64, 128, 32, 16, 2),
    (32, 128, 128, 32, 16, 2),
    (64, 64, 256, 64, 16, 2),
    (128, 64, 64, 128, 32, 3),
    (128, 128, 64, 128, 32, 3),
    (64, 64, 64, 64, 32, 3),
    (256, 64, 64, 64, 32, 2),
    (16, 64, 128, 16, 16, 2),
    (16, 64, 128, 16, 16, 2),
    (16, 64, 128, 16, 16, 2),
    (16, 64, 128, 16, 16, 2),
    (16, 64, 128, 16, 16, 2),
    (16, 64, 128, 16, 16, 2),
)

SCHEDULES = {
    24: (1, 1), 25: (1, 2), 26: (1, 4),
    27: (2, 1), 28: (2, 2), 29: (2, 4),
}

COOPERATIVE_K = {30: 64, 31: 64, 32: 64}
CONFIGS += (
    (16, 64, 512, 16, 32, 3),
    (64, 64, 128, 64, 32, 3),
    (128, 128, 128, 128, 32, 2),
)

COHORTS = {33: 2, 34: 4, 35: 8, 36: 4, 37: 2}
CONFIGS += (
    (16, 64, 128, 16, 16, 2),
    (16, 64, 128, 16, 16, 2),
    (16, 64, 128, 16, 16, 2),
    (64, 64, 64, 64, 32, 3),
    (128, 64, 64, 128, 32, 2),
)

CONFIGS += (
    (64, 64, 64, 64, 16, 2),
    (64, 64, 64, 64, 16, 3),
    (64, 64, 64, 64, 16, 4),
    (64, 128, 64, 64, 16, 2),
    (64, 64, 128, 64, 16, 2),
    (128, 64, 64, 128, 16, 2),
    (16, 64, 64, 16, 32, 3),
    (16, 64, 128, 16, 32, 2),
    (16, 64, 256, 16, 32, 2),
)
COHORTS.update({44: 8, 45: 4, 46: 4})

CONFIGS += (
    (16, 64, 512, 16, 32, 3),
    (64, 64, 256, 64, 32, 3),
    (128, 64, 128, 128, 32, 3),
    (128, 128, 128, 128, 32, 3),
)
COOPERATIVE_K.update({47: 64, 48: 32, 49: 32, 50: 64})
NATIVE_A = {47,48,49,50}

# Driver options are (vectorized partial reduction, flat grid padded to 40).
CONFIGS += (
    CONFIGS[47],
    CONFIGS[47],
    CONFIGS[47],
    CONFIGS[48],
    CONFIGS[50],
    CONFIGS[49],
    (16, 128, 512, 16, 32, 2),
)
COOPERATIVE_K.update({51:64,52:64,53:64,54:32,55:64,56:32,57:64})
NATIVE_A.update(range(51,58))
DRIVER_OPTIONS = {
    51:(1,0),52:(0,1),53:(1,1),54:(1,1),55:(1,1),56:(1,1),57:(1,1),
}
CONFIGS += (CONFIGS[51],CONFIGS[54],CONFIGS[55])
COOPERATIVE_K.update({58:64,59:32,60:64})
NATIVE_A.update({58,59,60})
NATIVE_B = {58,59,60}
DRIVER_OPTIONS.update({58:(1,0),59:(1,1),60:(1,1)})
CONFIGS += (CONFIGS[58],CONFIGS[59],CONFIGS[60])
COOPERATIVE_K.update({61:64,62:32,63:64})
NATIVE_A.update({61,62,63})
NATIVE_B.update({61,62,63})
CHUNK_A = {61,62,63}
DRIVER_OPTIONS.update({61:(1,0),62:(1,1),63:(1,1)})
CONFIGS += (
    CONFIGS[61],CONFIGS[62],CONFIGS[63],
    (128,64,128,128,32,3),(128,64,128,128,32,3),
)
COOPERATIVE_K.update({64:64,65:32,66:64,67:32,68:32})
NATIVE_A.update(range(64,69))
NATIVE_B.update(range(64,69))
CHUNK_A.update(range(64,69))
BOUNDED_REDUCTION = {64,65,66,68}
DRIVER_OPTIONS.update({64:(1,0),65:(1,1),66:(1,1),67:(1,1),68:(1,1)})
CONFIGS += (
    CONFIGS[61],CONFIGS[59],CONFIGS[62],CONFIGS[63],
    (64,64,256,64,32,2),
    (64,64,256,64,32,2),
    (64,128,256,64,32,2),
    (64,128,256,64,32,2),
)
COOPERATIVE_K.update({69:64,70:32,71:32,72:64,73:32,74:64,75:64,76:64})
NATIVE_A.update(range(69,77))
NATIVE_B.update(range(69,77))
CHUNK_A.update({69,71,72,76})
CHUNK_REDUCTION = set(range(69,77))
DRIVER_OPTIONS.update({index:(1,int(index!=69)) for index in range(69,77)})

SPECIALIZATIONS = {}
for base,n,k in (
    (61,1024,0),(61,0,3072),(61,1024,3072),(61,2048,3072),
    (73,1024,3072),(76,2048,3072),(63,1024,3072),(63,2048,3072),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    COOPERATIVE_K[index]=COOPERATIVE_K[base]
    DRIVER_OPTIONS[index]=DRIVER_OPTIONS[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION):
        if base in feature:
            feature.add(index)
    SPECIALIZATIONS[index]=(n,k)

# A compiler launch bound; actual residency still includes shared-memory,
# register billing and useful grid size.
MIN_BLOCKS = {}
for base,minimum,geometry,wk in (
    (59,2,None,None),(73,2,None,None),
    (81,2,None,None),(82,2,None,None),
    (79,2,None,None),(80,2,None,None),(61,2,None,None),
    (63,1,(128,128,128,128,32,2),None),
    (92,2,None,None),(92,4,None,None),
    (74,4,None,None),(76,2,None,None),
    (73,1,(64,128,128,64,32,3),32),(97,2,None,None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base] if geometry is None else geometry,)
    COOPERATIVE_K[index]=COOPERATIVE_K[base] if wk is None else wk
    DRIVER_OPTIONS[index]=DRIVER_OPTIONS[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION):
        if base in feature:
            feature.add(index)
    if base in SPECIALIZATIONS:
        SPECIALIZATIONS[index]=SPECIALIZATIONS[base]
    MIN_BLOCKS[index]=minimum

STAGE_CYCLES = set()
for base in (79,80,81,82,63,92,74,69):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION):
        if base in feature:
            feature.add(index)
    STAGE_CYCLES.add(index)

for base,geometry,wk in (
    (82,None,32),(76,None,32),(75,None,32),
    (79,(16,64,512,16,16,3),None),(80,(16,64,512,16,16,3),None),
    (110,(16,64,512,16,16,2),None),(111,(16,64,512,16,16,2),None),
    (79,None,32),(80,None,32),(114,None,None),(115,None,None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base] if geometry is None else geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS):
        if base in table:
            table[index]=table[base]
    if wk is not None:
        COOPERATIVE_K[index]=wk
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES):
        if base in feature:
            feature.add(index)
CHUNK_REDUCTION.update({116,117})

GLOBAL_SLICES = {}
for base,slices,geometry,wk in (
    (99,2,None,None),(100,2,None,None),(87,2,None,None),(88,2,None,None),
    (101,2,None,None),(102,2,None,None),(106,2,None,None),(105,2,None,None),
    (100,1,(16,128,512,16,32,2),128),(126,2,None,None),
    (99,1,(16,128,512,16,32,2),128),(128,2,None,None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base] if geometry is None else geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS):
        if base in table:
            table[index]=table[base]
    if wk is not None:
        COOPERATIVE_K[index]=wk
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES):
        if base in feature:
            feature.add(index)
    GLOBAL_SLICES[index]=slices

FUSED_STORE_WARPS = {}
PERSISTENT_MN = set()
for base,store_warps,persistent,specialization in (
    (118,1,False,None),(119,1,False,None),(120,1,False,None),
    (121,1,False,None),(127,1,False,None),(129,1,False,None),
    (103,0,True,None),(103,0,False,(2048,3072)),(137,0,True,None),
    (103,0,False,(1024,3072)),(139,0,True,None),(104,0,True,None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES):
        if base in table:
            table[index]=table[base]
    if specialization is not None:
        SPECIALIZATIONS[index]=specialization
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES):
        if base in feature:
            feature.add(index)
    FUSED_STORE_WARPS[index]=store_warps
    if persistent:
        PERSISTENT_MN.add(index)

MMA_M8 = {}
for mode in (1,2):
    index=len(CONFIGS)
    base=99
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN):
        if base in feature:
            feature.add(index)
    MMA_M8[index]=mode

REGISTER_PREFETCH = set()
for base,prefetch in (
    (101,False),(144,True),(99,True),(100,True),(102,True),
    (137,True),(139,True),(141,True),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN):
        if base in feature:
            feature.add(index)
    CHUNK_A.add(index)
    if prefetch:
        REGISTER_PREFETCH.add(index)

PAIRED_SCALES = set()
for base in (99,100,101,102,137,139,141):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH):
        if base in feature:
            feature.add(index)
    PAIRED_SCALES.add(index)

FULL_REGISTER_PIPELINE = set()
for base in (99,100,101,102,137,139,141,103):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES):
        if base in feature:
            feature.add(index)
    FULL_REGISTER_PIPELINE.add(index)

for base,geometry,paired in (
    (152,(8,64,512,8,32,3),None),
    (167,(8,32,512,8,32,3),None),
    (168,(8,32,512,8,16,3),None),
    (99,(8,64,512,8,32,3),None),
    (152,(16,32,512,16,32,3),None),
    (171,(16,32,512,16,16,3),None),
    (163,None,True),(164,None,True),
    (154,(64,32,256,64,32,3),None),
    (155,(64,64,256,64,32,2),None),
    (176,(64,32,256,64,32,2),None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base] if geometry is None else geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE):
        if base in feature:
            feature.add(index)
    if paired:
        PAIRED_SCALES.add(index)

GRID_MULTIPLE = {}
VECTOR_OUTPUT = set()
DIRECT_OUTPUT = set()
_output_candidates = [
    (base,grid,minimum,False,False)
    for base in (152,153)
    for grid,minimum in ((1,1),(40,1),(40,2))
]
_output_candidates += [
    (base,None,None,True,direct)
    for direct in (False,True)
    for base in (152,153,154,155,156,157,169)
]
_output_candidates += [(173,None,None,True,False),(174,None,None,True,False)]
for base,grid,minimum,vector,direct in _output_candidates:
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE):
        if base in feature:
            feature.add(index)
    if grid is not None:
        DRIVER_OPTIONS[index]=(1,1)
        GRID_MULTIPLE[index]=grid
        MIN_BLOCKS[index]=minimum
    if vector:
        VECTOR_OUTPUT.add(index)
    if direct:
        DIRECT_OUTPUT.add(index)

UNROLL_CYCLES = set()
_warp_candidates = [
    (base,stage,wk,unroll,chunk,None,False)
    for base in (152,153)
    for stage,wk,unroll,chunk in (
        (2,None,False,False),(4,None,False,False),(None,32,False,False),
        (None,None,True,False),(None,None,False,True),
    )
]
_warp_candidates += [(154,None,None,True,True,None,False),(155,None,None,True,True,None,False)]
_warp_candidates += [
    (base,None,None,False,chunk,64,full)
    for base in (156,157)
    for chunk,full in ((False,False),(True,False),(True,True))
]
for base,stage,wk,unroll,chunk,wm,full in _warp_candidates:
    index=len(CONFIGS)
    tm,tn,tk,old_wm,wn,old_stage=CONFIGS[base]
    CONFIGS += ((tm,tn,tk,wm or old_wm,wn,stage or old_stage),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT):
        if base in feature:
            feature.add(index)
    if wk:
        COOPERATIVE_K[index]=wk
    if chunk:
        CHUNK_REDUCTION.add(index)
    if unroll:
        UNROLL_CYCLES.add(index)

    if full:
        FULL_REGISTER_PIPELINE.add(index)

COMPILER_FENCE = {}
OPAQUE_COORDINATES = set()
for base in (210,211,213,216):
    variants=[(2,False,None),(0,True,None),(2,True,None),(0,False,2)]
    if base in CHUNK_A:
        variants.append((1,False,None))
    for fence,opaque,minimum in variants:
        index=len(CONFIGS)
        CONFIGS += (CONFIGS[base],)
        for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE):
            if base in table:
                table[index]=table[base]
        for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES):
            if base in feature:
                feature.add(index)
        if fence:
            COMPILER_FENCE[index]=fence
        if opaque:
            OPAQUE_COORDINATES.add(index)
        if minimum:
            MIN_BLOCKS[index]=minimum

SHARED_B = set()
for base in (156,157):
    for tm in (128,256):
        for stages in (2,3):
            for shared in (False,True):
                index=len(CONFIGS)
                CONFIGS += ((tm,128,64,64,32,stages),)
                for table in (DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE):
                    if base in table:
                        table[index]=table[base]
                for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES):
                    if base in feature:
                        feature.add(index)
                COOPERATIVE_K[index]=64
                if shared:
                    SHARED_B.add(index)

UNSIGNED_INDICES = set()
for base in (200,205,210,211,173,174,237,238,241,242,245,246,249,250):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B):
        if base in feature:
            feature.add(index)
    UNSIGNED_INDICES.add(index)

for base in (253,254):
    variants=(
        ((16,64,512,16,32,1),64,False,False,False),
        ((16,64,1536,16,32,1),192,False,False,False),
        ((16,64,3072,16,32,1),384,False,False,False),
        ((16,64,3072,16,32,1),192,False,False,False),
        ((16,64,3072,16,32,1),192,True,False,False),
        ((8,64,3072,8,32,1),384,False,False,False),
        ((16,32,512,16,16,2),64,False,False,False),
        ((8,32,512,8,16,2),64,False,False,False),
        (CONFIGS[base],64,False,True,False),
        (CONFIGS[base],64,False,False,True),
    )
    for geometry,wk,tree,prefetch,full in variants:
        index=len(CONFIGS)
        CONFIGS += (geometry,)
        for table in (DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
            if base in table:
                table[index]=table[base]
        for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES):
            if base in feature:
                feature.add(index)
        COOPERATIVE_K[index]=wk
        if tree:
            CHUNK_REDUCTION.add(index)
        if prefetch:
            REGISTER_PREFETCH.add(index)
        if full:
            FULL_REGISTER_PIPELINE.add(index)

INTERLEAVED_A = set()
for base in (173,174,257,258):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES):
        if base in feature:
            feature.add(index)
    INTERLEAVED_A.add(index)

STREAM_K_WORKERS = {}
for base,workers in ((253,32),(254,40),(156,40),(157,40),(173,40),(174,40),(289,40),(290,40)):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A):
        if base in feature:
            feature.add(index)
    STREAM_K_WORKERS[index]=workers

for base,tm,stage in (
    (173,112,3),(174,112,3),(156,112,3),(157,112,3),(289,112,3),(290,112,3),
    (289,80,3),(290,80,3),(289,80,2),(290,80,2),(173,96,3),(174,96,3),
):
    index=len(CONFIGS)
    _,tn,tk,_,wn,_=CONFIGS[base]
    CONFIGS += ((tm,tn,tk,tm,wn,stage),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A):
        if base in feature:
            feature.add(index)

N_FAST_RASTER = set()
for persistent,n_fast in ((False,True),(True,False),(True,True)):
    for base in (173,174,303,304):
        index=len(CONFIGS)
        CONFIGS += (CONFIGS[base],)
        for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
            if base in table:
                table[index]=table[base]
        for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A):
            if base in feature:
                feature.add(index)
        if persistent:
            PERSISTENT_MN.add(index)
        if n_fast:
            N_FAST_RASTER.add(index)

STATIC_M = {}
PRUNE_ROWS = set()
for base in (253,254):
    for m in (1,12):
        for prune,direct in ((False,False),(True,False),(True,True)):
            index=len(CONFIGS)
            CONFIGS += (CONFIGS[base],)
            for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
                if base in table:
                    table[index]=table[base]
            for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER):
                if base in feature:
                    feature.add(index)
            STATIC_M[index]=m
            if prune:
                PRUNE_ROWS.add(index)
            if direct:
                DIRECT_OUTPUT.add(index)

TAIL_M8 = set()
for base in (303,304,321,322):
    index=len(CONFIGS)
    _,tn,tk,_,wn,stages=CONFIGS[base]
    CONFIGS += ((104,tn,tk,104,wn,stages),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER):
        if base in feature:
            feature.add(index)
    TAIL_M8.add(index)

for base,wk,tn in (
    (323,128,64),(323,256,64),(326,128,64),(326,256,64),
    (329,128,64),(329,256,64),(332,128,64),(332,256,64),
    (339,128,128),(341,128,128),(343,128,128),(345,128,128),
    (323,64,128),(326,64,128),(329,64,128),(332,64,128),
):
    index=len(CONFIGS)
    tm,_,tk,wm,wn,stages=CONFIGS[base]
    CONFIGS += ((tm,tn,tk,wm,wn,stages),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8):
        if base in feature:
            feature.add(index)
    COOPERATIVE_K[index]=wk

for base in (303,321,337):
    for direct in (False,True):
        index=len(CONFIGS)
        CONFIGS += (CONFIGS[base],)
        for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M):
            if base in table:
                table[index]=table[base]
        for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8):
            if base in feature:
                feature.add(index)
        (DIRECT_OUTPUT if direct else VECTOR_OUTPUT).add(index)

for base,tm,tk,stages in (
    (323,16,1024,2),(326,16,1024,2),(329,16,1024,2),(332,16,1024,2),
    (361,16,1024,1),(362,16,1024,1),(363,16,1024,1),(364,16,1024,1),
    (365,8,1024,1),(366,8,1024,1),(367,8,1024,1),(368,8,1024,1),
    (361,16,1024,3),(362,16,1024,3),(363,16,1024,3),(364,16,1024,3),
):
    index=len(CONFIGS)
    _,tn,_,_,wn,_=CONFIGS[base]
    CONFIGS += ((tm,tn,tk,tm,wn,stages),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8):
        if base in feature:
            feature.add(index)

CACHE_SCALES = set()
for base in (323,326,349,350,359,303):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8):
        if base in feature:
            feature.add(index)
    CACHE_SCALES.add(index)

COMPACT_OUTPUT = {}
for base,mode in (
    (349,0),(350,0),(324,1),(327,1),(383,1),(384,1),
    (385,2),(386,2),(387,2),(388,2),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES):
        if base in feature:
            feature.add(index)
    PRUNE_ROWS.add(index)
    if mode:
        COMPACT_OUTPUT[index]=mode
    if mode==2:
        DIRECT_OUTPUT.add(index)

for mode in ("static_m","unroll","k64"):
    base=359
    index=len(CONFIGS)
    tm,tn,tk,wm,wn,stages=CONFIGS[base]
    CONFIGS += ((tm,tn,64 if mode=="k64" else tk,wm,wn,stages),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES):
        if base in feature:
            feature.add(index)
    if mode=="static_m":
        STATIC_M[index]=512
    elif mode=="unroll":
        UNROLL_CYCLES.add(index)

for base,ordinary in ((395,False),(396,True)):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES):
        if base in feature:
            feature.add(index)
    GRID_MULTIPLE[index]=80
    if ordinary:
        PERSISTENT_MN.remove(index)
        DRIVER_OPTIONS[index]=(1,1)

for base,static_m,unroll in (
    (323,1,True),(326,12,True),(329,1,True),(332,12,True),
    (349,1,True),(350,12,True),(326,16,False),(350,16,False),
    (404,16,True),(405,16,True),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES):
        if base in feature:
            feature.add(index)
    STATIC_M[index]=static_m
    if unroll:
        UNROLL_CYCLES.add(index)

SKIP_STAGE2_BARRIER = set()
for base,skip_barrier in (
    (398,False),(399,False),(406,False),(349,False),(350,False),(405,False),
    (408,True),(409,True),(410,True),(411,True),(412,True),(413,True),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES):
        if base in feature:
            feature.add(index)
    FULL_REGISTER_PIPELINE.add(index)
    if skip_barrier:
        SKIP_STAGE2_BARRIER.add(index)

REDUCTION_STORAGE = {}
for base,mode in (
    (398,1),(399,1),(406,1),(349,1),(350,1),(405,1),
    (420,2),(421,2),(422,2),(423,2),(424,2),(425,2),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    REDUCTION_STORAGE[index]=mode

DIRECT_A = {}
for base,mode in (
    (398,1),(399,1),(406,1),(349,1),(350,1),(405,1),
    (432,2),(433,2),(434,2),(435,2),(436,2),(437,2),
    (438,3),(439,3),(440,3),(441,3),(442,3),(443,3),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    DIRECT_A[index]=mode

for base,readonly in (
    (398,False),(399,False),(406,False),(349,False),(350,False),(405,False),
    (444,True),(445,True),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    if readonly:
        DIRECT_A[index]=4
    else:
        NATIVE_A.remove(index)

for base in (398,399,406,349,350,405,400,401):
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    geometry[4]=16
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)

for base in (398,399,349,350):
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    geometry[0]=geometry[3]=8
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)

for base in (349,350,405,461,462,463):
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    geometry[2]=1024
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    if geometry[4]==16:
        COOPERATIVE_K[index]=256

COHORT_PIPELINE = {}
for base,mode in ((349,1),(350,1),(405,1),(476,2),(477,2),(478,2)):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    COHORT_PIPELINE[index]=mode

for base,stages in (
    (349,3),(350,3),(405,3),(400,3),(401,3),(464,3),(465,3),
    (349,4),(350,4),(405,4),
):
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    geometry[5]=stages
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)

for base,mode in (
    (468,1),(350,1),(405,1),
    (468,2),(350,2),(405,2),
    (468,3),(350,3),(405,3),
    (498,4),(499,4),(500,4),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    if mode==1:
        VECTOR_OUTPUT.add(index)
    elif mode==2:
        DIRECT_OUTPUT.add(index)
    else:
        DRIVER_OPTIONS[index]=(1,1)
        N_FAST_RASTER.add(index)
        GRID_MULTIPLE[index]=1 if mode==3 else 40

for base,mode in ((468,3),(350,3),(405,3),(504,4),(505,4),(506,4)):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    COHORT_PIPELINE[index]=mode

WARP_ORDER = {}
for mode in (1,2,3):
    for base in (468,350,405):
        index=len(CONFIGS)
        CONFIGS += (CONFIGS[base],)
        for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE):
            if base in table:
                table[index]=table[base]
        for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
            if base in feature:
                feature.add(index)
        WARP_ORDER[index]=mode

B_PRODUCER_WARP = {}
for producer in (8,10,14):
    base=350
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    B_PRODUCER_WARP[index]=producer

for base,change,value in (
    (345,"wn",16),(522,"tn",32),(523,"tk",256),
    (524,"wk",64),(522,"unroll",1),(522,"wk",256),
):
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    if change in ("tn","tk","wn"):
        geometry[{"tn":1,"tk":2,"wn":4}[change]]=value
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    if change=="wk":
        COOPERATIVE_K[index]=value
    elif change=="unroll":
        UNROLL_CYCLES.add(index)

for change in ("a_first","prefetch","scales","direct","producer","m1","m16"):
    base=526
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    if change=="m1":
        geometry[0]=geometry[3]=8
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    if change=="a_first":
        CHUNK_A.discard(index)
    elif change=="prefetch":
        REGISTER_PREFETCH.add(index)
    elif change=="scales":
        CACHE_SCALES.add(index)
    elif change=="direct":
        DIRECT_OUTPUT.add(index)
    elif change=="producer":
        B_PRODUCER_WARP[index]=8
    elif change=="m1":
        STATIC_M[index]=1
    else:
        STATIC_M[index]=16

for base,change in (
    (533,"direct"),(534,"direct"),(531,"a_first"),(531,"scales"),
    (531,"prefetch"),(531,"prune"),(535,"prune"),
    (531,"disjoint"),(535,"disjoint"),(536,"disjoint"),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER):
        if base in feature:
            feature.add(index)
    if change=="direct":
        DIRECT_OUTPUT.add(index)
    elif change=="a_first":
        CHUNK_A.discard(index)
    elif change=="scales":
        CACHE_SCALES.add(index)
    elif change=="prefetch":
        REGISTER_PREFETCH.add(index)
    elif change=="prune":
        PRUNE_ROWS.add(index)
    else:
        REDUCTION_STORAGE[index]=2

PREFETCH_REDUCTION = set()
for base,change in ((531,"prefetch"),(531,"wm8"),(546,"tk256"),(547,"wk64")):
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    if change=="wm8":
        geometry[3]=8
    elif change=="tk256":
        geometry[2]=256
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="prefetch":
        PREFETCH_REDUCTION.add(index)
    elif change=="wk64":
        COOPERATIVE_K[index]=64

GROUP_OUTPUT_STORES = set()
for base in (531,545):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION):
        if base in feature:
            feature.add(index)
    GROUP_OUTPUT_STORES.add(index)

INTEGER_ZERO = set()
for base in (550,535,536,550):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES):
        if base in feature:
            feature.add(index)
    INTEGER_ZERO.add(index)
    if index==554:
        STATIC_M.pop(index)
        SPECIALIZATIONS[index]=(0,3072)

ZERO_WORD_LOAD = set()
for base in (551,552,553,554):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO):
        if base in feature:
            feature.add(index)
    ZERO_WORD_LOAD.add(index)

SINGLE_ZERO_BIAS = set()
for base in (551,555,552,553,554):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD):
        if base in feature:
            feature.add(index)
    SINGLE_ZERO_BIAS.add(index)

INTERLEAVE_ZERO_GROUPS = set()
for base,word_load in ((559,False),(560,False),(561,False),(562,False),
                       (563,False),(563,True),(561,True),(562,True)):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if word_load:
        ZERO_WORD_LOAD.add(index)
    INTERLEAVE_ZERO_GROUPS.add(index)

PAIRED_ZERO_BIAS = set()
for base in (564,566,567,568):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS):
        if base in feature:
            feature.add(index)
    PAIRED_ZERO_BIAS.add(index)

# A5: pipeline depth on the validated asymmetric readers, then native
# integer-zero versions of the other symmetric anchor geometries.
for base,stages,nk in (
    (564,3,None),(566,3,None),(567,3,None),
    (458,0,None),(459,0,None),(460,0,None),
    (255,0,None),(256,0,None),(336,0,None),(396,0,None),
    (74,0,(3072,1024)),(151,0,(3072,1024)),(568,0,(3072,1024)),
):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    CONFIGS += (geometry[:5]+(stages or geometry[5],),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    INTEGER_ZERO.add(index)
    PAIRED_SCALES.add(index)
    SINGLE_ZERO_BIAS.add(index)
    if geometry[2]%128==0:
        INTERLEAVE_ZERO_GROUPS.add(index)
    if nk is not None:
        SPECIALIZATIONS[index]=nk

for base,change in (
    (585,"zero_pairs"),(579,"m8"),(580,"direct_output"),(581,"direct_output"),
    (564,"prefetch"),(566,"prefetch"),(567,"prefetch"),
    (564,"warp32"),(566,"warp32"),(567,"warp32"),
    (564,"pipeline"),(566,"pipeline"),(567,"pipeline"),
    (591,"group_output"),(592,"group_output"),
):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    if change=="m8":
        geometry=(8,*geometry[1:3],8,*geometry[4:])
    elif change=="warp32":
        geometry=(*geometry[:4],32,geometry[5])
    CONFIGS += (geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if change=="zero_pairs":
        INTERLEAVE_ZERO_GROUPS.add(index)
    elif change=="m8":
        MMA_M8[index]=2
    elif change=="group_output":
        GROUP_OUTPUT_STORES.add(index)
    elif change=="direct_output":
        DIRECT_OUTPUT.add(index)
    elif change=="prefetch":
        REGISTER_PREFETCH.add(index)
    elif change=="pipeline":
        FULL_REGISTER_PIPELINE.add(index)
    elif change=="warp32":
        COOPERATIVE_K[index]=64

for base,change in (
    (593,"word"),(594,"word"),(595,"word"),(597,"stage3"),
    (596,"bounded"),(598,"bounded"),
    (585,"m112"),(585,"m120"),(585,"m128"),
    (608,"stage3"),(609,"stage3"),
):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    if change=="stage3":
        geometry=(*geometry[:5],3)
    elif change.startswith("m"):
        rows=int(change[1:])
        geometry=(rows,*geometry[1:3],rows,*geometry[4:])
    CONFIGS += (geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if change=="word":
        ZERO_WORD_LOAD.add(index)
    elif change=="bounded":
        BOUNDED_REDUCTION.add(index)
        PREFETCH_REDUCTION.discard(index)
    if change.startswith("m") and geometry[3]%16==0:
        TAIL_M8.discard(index)

# Bounded generic fallbacks for the public selector. Exact measured shapes
# retain their specialized configurations; these rows need separate admission.
for base,small in ((460,True),(535,True),(255,False),
                   (568,True),(566,True),(582,False),(587,False)):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    if small:
        geometry=(*geometry[:2],256,*geometry[3:])
    CONFIGS += (geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    SPECIALIZATIONS[index]=(0,0)
    STATIC_M.pop(index,None)
    if small:
        COOPERATIVE_K[index]=64

for base,change in ((585,"unroll"),(394,"integer_zero"),
                    (593,"paired_bias"),(594,"paired_bias"),(595,"paired_bias")):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if change=="unroll":
        UNROLL_CYCLES.add(index)
    elif change=="integer_zero":
        INTEGER_ZERO.add(index)
        PAIRED_SCALES.add(index)
        SINGLE_ZERO_BIAS.add(index)
        INTERLEAVE_ZERO_GROUPS.add(index)
    else:
        PAIRED_ZERO_BIAS.add(index)

for base,change in ((458,"m8"),(597,"prefetch"),(628,"paired_bias"),
                    (629,"word"),(624,"mma8"),(626,"mma8"),
                    (622,"grid2d"),(622,"flat"),(622,"m512")):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    if change=="m8":
        geometry=(8,*geometry[1:3],8,*geometry[4:])
    CONFIGS += (geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if change=="prefetch":
        REGISTER_PREFETCH.add(index)
    elif change=="paired_bias":
        PAIRED_ZERO_BIAS.add(index)
    elif change=="word":
        ZERO_WORD_LOAD.add(index)
    elif change=="mma8":
        MMA_M8[index]=2
    elif change in ("grid2d","flat"):
        PERSISTENT_MN.discard(index)
        DRIVER_OPTIONS[index]=(1,int(change=="flat"))
        if change=="grid2d":
            N_FAST_RASTER.discard(index)
    elif change=="m512":
        STATIC_M[index]=512

ZERO_BIAS_CACHE=set()
for base,change in ((625,"zero"),(624,"zero"),(626,"zero"),(634,"zero"),(575,"zero"),
                    (636,"scale"),(637,"scale"),(638,"scale"),(640,"scale")):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE):
        if base in feature:
            feature.add(index)
    if change=="zero":
        ZERO_BIAS_CACHE.add(index)
    else:
        CACHE_SCALES.add(index)

for base,change in ((625,"bounds"),(625,"m12"),(625,"m16"),(646,"bounds"),
                    (647,"bounds"),(624,"bounds"),(626,"bounds")):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE):
        if base in feature:
            feature.add(index)
    if change=="bounds":
        MIN_BLOCKS[index]=4
    else:
        STATIC_M[index]=int(change[1:])

for base,change in ((645,"n1024"),(590,"wn32"),(653,"direct"),(590,"paired"),
                    (590,"prune"),(645,"prune"),(624,"prune"),
                    (645,"flat40"),(624,"flat40"),(626,"flat40"),
                    (659,"grid32"),(660,"grid32"),(661,"grid32")):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    if change=="wn32":
        geometry=(*geometry[:4],32,geometry[5])
    CONFIGS += (geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE):
        if base in feature:
            feature.add(index)
    if change=="n1024":
        SPECIALIZATIONS[index]=(1024,3072)
    elif change=="direct":
        DIRECT_OUTPUT.add(index)
    elif change=="paired":
        PAIRED_ZERO_BIAS.add(index)
    elif change=="prune":
        PRUNE_ROWS.add(index)
    elif change=="flat40":
        DRIVER_OPTIONS[index]=(1,1)
        N_FAST_RASTER.add(index)
        GRID_MULTIPLE[index]=40
    elif change=="grid32":
        GRID_MULTIPLE[index]=32

PERMUTE_ZERO_BIAS = set()
for base,permuted in ((624,False),(645,False),(626,False),
                      (665,True),(666,True),(667,True),(569,True)):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE):
        if base in feature:
            feature.add(index)
    ZERO_WORD_LOAD.add(index)
    if permuted:
        PERMUTE_ZERO_BIAS.add(index)

for base,change in ((655,"permute"),(602,"paired"),(603,"paired"),
                    (673,"permute"),(674,"permute"),
                    (668,"ungroup"),(670,"group"),
                    (668,"serial"),(670,"prefetch"),
                    (668,"disjoint"),(670,"disjoint"),(672,"generic")):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if change=="permute":
        ZERO_WORD_LOAD.add(index)
        PERMUTE_ZERO_BIAS.add(index)
    elif change=="paired":
        PAIRED_ZERO_BIAS.add(index)
    elif change=="ungroup":
        GROUP_OUTPUT_STORES.discard(index)
    elif change=="group":
        GROUP_OUTPUT_STORES.add(index)
    elif change=="serial":
        PREFETCH_REDUCTION.discard(index)
    elif change=="prefetch":
        PREFETCH_REDUCTION.add(index)
    elif change=="disjoint":
        REDUCTION_STORAGE[index]=2
    elif change=="generic":
        STATIC_M[index]=0

# Extend existing large-M bodies to the new N512 validation cohort.
for base,change in ((582,"specialize"),(583,"specialize"),(584,"specialize"),
                    (634,"specialize"),(621,"flat"),
                    (688,"n64k32"),(689,"stage3"),(688,"n256k64"),
                    (691,"pipeline"),(689,"m64"),(690,"m64"),
                    (621,"specialize"),(695,"unroll"),(695,"pipeline")):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    if change=="n64k32":
        geometry=(geometry[0],64,*geometry[2:])
    elif change=="stage3":
        geometry=(*geometry[:5],3)
    elif change=="n256k64":
        geometry=(geometry[0],256,64,geometry[3],geometry[4],3)
    elif change=="m64":
        geometry=(64,geometry[1],geometry[2],64,geometry[4],geometry[5])
    CONFIGS += (geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    SPECIALIZATIONS[index]=(512,3072)
    STATIC_M[index]=0
    if change=="flat":
        PERSISTENT_MN.discard(index)
    elif change=="n64k32":
        COOPERATIVE_K[index]=32
    elif change=="pipeline":
        REGISTER_PREFETCH.add(index)
        FULL_REGISTER_PIPELINE.add(index)
    elif change=="unroll":
        UNROLL_CYCLES.add(index)

# Full-M continuation: retain the proven readers and vary one geometry or
# pipeline property at a time. These candidates are not default selection.
for base,n,change in (
    (655,1024,"dynamic_m"), (583,1024,"specialize"), (634,1024,"specialize"),
    (582,1024,"m32"), (701,1024,"stage3"),
    (582,1024,"m48"), (703,1024,"stage3"),
    (701,1024,"wn16"), (703,1024,"wn16"),
    (705,1024,"wk64"), (706,1024,"wk64"),
    (686,512,"m128"), (709,512,"cache_scales"),
    (686,512,"m112"), (686,512,"m96"),
    (688,512,"tk256"), (713,512,"stage3"),
    (688,512,"wn16"), (688,512,"wm64"),
    (687,512,"m128"), (717,512,"cache_scales"),
    (687,512,"n256"), (717,512,"n256"), (719,512,"persistent"),
    (686,512,"wk32"), (688,512,"wk32"), (709,512,"wk32"),
):
    index=len(CONFIGS)
    geometry=CONFIGS[base]
    if change in ("m32","m48","m96","m112","m128"):
        rows=int(change[1:])
        geometry=(rows,geometry[1],geometry[2],rows,geometry[4],geometry[5])
    elif change=="stage3":
        geometry=(*geometry[:5],3)
    elif change=="wn16":
        geometry=(*geometry[:4],16,geometry[5])
    elif change=="wm64":
        geometry=(*geometry[:3],64,*geometry[4:])
    elif change=="tk256":
        geometry=(*geometry[:2],256,*geometry[3:])
    elif change=="n256":
        geometry=(geometry[0],256,*geometry[2:])
    CONFIGS += (geometry,)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    SPECIALIZATIONS[index]=(n,3072)
    STATIC_M[index]=0
    if geometry[3]%16==0:
        TAIL_M8.discard(index)
    if change=="wk64":
        COOPERATIVE_K[index]=64
    elif change=="wk32":
        COOPERATIVE_K[index]=32
    elif change=="cache_scales":
        CACHE_SCALES.add(index)
    elif change=="persistent":
        PERSISTENT_MN.add(index)

# A17 keeps the A16 numeric winners and screens larger-M reuse without spills.
for base,change,value in (
    (707,"static_m",24), (707,"static_m",32),
    (707,"stages",3), (708,"stages",3),
    (669,"nk",(1024,3072)), (669,"static_m",0),
    (707,"nk",(2048,3072)), (708,"nk",(2048,3072)),
    (717,"loop",0), (720,"loop",0),
    (733,"stages",2), (734,"stages",2),
    (715,"pipeline",0), (737,"interleave_a",0),
    (715,"tk",64), (739,"pipeline",0),
    (740,"interleave_a",0), (741,"stages",3),
    (709,"direct_output",0),
    (733,"wn",16), (744,"tn",256),
    (733,"nk",(0,0)), (734,"nk",(0,0)),
    (741,"nk",(0,0)), (742,"nk",(0,0)),
    (687,"nk",(0,0)), (699,"nk",(0,0)),
    (655,"nk",(16384,3072)), (602,"nk",(16384,3072)),
    (603,"nk",(16384,3072)), (683,"nk",(16384,3072)),
    (669,"nk",(16384,3072)),
    (683,"nk",(8192,8192)), (668,"nk",(8192,8192)),
    (670,"nk",(8192,8192)), (669,"nk",(8192,8192)),
    (731,"nk",(16384,3072)), (732,"nk",(16384,3072)),
    (731,"nk",(8192,8192)), (732,"nk",(8192,8192)),
):
    index=len(CONFIGS)
    geometry=list(CONFIGS[base])
    if change in ("tn","tk","wn","stages"):
        geometry[{"tn":1,"tk":2,"wn":4,"stages":5}[change]]=value
    CONFIGS += (tuple(geometry),)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="loop":
        UNROLL_CYCLES.discard(index)
    elif change=="pipeline":
        REGISTER_PREFETCH.add(index)
        FULL_REGISTER_PIPELINE.add(index)
    elif change=="interleave_a":
        INTERLEAVED_A.add(index)
    elif change=="direct_output":
        DIRECT_OUTPUT.add(index)

# A18 trades metadata bandwidth for fewer bias/address instructions in run.
PREPARED_ZERO_BIAS = set()
for base,change in (
    (655,"prepare"), (668,"prepare"), (670,"prepare"), (729,"prepare"),
    (707,"prepare"), (708,"prepare"), (700,"prepare"), (683,"prepare"),
    (766,"generic"), (765,"cached"), (766,"cached"), (771,"cached"),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (COOPERATIVE_K,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    PREPARED_ZERO_BIAS.add(index)
    ZERO_WORD_LOAD.discard(index)
    PERMUTE_ZERO_BIAS.discard(index)
    INTERLEAVE_ZERO_GROUPS.discard(index)
    if change=="generic":
        STATIC_M[index]=0
    elif change=="cached":
        CACHE_SCALES.add(index)
        ZERO_BIAS_CACHE.add(index)

# A19: preserve the native data/fragment contract while extending A18's gains.
for base,change,value in (
    (717,"prepare",0), (720,"prepare",0),
    (777,"nk",(1024,3072)), (778,"nk",(1024,3072)),
    (777,"nk",(0,3072)), (778,"nk",(0,3072)),
    (765,"producer",8), (775,"producer",8),
    (668,"nk",(16384,3072)), (670,"nk",(16384,3072)),
    (766,"nk",(16384,3072)), (767,"nk",(16384,3072)),
    (768,"nk",(8192,8192)), (765,"nk",(8192,8192)),
    (689,"m",112), (690,"m",112),
    (689,"prepare",0), (791,"prepare",0),
    (690,"prepare",0), (792,"prepare",0),
    (771,"direct_output",0), (777,"direct_output",0),
    (669,"static_m",2), (669,"static_m",4),
    (669,"static_m",6), (669,"static_m",8),
    (799,"nk",(16384,3072)), (800,"nk",(16384,3072)),
    (801,"nk",(16384,3072)), (802,"nk",(16384,3072)),
    (760,"static_m",2), (760,"static_m",4),
    (760,"static_m",6), (760,"static_m",8),
    (689,"unsigned",0), (811,"vector_output",0),
    (812,"pipeline",0), (813,"interleave_a",0),
    (814,"unroll",0), (815,"prepare",0), (816,"stages",3),
    (816,"m",112), (818,"stages",3),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="m":
        geometry[0]=geometry[3]=value
    elif change=="stages":
        geometry[5]=value
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS):
        if base in feature:
            feature.add(index)
    if change=="prepare":
        PREPARED_ZERO_BIAS.add(index)
        ZERO_WORD_LOAD.discard(index)
        PERMUTE_ZERO_BIAS.discard(index)
        INTERLEAVE_ZERO_GROUPS.discard(index)
    elif change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="producer":
        B_PRODUCER_WARP[index]=value
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="direct_output":
        DIRECT_OUTPUT.add(index)
    elif change=="unsigned":
        UNSIGNED_INDICES.add(index)
    elif change=="vector_output":
        VECTOR_OUTPUT.add(index)

    elif change=="pipeline":
        FULL_REGISTER_PIPELINE.add(index)
    elif change=="interleave_a":
        INTERLEAVED_A.add(index)
    elif change=="unroll":
        UNROLL_CYCLES.add(index)
    if change=="m" and value%16==0:
        TAIL_M8.discard(index)

# A20: four byte-sized integer zeros per word, two groups per column pair.
BYTE_ZERO_WORDS = set()
for base,change,value in (
    (655,"format",0), (668,"format",0), (670,"format",0), (729,"format",0),
    (707,"format",0), (708,"format",0), (700,"format",0), (683,"format",0),
    (821,"static_m",0), (820,"producer",8),
    (821,"cached",0), (826,"cached",0),
    (817,"format",0), (819,"format",0),
    (820,"nk",(2048,3072)), (821,"nk",(16384,3072)),
    (822,"nk",(16384,3072)), (823,"nk",(8192,8192)),
    (820,"static_m",8), (823,"static_m",8),
    (839,"nk",(16384,3072)), (839,"nk",(8192,8192)),
    (839,"nk",(2048,3072)), (820,"nk",(0,3072)),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS):
        if base in feature:
            feature.add(index)
    BYTE_ZERO_WORDS.add(index)
    PREPARED_ZERO_BIAS.discard(index)
    PERMUTE_ZERO_BIAS.discard(index)
    INTERLEAVE_ZERO_GROUPS.discard(index)
    ZERO_WORD_LOAD.add(index)
    if change=="static_m":
        STATIC_M[index]=value
    elif change=="producer":
        B_PRODUCER_WARP[index]=value
    elif change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="cached":
        CACHE_SCALES.add(index)
        ZERO_BIAS_CACHE.add(index)

# A21: first close all remaining losses, starting with large-M/wide-N gaps.
assert len(CONFIGS)==844
for base,change,value in (
    (776,"m",112), (776,"m",96), (844,"tn",256),
    (845,"tn",256), (776,"tn",256),
    (583,"nk",(16384,3072)), (849,"m",48),
    (849,"tk",128), (851,"wk",32), (852,"stages",3),
    (582,"nk",(16384,3072)), (582,"nk",(8192,8192)),
    (583,"nk",(8192,8192)), (849,"m",32),
    (856,"m",48), (856,"m",32),
    (776,"nk",(2048,3072)), (844,"nk",(2048,3072)),
    (846,"nk",(2048,3072)), (776,"nk",(16384,3072)),
    (844,"nk",(16384,3072)), (846,"nk",(16384,3072)),
    (776,"nk",(3072,1024)), (844,"nk",(3072,1024)),
    (846,"nk",(3072,1024)), (776,"nk",(3072,8192)),
    (844,"nk",(3072,8192)), (846,"nk",(3072,8192)),
    (776,"nk",(8192,8192)), (844,"nk",(8192,8192)),
    (846,"nk",(8192,8192)), (845,"nk",(16384,3072)),
    (847,"nk",(16384,3072)), (845,"nk",(3072,1024)),
    (847,"nk",(3072,1024)), (845,"nk",(3072,8192)),
    (847,"nk",(3072,8192)), (845,"nk",(8192,8192)),
    (847,"nk",(8192,8192)),
    (715,"nk",(1024,3072)), (715,"nk",(2048,3072)),
    (716,"nk",(1024,3072)), (716,"nk",(2048,3072)),
    (716,"tk",64), (887,"stages",3),
    (888,"nk",(1024,3072)), (888,"nk",(2048,3072)),
    (888,"nk",(16384,3072)), (888,"nk",(3072,1024)),
    (888,"nk",(3072,8192)), (888,"nk",(8192,8192)),
    (888,"prepare",0), (895,"unsigned",0),
    (896,"pipeline",0), (897,"interleave_a",0),
    (898,"unroll",0), (899,"nk",(1024,3072)),
    (899,"nk",(2048,3072)), (899,"nk",(16384,3072)),
    (899,"nk",(3072,1024)), (899,"nk",(3072,8192)),
    (899,"nk",(8192,8192)),
    (810,"min_blocks",1), (806,"min_blocks",1), (802,"min_blocks",1),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="m":
        geometry[0]=geometry[3]=value
    elif change in ("tn","tk","stages"):
        geometry[{"tn":1,"tk":2,"stages":5}[change]]=value
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS):
        if base in feature:
            feature.add(index)
    if change=="m":
        TAIL_M8.discard(index)
    elif change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="wk":
        COOPERATIVE_K[index]=value
    elif change=="min_blocks":
        MIN_BLOCKS[index]=value
    elif change=="prepare":
        PREPARED_ZERO_BIAS.add(index)
        BYTE_ZERO_WORDS.discard(index)
        ZERO_WORD_LOAD.discard(index)
        PERMUTE_ZERO_BIAS.discard(index)
        INTERLEAVE_ZERO_GROUPS.discard(index)
    elif change=="unsigned":
        UNSIGNED_INDICES.add(index)
    elif change=="pipeline":
        FULL_REGISTER_PIPELINE.add(index)
    elif change=="interleave_a":
        INTERLEAVED_A.add(index)
    elif change=="unroll":
        UNROLL_CYCLES.add(index)

# A22: match wide-N geometry and inspect, rather than categorically reject, stack use.
assert len(CONFIGS)==909
for base,change,value in (
    (851,"tn",256), (909,"stages",3),
    (910,"no_unroll",0), (910,"fence",1), (910,"fence",2),
    (910,"prepare",0), (914,"no_unroll",0),
    (914,"fence",1), (914,"fence",2),
    (914,"pipeline",0), (918,"interleave_a",0), (919,"no_unroll",0),
    (910,"min_blocks",2), (914,"min_blocks",2), (919,"min_blocks",2),
    (910,"m",48), (914,"m",48), (919,"m",48),
    (910,"m",32), (914,"m",32), (919,"m",32),
    (853,"nk",(8192,8192)), (930,"m",48), (930,"m",32),
    (930,"no_unroll",0), (930,"prepare",0), (934,"no_unroll",0),
    (934,"fence",1), (934,"pipeline",0),
    (937,"interleave_a",0), (938,"no_unroll",0),
    (934,"min_blocks",2), (938,"min_blocks",2),
    (934,"m",48), (938,"m",48), (934,"m",32), (938,"m",32),
    (776,"m",128), (946,"tn",256),
    (947,"nk",(16384,3072)), (947,"nk",(3072,1024)),
    (947,"nk",(3072,8192)), (947,"nk",(8192,8192)),
    (947,"nk",(2048,3072)),
    (780,"nk",(16384,3072)), (780,"nk",(3072,1024)),
    (780,"nk",(3072,8192)), (780,"nk",(8192,8192)),
    (780,"nk",(2048,3072)),
    (910,"opaque",0), (914,"opaque",0), (919,"opaque",0),
    (930,"opaque",0), (934,"opaque",0), (938,"opaque",0),
    (915,"m",48), (920,"m",48), (935,"m",48), (939,"m",48),
    (910,"vector_output",0), (914,"vector_output",0), (919,"vector_output",0),
    (930,"vector_output",0), (934,"vector_output",0), (938,"vector_output",0),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="m":
        geometry[0]=geometry[3]=value
    elif change in ("tn","stages"):
        geometry[{"tn":1,"stages":5}[change]]=value
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS):
        if base in feature:
            feature.add(index)
    if change=="m":
        TAIL_M8.discard(index)
    elif change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="min_blocks":
        MIN_BLOCKS[index]=value
    elif change=="prepare":
        PREPARED_ZERO_BIAS.add(index)
        BYTE_ZERO_WORDS.discard(index)
        ZERO_WORD_LOAD.discard(index)
        PERMUTE_ZERO_BIAS.discard(index)
        INTERLEAVE_ZERO_GROUPS.discard(index)
    elif change=="pipeline":
        FULL_REGISTER_PIPELINE.add(index)
    elif change=="interleave_a":
        INTERLEAVED_A.add(index)
    elif change=="no_unroll":
        UNROLL_CYCLES.discard(index)
    elif change=="fence":
        COMPILER_FENCE[index]=value
    elif change=="opaque":
        OPAQUE_COORDINATES.add(index)
    elif change=="vector_output":
        VECTOR_OUTPUT.add(index)

# A23: measured register cliffs in the wide-N M32/M48 bodies.
assert len(CONFIGS)==974
for base,change,value in (
    (925,"min_blocks",2), (924,"min_blocks",2), (926,"min_blocks",2),
    (964,"min_blocks",2), (965,"min_blocks",2),
    (942,"min_blocks",2), (931,"min_blocks",2), (943,"min_blocks",2),
    (966,"min_blocks",2), (967,"min_blocks",2),
    (932,"min_blocks",2), (944,"min_blocks",2), (945,"min_blocks",2),
    (925,"stages",2), (924,"stages",2),
    (987,"min_blocks",2), (988,"min_blocks",2),
    (942,"stages",2), (931,"stages",2),
    (991,"min_blocks",2), (992,"min_blocks",2),
    (925,"static_m",48), (942,"static_m",48),
    (944,"static_m",32), (944,"static_m",24),
    (995,"min_blocks",2), (996,"min_blocks",2),
    (997,"min_blocks",2), (998,"min_blocks",2),
    (987,"static_m",48), (991,"static_m",48),
    (1003,"min_blocks",2), (1004,"min_blocks",2),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="stages":
        geometry[5]=value
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS):
        if base in feature:
            feature.add(index)
    if change=="min_blocks":
        MIN_BLOCKS[index]=value
    elif change=="static_m":
        STATIC_M[index]=value

# A24: rectangle grid coverage, K64 readers, streamed partials and persistent tiles.
assert len(CONFIGS)==1007
INLINE_REDUCTION = set()
for base,change,value in (
    (715,"tn",64), (883,"tn",64), (884,"tn",64),
    (1007,"unsigned",0), (1010,"prepare",0), (1011,"inline",0),
    (1012,"nk",(1024,3072)), (1012,"nk",(2048,3072)),
    (850,"min_blocks",2), (858,"min_blocks",2),
    (1015,"prepare",0), (1016,"prepare",0),
    (1017,"static_m",48), (1018,"static_m",48),
    (1017,"inline",0), (1018,"inline",0),
    (974,"inline",0), (1005,"inline",0), (982,"inline",0),
    (985,"inline",0), (928,"inline",0), (859,"inline",0),
    (764,"inline",0), (922,"inline",0), (940,"inline",0),
    (883,"inline",0), (884,"inline",0), (715,"inline",0),
    (776,"persistent",80), (1035,"grid",40),
    (844,"persistent",80), (1037,"grid",40),
    (947,"persistent",40), (1039,"grid",80),
    (863,"persistent",80), (1041,"grid",40),
    (864,"persistent",80), (1043,"grid",40),
    (948,"persistent",40), (1045,"grid",80),
    (872,"persistent",80), (1047,"grid",40),
    (873,"persistent",80), (1049,"grid",40),
    (951,"persistent",40), (1051,"grid",80),
    (866,"persistent",80), (1053,"grid",40),
    (867,"persistent",80), (1055,"grid",40),
    (954,"persistent",40), (1057,"grid",80),
    (869,"persistent",80), (1059,"grid",40),
    (870,"persistent",80), (1061,"grid",40),
    (950,"persistent",40), (1063,"grid",80),
    (860,"persistent",80), (1065,"grid",40),
    (861,"persistent",80), (1067,"grid",40),
    (952,"persistent",40), (1069,"grid",80),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="tn":
        geometry[1]=value
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="unsigned":
        UNSIGNED_INDICES.add(index)
    elif change=="prepare":
        PREPARED_ZERO_BIAS.add(index)
        BYTE_ZERO_WORDS.discard(index)
        ZERO_WORD_LOAD.discard(index)
        PERMUTE_ZERO_BIAS.discard(index)
        INTERLEAVE_ZERO_GROUPS.discard(index)
    elif change=="inline":
        INLINE_REDUCTION.add(index)
        CHUNK_REDUCTION.discard(index)
        BOUNDED_REDUCTION.discard(index)
        PREFETCH_REDUCTION.discard(index)
    elif change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="min_blocks":
        MIN_BLOCKS[index]=value
    elif change=="persistent":
        PERSISTENT_MN.add(index)
        GRID_MULTIPLE[index]=value
    elif change=="grid":
        GRID_MULTIPLE[index]=value

# A25: close the remaining twelve losses before spending on existing winners.
assert len(CONFIGS)==1071
for base,change,value in (
    (1005,"persistent",40), (1071,"grid",80),
    (974,"persistent",40), (1073,"grid",80),
    (922,"persistent",40), (1075,"grid",80),
    (928,"persistent",40), (1077,"grid",80),
    (859,"persistent",40), (1079,"grid",80),
    (1018,"m",64), (1081,"no_unroll",0),
    (1081,"min_blocks",1), (1082,"min_blocks",1),
    (1081,"persistent",40), (1082,"persistent",40),
    (1081,"nk",(16384,3072)), (1082,"nk",(16384,3072)),
    (1085,"nk",(16384,3072)), (1086,"nk",(16384,3072)),
    (1014,"grid",32), (1014,"unpadded",0), (1014,"persistent",40),
    (1005,"cache",0), (1071,"cache",0),
    (928,"cache",0), (1077,"cache",0),
    (1081,"cache",0), (1085,"cache",0),
    (1087,"cache",0), (1089,"cache",0),
    (1096,"static_m",32), (1096,"static_m",24),
    (1102,"persistent",40), (1103,"persistent",40),
    (1057,"wide_k",0), (1106,"cache",0),
    (1106,"register_pipeline",0), (1108,"cache",0),
    (1106,"m",112), (1107,"m",112),
    (1106,"m",104), (1107,"m",104),
    (1106,"no_unroll",0), (1107,"no_unroll",0),
    (906,"persistent",40), (906,"cache",0),
    (1117,"persistent",40), (906,"no_unroll",0),
    (1117,"no_unroll",0), (906,"prepare",0),
    (1121,"cache",0), (1122,"persistent",40),
    (1121,"persistent",40),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="m":
        geometry[0]=geometry[3]=value
    elif change=="wide_k":
        geometry[2]=128
        geometry[5]=2
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="m":
        if value%16==8:
            TAIL_M8.add(index)
        else:
            TAIL_M8.discard(index)
    elif change=="persistent":
        PERSISTENT_MN.add(index)
        GRID_MULTIPLE[index]=value
    elif change=="grid":
        GRID_MULTIPLE[index]=value
    elif change=="min_blocks":
        MIN_BLOCKS[index]=value
    elif change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="no_unroll":
        UNROLL_CYCLES.discard(index)
    elif change=="cache":
        CACHE_SCALES.add(index)
        ZERO_BIAS_CACHE.add(index)
    elif change=="prepare":
        PREPARED_ZERO_BIAS.add(index)
        BYTE_ZERO_WORDS.discard(index)
        ZERO_WORD_LOAD.discard(index)
        PERMUTE_ZERO_BIAS.discard(index)
        INTERLEAVE_ZERO_GROUPS.discard(index)
    elif change=="unpadded":
        DRIVER_OPTIONS[index]=(DRIVER_OPTIONS[index][0],0)
        N_FAST_RASTER.discard(index)
    elif change=="wide_k":
        COOPERATIVE_K[index]=128
    elif change=="register_pipeline":
        FULL_REGISTER_PIPELINE.discard(index)
        INTERLEAVED_A.discard(index)
        REGISTER_PREFETCH.add(index)

# A26: wide-N parallelism without K-cohort reduction, plus remaining range ties.
assert len(CONFIGS)==1125
for base,change,value in (
    (1071,"no_unroll",0), (1073,"no_unroll",0),
    (1075,"no_unroll",0), (1077,"no_unroll",0),
    (1079,"no_unroll",0), (1095,"no_unroll",0),
    (1097,"no_unroll",0), (1125,"min_blocks",1),
    (1128,"min_blocks",2), (1129,"min_blocks",2),
    (1116,"no_unroll",0), (1135,"min_blocks",4),
    (1121,"min_blocks",4), (1121,"no_prefetch",0),
    (906,"no_prefetch",0), (1138,"min_blocks",4),
    (1139,"min_blocks",4), (1121,"tn128_min2",0),
    (1138,"tn128_min2",0), (1139,"tn128_min2",0),
    (1107,"static_m",2048), (1107,"m_fast",0),
    (1145,"m_fast",0),
    (922,"s1",0), (1148,"min_blocks",2),
    (1148,"stages",2), (1150,"min_blocks",2),
    (1148,"tn128_min8",0), (1152,"min_blocks",4),
    (1152,"stages",2),
    (1005,"s1",0), (1155,"min_blocks",2),
    (1155,"stages",3), (1157,"min_blocks",2),
    (1155,"tn128_min8",0), (1159,"min_blocks",4),
    (928,"s1",0), (1161,"min_blocks",2),
    (1161,"stages",2), (1163,"min_blocks",2),
    (1161,"tn128_min8",0), (1165,"min_blocks",4),
    (1165,"stages",2),
    (859,"s1",0), (1168,"min_blocks",8),
    (1168,"tn",256), (1170,"min_blocks",2),
    (1170,"stages",3), (1172,"min_blocks",2),
    (1161,"persistent",40), (1163,"persistent",80),
    (1155,"persistent",80), (1148,"persistent",80),
    (1170,"persistent",80),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="s1":
        geometry[2]=64
    elif change in ("tn128_min2","tn128_min8"):
        geometry[1]=128
    elif change=="tn":
        geometry[1]=value
    elif change=="stages":
        geometry[5]=value
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="no_unroll":
        UNROLL_CYCLES.discard(index)
    elif change=="min_blocks":
        MIN_BLOCKS[index]=value
    elif change=="no_prefetch":
        REGISTER_PREFETCH.discard(index)
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="m_fast":
        N_FAST_RASTER.discard(index)
    elif change=="s1":
        COOPERATIVE_K[index]=64
        MIN_BLOCKS[index]=4
        CHUNK_REDUCTION.discard(index)
        BOUNDED_REDUCTION.discard(index)
        PREFETCH_REDUCTION.discard(index)
        INLINE_REDUCTION.discard(index)
    elif change=="tn128_min2":
        MIN_BLOCKS[index]=2
    elif change=="tn128_min8":
        MIN_BLOCKS[index]=8
    elif change=="persistent":
        PERSISTENT_MN.add(index)
        GRID_MULTIPLE[index]=value

# A27: add margin to the last rectangle that fails the frozen-map range gate.
assert len(CONFIGS)==1179
for base,change,value in (
    (1013,"grid",32), (1013,"static_m",256), (1179,"static_m",256),
    (1013,"wm",64), (1182,"grid",32), (1182,"static_m",256),
    (1184,"grid",32), (1182,"min_blocks",2),
    (1182,"no_prefetch",0), (1186,"no_prefetch",0),
    (1182,"chunk_reduction",0),
):
    index=len(CONFIGS)
    assert 0<=base<index, (base,index)
    geometry=list(CONFIGS[base])
    if change=="wm":
        geometry[3]=value
    CONFIGS += (tuple(geometry),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="grid":
        GRID_MULTIPLE[index]=value
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="min_blocks":
        MIN_BLOCKS[index]=value
    elif change=="no_prefetch":
        REGISTER_PREFETCH.discard(index)
    elif change=="chunk_reduction":
        CHUNK_REDUCTION.add(index)
        INLINE_REDUCTION.discard(index)

# A28: add margin at M4096/N3072/K1024 using existing FPR stage2 controls.
assert len(CONFIGS)==1190
for base,change in (
    (1107,"static_m"), (1190,"m_fast"),
    (1107,"skip_barrier"), (1190,"skip_barrier"), (1191,"skip_barrier"),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="static_m":
        STATIC_M[index]=4096
    elif change=="m_fast":
        N_FAST_RASTER.discard(index)
    elif change=="skip_barrier":
        SKIP_STAGE2_BARRIER.add(index)

# A29: transfer the validated K128 FPR pipeline to the large-matrix gaps.
# Keep the TK64/S3 winners as controls; these candidates still need admission.
assert len(CONFIGS)==1195
for base,change,value in (
    (1194,"static_m",8192),
    (1107,"nk",(2048,3072)), (1196,"skip_barrier",None), (1197,"m_fast",None),
    (1107,"nk",(3072,8192)), (1199,"skip_barrier",None), (1200,"m_fast",None),
    (1107,"nk",(8192,8192)), (1202,"skip_barrier",None), (1203,"m_fast",None),
    (1107,"nk",(16384,3072)), (1205,"skip_barrier",None), (1206,"m_fast",None),
    (1141,"static_m",1), (1141,"static_m",2),
    (1141,"static_m",4), (1141,"static_m",6),
    (1167,"tail24",None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="static_m":
        STATIC_M[index]=value
    elif change=="nk":
        SPECIALIZATIONS[index]=value
    elif change=="skip_barrier":
        SKIP_STAGE2_BARRIER.add(index)
    elif change=="m_fast":
        N_FAST_RASTER.discard(index)
    elif change=="tail24":
        CONFIGS=CONFIGS[:-1]+((24,128,64,24,32,2),)
        TAIL_M8.add(index)
        STATIC_M[index]=24

# A30: N512/M512 grid utilization and warp-N/K work distribution.
# Prepared metadata is one paired load, so caching it needs both cache flags.
assert len(CONFIGS)==1213
for base,change,value in (
    (1011,"tile_m",112), (1011,"tile_m",104),
    (1213,"inline_reduction",None), (1214,"inline_reduction",None),
    (1011,"warp_n32",None), (1217,"inline_reduction",None),
    (1218,"stages",3),
    (1218,"cache_metadata",None), (1219,"cache_metadata",None),
    (1220,"unroll",None), (1221,"unroll",None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    tm,tn,tk,wm,wn,stages=CONFIGS[index]
    if change=="tile_m":
        CONFIGS=CONFIGS[:-1]+((value,tn,tk,value,wn,stages),)
        if value%16:
            TAIL_M8.add(index)
    elif change=="inline_reduction":
        INLINE_REDUCTION.add(index)
    elif change=="warp_n32":
        CONFIGS=CONFIGS[:-1]+((tm,tn,tk,wm,32,stages),)
        COOPERATIVE_K[index]=32
    elif change=="stages":
        CONFIGS=CONFIGS[:-1]+((tm,tn,tk,wm,wn,value),)
    elif change=="cache_metadata":
        CACHE_SCALES.add(index)
        ZERO_BIAS_CACHE.add(index)
    elif change=="unroll":
        UNROLL_CYCLES.add(index)

# A31: retain N locality while grouping a few M tiles to reuse B in LLC.
RASTER_GROUP_M = {}
assert len(CONFIGS)==1224
for base,change,value in (
    (1051,"raster_group",2), (1051,"raster_group",4), (1051,"raster_group",8),
    (1203,"raster_group",4),
    (1225,"static_m",8192), (1225,"static_m",4096),
    (1045,"raster_group",2), (1045,"raster_group",4), (1045,"raster_group",8),
    (1063,"raster_group",2), (1063,"raster_group",4), (1063,"raster_group",8),
    (1213,"cache_metadata",None), (1236,"unroll",None),
    (1237,"static_m",512), (1237,"vector_output",None),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="raster_group":
        RASTER_GROUP_M[index]=value
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="cache_metadata":
        CACHE_SCALES.add(index)
        ZERO_BIAS_CACHE.add(index)
    elif change=="unroll":
        UNROLL_CYCLES.add(index)
    elif change=="vector_output":
        VECTOR_OUTPUT.add(index)

# A32: compare full-domain Stream-K with a persistent prefix and balanced tail.
STREAM_K_MODE = {}
assert len(CONFIGS)==1240
for base,change,value in (
    (1051,"streamk",40), (1240,"mode",1), (1241,"mode",2),
    (1242,"static_m",8192), (1242,"static_m",4096),
    (1063,"streamk",40), (1245,"mode",1), (1246,"mode",2),
    (1247,"static_m",8192),
    (1045,"streamk",40), (1249,"mode",1), (1250,"mode",2),
    (1107,"streamk",40), (1252,"mode",1), (1253,"mode",2),
    (1254,"static_m",8192),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="streamk":
        STREAM_K_WORKERS[index]=value
        PERSISTENT_MN.discard(index)
    elif change=="mode":
        STREAM_K_MODE[index]=value
    elif change=="static_m":
        STATIC_M[index]=value

# A33: the FP32 completion staging tile otherwise exceeds half a CU's TSM.
GLOBAL_OUTPUT_PADDING = {}
assert len(CONFIGS)==1256
for base,change,value in (
    *((index,"global_output_padding",0) for index in range(1240,1256)),
    (1236,"n_fast",None), (1272,"static_m",512), (1273,"unroll",None),
    (1212,"nk",(8192,8192)),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="global_output_padding":
        GLOBAL_OUTPUT_PADDING[index]=value
    elif change=="n_fast":
        N_FAST_RASTER.add(index)
    elif change=="static_m":
        STATIC_M[index]=value
    elif change=="unroll":
        UNROLL_CYCLES.add(index)
    elif change=="nk":
        SPECIALIZATIONS[index]=value

# A34: keep block shape, CTA size and MMA work fixed while widening warp N.
# This trades less duplicated A reading for more B conversion across M warps.
assert len(CONFIGS)==1276
for base,change,value in (
    (1051,"warp_shape",(64,64)), (1045,"warp_shape",(64,64)),
    (1063,"warp_shape",(64,64)), (1107,"warp_shape",(64,64)),
    (1051,"warp_shape",(32,128)), (1045,"warp_shape",(32,128)),
    (1063,"warp_shape",(32,128)), (1107,"warp_shape",(32,128)),
    (1202,"warp_shape",(64,64)), (1205,"warp_shape",(64,64)),
    (1276,"static_m",8192), (1277,"static_m",8192),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="warp_shape":
        tm,tn,tk,_,_,stages=CONFIGS[index]
        CONFIGS=CONFIGS[:-1]+((tm,tn,tk,*value,stages),)
    elif change=="static_m":
        STATIC_M[index]=value

# A35: larger CTAs retain warp128x32 and its B-conversion amortization.
assert len(CONFIGS)==1288
for base,change in (
    (1051,"block_n"), (1051,"block_m"),
    (1045,"block_n"), (1045,"block_m"),
    (1063,"block_n"), (1063,"block_m"),
    (1107,"block_n"), (1107,"block_m"),
    (1272,"direct"), (1272,"vector"),
    (1296,"inline_reduction"), (1296,"group_stores"),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change in ("block_n","block_m"):
        tm,tn,tk,wm,wn,stages=CONFIGS[index]
        CONFIGS=CONFIGS[:-1]+((tm*(1+(change=="block_m")),tn*(1+(change=="block_n")),
                              tk,wm,wn,stages),)
        GRID_MULTIPLE[index]=20
        MIN_BLOCKS[index]=1
    elif change=="direct":
        DIRECT_OUTPUT.add(index)
    elif change=="vector":
        VECTOR_OUTPUT.add(index)
    elif change=="inline_reduction":
        INLINE_REDUCTION.add(index)
    elif change=="group_stores":
        GROUP_OUTPUT_STORES.add(index)

# A36: isolate whole-K prefix and FP32 Stream-K tail in separate launches.
assert len(CONFIGS)==1300
for base in (1258,1264,1267,1270):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    STREAM_K_MODE[index]=3

# A37: extend admitted mappings to the remaining small-M and narrow-N gaps.
assert len(CONFIGS)==1304
for base,change in (
    (758,"no_prefetch"), (759,"no_prefetch"),
    (1069,"n512"), (1091,"m64"), (1181,"m64"),
    (1307,"no_prefetch"), (1308,"no_prefetch"),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION):
        if base in feature:
            feature.add(index)
    if change=="no_prefetch":
        REGISTER_PREFETCH.discard(index)
    elif change=="n512":
        SPECIALIZATIONS[index]=(512,3072)
    elif change=="m64":
        _,tn,tk,_,wn,stages=CONFIGS[index]
        CONFIGS=CONFIGS[:-1]+((64,tn,tk,64,wn,stages),)

# A38: direct-output controls, then carry the input pipeline across MN tiles.
PERSISTENT_PREFETCH=set()
assert len(CONFIGS)==1311
for base,prefetch in (
    (1195,False),(1311,True),
    (1045,False),(1313,True),
    (1107,False),(1315,True),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION,PERSISTENT_PREFETCH):
        if base in feature:
            feature.add(index)
    DIRECT_OUTPUT.add(index)
    if prefetch:
        PERSISTENT_PREFETCH.add(index)

# A39: the first full rotation exposes four medium-M losses. Keep the
# installed shape controls; vary one pipeline/metadata choice at each rung.
assert len(CONFIGS)==1317
for base,change in (
    (824,"tk512"), (824,"stage3"), (824,"compact-zero"), (1317,"stage3"),
    (1091,"stage3"), (1091,"no-prefetch"),
    (1181,"stage3"), (1181,"no-prefetch"),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION,PERSISTENT_PREFETCH):
        if base in feature:
            feature.add(index)
    if change=="compact-zero":
        BYTE_ZERO_WORDS.discard(index)
    elif change=="no-prefetch":
        REGISTER_PREFETCH.discard(index)
    else:
        tm,tn,tk,wm,wn,stages=CONFIGS[index]
        CONFIGS=CONFIGS[:-1]+((tm,tn,512 if change=="tk512" else tk,
                             wm,wn,3 if change=="stage3" else stages),)

# A40: transfer only the third pipeline stage to selected small-M controls.
# Canonical bytes, N/K ownership, grid, decoder and reduction remain fixed.
assert len(CONFIGS)==1325
for base in (829,683,838,675,676,1304,1305):
    index=len(CONFIGS)
    tm,tn,tk,wm,wn,stages=CONFIGS[base]
    assert stages==2
    CONFIGS += ((tm,tn,tk,wm,wn,3),)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION,PERSISTENT_PREFETCH):
        if base in feature:
            feature.add(index)

# A41: trade additional A reads for twice the B reuse within each warp.
# Keep the existing readers, prepared bytes and FP32 arithmetic unchanged.
assert len(CONFIGS)==1332
for base in (1051,1045):
    for tm,tn,pipeline,grid in (
        (256,128,"full",40),(256,128,"chunk",40),(256,128,"prefetch",40),
        (256,256,"full",20),(256,256,"chunk",20),(256,256,"prefetch",20),
        (128,256,"chunk",40),
    ):
        index=len(CONFIGS)
        CONFIGS += ((tm,tn,64,tm,16 if tm==256 else 32,3),)
        for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
            if base in table:
                table[index]=table[base]
        for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION,PERSISTENT_PREFETCH):
            if base in feature:
                feature.add(index)
        GRID_MULTIPLE[index]=grid
        if tm==256 and tn==256:
            MIN_BLOCKS[index]=1
        if pipeline!="full":
            FULL_REGISTER_PIPELINE.discard(index)
            INTERLEAVED_A.discard(index)
        if pipeline=="prefetch":
            REGISTER_PREFETCH.add(index)

# A42: producer placement, existing byte-pair metadata, then exact-M lowering.
assert len(CONFIGS)==1346
for base,change in (
    (1326,"producer"),(1325,0),(1347,2),(1347,4),(1347,6),
):
    index=len(CONFIGS)
    CONFIGS += (CONFIGS[base],)
    for table in (SCHEDULES,COOPERATIVE_K,COHORTS,DRIVER_OPTIONS,SPECIALIZATIONS,MIN_BLOCKS,GLOBAL_SLICES,FUSED_STORE_WARPS,MMA_M8,GRID_MULTIPLE,COMPILER_FENCE,STATIC_M,COMPACT_OUTPUT,REDUCTION_STORAGE,DIRECT_A,COHORT_PIPELINE,WARP_ORDER,B_PRODUCER_WARP,STREAM_K_WORKERS,RASTER_GROUP_M,STREAM_K_MODE,GLOBAL_OUTPUT_PADDING):
        if base in table:
            table[index]=table[base]
    for feature in (NATIVE_A,NATIVE_B,CHUNK_A,BOUNDED_REDUCTION,CHUNK_REDUCTION,STAGE_CYCLES,PERSISTENT_MN,REGISTER_PREFETCH,PAIRED_SCALES,FULL_REGISTER_PIPELINE,VECTOR_OUTPUT,DIRECT_OUTPUT,UNROLL_CYCLES,OPAQUE_COORDINATES,SHARED_B,UNSIGNED_INDICES,INTERLEAVED_A,N_FAST_RASTER,PRUNE_ROWS,TAIL_M8,CACHE_SCALES,SKIP_STAGE2_BARRIER,PREFETCH_REDUCTION,GROUP_OUTPUT_STORES,INTEGER_ZERO,ZERO_WORD_LOAD,SINGLE_ZERO_BIAS,INTERLEAVE_ZERO_GROUPS,PAIRED_ZERO_BIAS,ZERO_BIAS_CACHE,PERMUTE_ZERO_BIAS,PREPARED_ZERO_BIAS,BYTE_ZERO_WORDS,INLINE_REDUCTION,PERSISTENT_PREFETCH):
        if base in feature:
            feature.add(index)
    if change=="producer":
        B_PRODUCER_WARP[index]=8
    else:
        STATIC_M[index]=change
