"""Native ZW810E affine INT4 selection, separate from performance admission.

The public builder compiles this finite configuration set into its C ABI.
Query/prepare select once; run neither imports this module nor dispatches/JITs.
Generic fallbacks provide coverage, not inherited performance claims.
"""

# zero_mode, M, N, K, configuration. All reductions remain FP32.
EXACT = (
    (0,1,1024,3072,627),(0,12,1024,3072,459),(0,16,1024,3072,460),
    (0,64,1024,3072,255),(0,512,1024,3072,336),
    (0,1,2048,3072,535),(0,12,2048,3072,550),(0,16,2048,3072,536),
    (0,64,2048,3072,256),(0,512,2048,3072,396),
    (0,1,3072,1024,45),(0,12,3072,1024,45),(0,16,3072,1024,45),
    (0,64,3072,1024,74),(0,512,3072,1024,151),
    (1,1,1024,3072,590),(1,12,1024,3072,602),(1,16,1024,3072,603),
    (1,64,1024,3072,582),(1,512,1024,3072,584),
    (1,1,2048,3072,645),(1,12,2048,3072,624),(1,16,2048,3072,626),
    (1,64,2048,3072,583),(1,512,2048,3072,634),
    (1,1,3072,1024,588),(1,12,3072,1024,588),(1,16,3072,1024,588),
    (1,64,3072,1024,586),(1,512,3072,1024,587),
)

# V5 incorporates phase-two candidates validated in hot and rotated weights.
# Installed-wheel performance admission remains a separate immutable receipt.
_MATCHED_INTEGER = (
    (512,3072,((256,685),(512,1299),(1024,686),(2048,687),(4096,687),(8192,687))),
    (1024,3072,(
        (1,1325),(2,1348),(4,1349),(6,1350),(8,1327),(12,1328),(16,1329),
        (24,1320),(32,1320),(48,825),(64,582),(128,699),(256,1324),
        (512,584),(1024,776),(2048,826),(4096,826),(8192,1039))),
    (2048,3072,(
        (1,625),(2,799),(4,800),(6,801),(8,908),(12,775),(16,682),
        (24,731),(32,731),(48,732),(64,583),(128,1322),(256,621),
        (512,634),(1024,1069),(2048,860),(4096,1069),(8192,1069))),
    (3072,1024,((1024,866),(2048,1147),(4096,1194),(8192,1195))),
    (3072,8192,((1024,869),(2048,1063),(4096,1063),(8192,1063))),
    (8192,8192,(
        (1,1208),(2,1209),(4,1210),(6,1211),(8,1141),(12,1304),(16,1305),
        (24,1129),(32,1129),(48,1020),(64,1081),(128,1051),(256,1051),
        (512,1051),(1024,1051),(2048,1051),(4096,1051),(8192,1051))),
    (16384,3072,(
        (1,756),(2,803),(4,804),(6,805),(8,907),(12,785),(16,786),
        (24,1167),(32,1167),(48,1159),(64,1154),(128,1045),(256,1045),
        (512,1045),(1024,1045),(2048,1045),(4096,1045),(8192,1045))),
)
_MATCHED_ROWS = tuple(
    (1,m,n,k,config)
    for n,k,selections in _MATCHED_INTEGER for m,config in selections
)
_MATCHED_KEYS = {row[:4] for row in _MATCHED_ROWS}
EXACT = tuple(row for row in EXACT if row[:4] not in _MATCHED_KEYS) + _MATCHED_ROWS

# zero_mode, inclusive maximum M, configuration. N/K remain multiples of256.
FALLBACKS = (
    (0,7,616),(0,16,615),(0,64,617),(0,2**31-1,103),
    (1,7,619),(1,16,618),(1,64,620),(1,2**31-1,621),
)
# Preserve the replaced public IDs for callers using explicit configurations.
RETAINED_CONFIGS = (675,676,683,758,759,824,829,838,1091,1181)
PRODUCTION_CONFIGS = tuple(sorted({r[-1] for r in EXACT+FALLBACKS} | set(RETAINED_CONFIGS)))


def describe(configs):
    compiled=set(configs)
    return dict(
        policy="ZW810E_AFFINE_INT4_G32_V5",group_size=32,split=1,
        exact=[dict(zip(("zero_mode","m","n","k","config"),r)) for r in EXACT if r[-1] in compiled],
        fallbacks=[dict(zip(("zero_mode","max_m","config"),r)) for r in FALLBACKS if r[-1] in compiled],
        performance_admitted=False,
    )


def render(configs):
    """Emit selection only for entries present in this native compilation."""
    policy=describe(configs)
    lines=["int default_config(qwa_problem_v1 const& p) {","  if(p.split!=1) return -1;"]
    for row in policy["exact"]:
        condition=" && ".join(f"p.{name}=={row[name]}" for name in ("zero_mode","m","n","k"))
        lines.append(f"  if({condition}) return {row['config']};")
    for row in policy["fallbacks"]:
        lines.append(f"  if(p.zero_mode=={row['zero_mode']} && p.m<={row['max_m']}) return {row['config']};")
    return "\n".join([*lines,"  return -1;","}"])
