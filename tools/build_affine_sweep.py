import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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
from flashquant.affine.selection import describe as describe_selection, render as render_selection
from tools.build_affine import FLAGS, LIBRARIES, actlize_revision, sha


def build(sdk, output, configs, jobs, layout="kpack", *, arch="ppu_10"):
    if arch != "ppu_10":
        raise ValueError("R4 affine sweep supports ppu_10 only")
    dependency = actlize_revision(ROOT)
    sdk = sdk.resolve(strict=True)
    output = output.resolve()
    if (not configs and arch=="ppu_10") or len(configs) != len(set(configs)) or any(i not in range(len(CONFIGS)) for i in configs):
        raise ValueError("invalid W4A16 candidate IDs")
    if arch!="ppu_10" and configs:
        raise ValueError("W4A16 native collectives currently require ppu_10")
    if jobs < 1:
        raise ValueError("jobs must be positive")
    if layout == "classic" and any(index not in COOPERATIVE_K for index in configs):
        raise ValueError("classic code-layout control requires the native warp-K collective")
    if layout == "classic" and any(index in INTEGER_ZERO for index in configs):
        raise ValueError("integer-zero candidates require native K-pack")
    output.mkdir(exist_ok=False)
    include = [
        ROOT / "flashquant/affine", ROOT / "flashquant/include",
        ROOT / "third_party/actlize/include", ROOT / "third_party/actlize/tools/util/include",
        ROOT / "third_party/actlize/examples/common", sdk / "include",
    ]
    flags = [str(sdk / "bin/hgcc"), *FLAGS, *("-I" + str(path) for path in include)]
    flags += ["-DQUACTLIZE_W4A16_CLASSIC_WEIGHTS=" + str(int(layout == "classic"))]
    env = dict(os.environ, PATH=str(sdk / "bin") + ":" + os.environ.get("PATH", ""),
               LD_LIBRARY_PATH=str(sdk / "lib") + ":" + os.environ.get("LD_LIBRARY_PATH", ""))
    declarations, entries, sources = [], [], []
    for index in configs:
        geometry = ",".join(map(str, CONFIGS[index]))
        name = f"w4a16_{index}"
        source = output / (name + ".cu")
        schedule = SCHEDULES.get(index)
        header = "scheduled.cuh" if schedule else "launch.cuh"
        kernel = "ScheduledKernel" if schedule else "Kernel"
        extra = "," + ",".join(map(str, schedule)) if schedule else ""
        if index in COOPERATIVE_K:
            header, kernel = "cooperative.cuh", "CooperativeKernel"
            extra = "," + str(COOPERATIVE_K[index]) + "," + str(int(index in NATIVE_A))
            extra += "," + ",".join(map(str,DRIVER_OPTIONS.get(index,(0,0))))
            extra += "," + str(int(index in NATIVE_B))
            extra += "," + str(int(index in CHUNK_A))
            extra += "," + str(int(index in BOUNDED_REDUCTION))
            extra += "," + str(int(index in CHUNK_REDUCTION))
            extra += "," + ",".join(map(str,SPECIALIZATIONS.get(index,(0,0))))
            extra += "," + str(MIN_BLOCKS.get(index,1))
            extra += "," + str(int(index in STAGE_CYCLES))
            extra += "," + str(GLOBAL_SLICES.get(index,1))
            extra += "," + str(FUSED_STORE_WARPS.get(index,0))
            extra += "," + str(int(index in PERSISTENT_MN))
            extra += "," + str(MMA_M8.get(index,0))
            extra += "," + str(int(index in REGISTER_PREFETCH))
            extra += "," + str(int(index in PAIRED_SCALES))
            extra += "," + str(int(index in FULL_REGISTER_PIPELINE))
            extra += "," + str(GRID_MULTIPLE.get(index,40))
            extra += "," + str(int(index in VECTOR_OUTPUT))
            extra += "," + str(int(index in DIRECT_OUTPUT))
            extra += "," + str(int(index in UNROLL_CYCLES))
            extra += "," + str(COMPILER_FENCE.get(index,0))
            extra += "," + str(int(index in OPAQUE_COORDINATES))
            extra += "," + str(int(index in SHARED_B))
            extra += "," + str(int(index in UNSIGNED_INDICES))
            extra += "," + str(int(index in INTERLEAVED_A))
            extra += "," + str(STREAM_K_WORKERS.get(index,0))
            extra += "," + str(int(index in N_FAST_RASTER))
            extra += "," + str(STATIC_M.get(index,0)) + "," + str(int(index in PRUNE_ROWS))
            extra += "," + str(int(index in TAIL_M8))
            extra += "," + str(int(index in CACHE_SCALES))
            extra += f",{COMPACT_OUTPUT.get(index,0)}"
            extra += "," + str(int(index in SKIP_STAGE2_BARRIER))
            extra += f",{REDUCTION_STORAGE.get(index,0)}"
            extra += f",{DIRECT_A.get(index,0)}"
            extra += f",{COHORT_PIPELINE.get(index,0)}"
            extra += f",{WARP_ORDER.get(index,0)}"
            extra += f",{B_PRODUCER_WARP.get(index,0)}"
            extra += f",{int(index in PREFETCH_REDUCTION)}"
            extra += f",{int(index in GROUP_OUTPUT_STORES)}"
            extra += f",{int(index in INTEGER_ZERO)}"
            extra += f",{int(index in ZERO_WORD_LOAD)}"
            extra += f",{int(index in SINGLE_ZERO_BIAS)}"
            extra += f",{int(index in INTERLEAVE_ZERO_GROUPS)}"
            extra += f",{int(index in PAIRED_ZERO_BIAS)}"
            extra += f",{int(index in ZERO_BIAS_CACHE)}"
            extra += f",{int(index in PERMUTE_ZERO_BIAS)}"
            extra += f",{int(index in PREPARED_ZERO_BIAS)}"
            extra += f",{int(index in BYTE_ZERO_WORDS)}"
            extra += f",{int(index in INLINE_REDUCTION)}"
            extra += f",{RASTER_GROUP_M.get(index,1)}"
            extra += f",{STREAM_K_MODE.get(index,0)}"
            extra += f",{GLOBAL_OUTPUT_PADDING.get(index,8)}"
            extra += f",{int(index in PERSISTENT_PREFETCH)}"
        if index in COHORTS:
            header, kernel = "cohorts.cuh", "CohortKernel"
            extra = "," + str(COHORTS[index])
        source.write_text(
            f'#include "{header}"\n'
            f"using K = quactlize::affine::{kernel}<{geometry}{extra}>;\n"
            f"qwa_info_v1 {name}_query(qwa_problem_v1 const& p) {{ return K::query(p); }}\n"
            f"quactlize::affine::Plan* {name}_prepare(qwa_problem_v1 const& p, qwa_buffers_v1 const& b) "
            "{ return K::prepare(p,b); }\n")
        sources.append(source)
        declarations.extend([
            f"qwa_info_v1 {name}_query(qwa_problem_v1 const&);",
            f"quactlize::affine::Plan* {name}_prepare(qwa_problem_v1 const&, qwa_buffers_v1 const&);",
        ])
        entries.append(f"{{{{1,sizeof(qwa_config_v1),{index},{geometry}}},{name}_query,{name}_prepare,{int(index in INTEGER_ZERO)}}}")
    registry = output / "registry.cpp"
    registry.write_text(
        '#include "internal.hpp"\n' + "\n".join(declarations) +
        "\nnamespace quactlize::affine {\nEntry const entries[] = {\n" +
        (",\n".join(entries) if entries else "{}") +
        f"\n}};\nint const entry_count = {len(entries)};\n" + render_selection(configs) + "\n}\n")
    sources += [registry, ROOT / "flashquant/affine/runtime.cpp", ROOT / "flashquant/affine/pack.cu"]
    commands = [
        [*flags, "-c", str(source), "-o", str(output / (source.stem + ".o"))]
        for source in sources
    ]
    library = output / "libflashquant-sweep.so"
    link = [
        "g++", "-shared", "-Wl,-Bsymbolic", "-Wl,-z,defs",
        *[str(output / (source.stem + ".o")) for source in sources],
        "-L" + str(sdk / "lib"), *["-l" + name for name in LIBRARIES],
        "-o", str(library),
    ]
    (output / "commands.json").write_text(json.dumps(commands + [link], indent=2) + "\n")
    files = sorted([
        p for root in (ROOT / "flashquant/affine", ROOT / "flashquant/include")
        for p in root.rglob("*") if p.is_file() and p.suffix in (".h", ".hpp", ".cuh", ".cpp", ".cu", ".py", ".inl", ".inc")
    ] + [Path(__file__).resolve(),ROOT / "tools/build_affine.py", ROOT / "tools/sweep_catalog.py"])
    source_hashes={str(path.relative_to(ROOT)):sha(path) for path in files}
    snapshot=output / "source.tar.gz"
    with tarfile.open(snapshot,"w:gz") as archive:
        for path in files:
            archive.add(path,arcname=str(path.relative_to(ROOT)),recursive=False)

    def run(index_command):
        index, command = index_command
        log = output / f"compile-{index}.log"
        Path(command[-1]).unlink(missing_ok=True)
        with log.open("w") as handle:
            result = subprocess.run(command, env=env, stdout=handle, stderr=subprocess.STDOUT)
        errors=len(re.findall(r"\b(?:fatal )?error:",log.read_text(errors="replace")))
        print(json.dumps({"source":str(sources[index]),"compiler_errors":errors,
                          "returncode":result.returncode}),flush=True)
        if result.returncode or errors:
            raise RuntimeError(f"W4A16 native build failed: {log}")
        print(json.dumps({"compiled": index, "source": str(sources[index])}), flush=True)

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(run, enumerate(commands)))
    library.unlink(missing_ok=True)
    with (output / "link.log").open("w") as log:
        subprocess.run(link, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    if source_hashes != {str(path.relative_to(ROOT)):sha(path) for path in files}:
        raise RuntimeError("Source changed during the native build; this candidate is not reproducible")
    manifest = {
        "arch": arch, "group_size": 32,
        "quantization": "ordinary affine INT4; unsigned codes 0..15; candidate zero_mode 0=center8, 1=integer0..15",
        "input_dtype": "float16", "output_dtype": "float16", "accumulation": "float32",
        "layout": "classic Marlin code layout" if layout == "classic" else "canonical K-pack4",
        "mapping_id": "0x5741344d4c000001" if layout == "classic" else "0x51344b5034540001",
        "splitk": "production compact FP32 partials and final FP16 reducer",
        "configurations": {str(index): CONFIGS[index] for index in configs},
        "selection": describe_selection(configs),
        "objects": [str(output/(source.stem+".o")) for source in sources],
        "schedulers": {str(index): SCHEDULES[index] for index in configs if index in SCHEDULES},
        "cooperative_k": {str(index): COOPERATIVE_K[index] for index in configs if index in COOPERATIVE_K},
        "cohorts": {str(index): COHORTS[index] for index in configs if index in COHORTS},
        "native_a": [index for index in configs if index in NATIVE_A],
        "native_b": [index for index in configs if index in NATIVE_B],
        "chunk_a": [index for index in configs if index in CHUNK_A],
        "bounded_reduction": [index for index in configs if index in BOUNDED_REDUCTION],
        "chunk_reduction": [index for index in configs if index in CHUNK_REDUCTION],
        "specializations": {str(index): SPECIALIZATIONS[index] for index in configs if index in SPECIALIZATIONS},
        "launch_bounds_min_blocks": {str(index): MIN_BLOCKS.get(index,1) for index in configs},
        "stage_cycles": [index for index in configs if index in STAGE_CYCLES],
        "global_slices": {str(index): GLOBAL_SLICES.get(index,1) for index in configs},
        "fused_store_warps": {str(index): FUSED_STORE_WARPS.get(index,0) for index in configs},
        "persistent_mn": [index for index in configs if index in PERSISTENT_MN],
        "mma_m8_partition": {str(index): MMA_M8.get(index,0) for index in configs},
        "register_prefetch": [index for index in configs if index in REGISTER_PREFETCH],
        "paired_scales": [index for index in configs if index in PAIRED_SCALES],
        "full_register_pipeline": [index for index in configs if index in FULL_REGISTER_PIPELINE],
        "grid_multiple": {str(index):GRID_MULTIPLE[index] for index in configs if index in GRID_MULTIPLE},
        "vector_output": [index for index in configs if index in VECTOR_OUTPUT],
        "direct_output": [index for index in configs if index in DIRECT_OUTPUT],
        "unroll_cycles": [index for index in configs if index in UNROLL_CYCLES],
        "compiler_fence": {str(index):COMPILER_FENCE[index] for index in configs if index in COMPILER_FENCE},
        "opaque_coordinates": [index for index in configs if index in OPAQUE_COORDINATES],
        "shared_b": [index for index in configs if index in SHARED_B],
        "unsigned_indices": [index for index in configs if index in UNSIGNED_INDICES],
        "interleaved_a": [index for index in configs if index in INTERLEAVED_A],
        "stream_k_workers": {str(index):STREAM_K_WORKERS[index] for index in configs if index in STREAM_K_WORKERS},
        "n_fast_raster": [index for index in configs if index in N_FAST_RASTER],
        "static_m": {str(index):STATIC_M[index] for index in configs if index in STATIC_M},
        "prune_rows": [index for index in configs if index in PRUNE_ROWS],
        "tail_m8": [index for index in configs if index in TAIL_M8],
        "cache_scales": [index for index in configs if index in CACHE_SCALES],
        "compact_output": {str(index):COMPACT_OUTPUT[index] for index in configs if index in COMPACT_OUTPUT},
        "skip_stage2_barrier": [index for index in configs if index in SKIP_STAGE2_BARRIER],
        "reduction_storage": {str(index):REDUCTION_STORAGE[index] for index in configs if index in REDUCTION_STORAGE},
        "direct_a": {str(index):DIRECT_A[index] for index in configs if index in DIRECT_A},
        "cohort_pipeline": {str(index):COHORT_PIPELINE[index] for index in configs if index in COHORT_PIPELINE},
        "warp_order": {str(index):WARP_ORDER[index] for index in configs if index in WARP_ORDER},
        "b_producer_warp": {str(index):B_PRODUCER_WARP[index] for index in configs if index in B_PRODUCER_WARP},
        "prefetch_reduction": [index for index in configs if index in PREFETCH_REDUCTION],
        "group_output_stores": [index for index in configs if index in GROUP_OUTPUT_STORES],
        "integer_zero": [index for index in configs if index in INTEGER_ZERO],
        "zero_word_load": [index for index in configs if index in ZERO_WORD_LOAD],
        "single_zero_bias": [index for index in configs if index in SINGLE_ZERO_BIAS],
        "interleave_zero_groups": [index for index in configs if index in INTERLEAVE_ZERO_GROUPS],
        "zero_group_interleave": {
            str(index):2 if index in BYTE_ZERO_WORDS else
                (4 if CONFIGS[index][2]%128==0 else 2) if index in INTERLEAVE_ZERO_GROUPS else 1
            for index in configs if index in INTEGER_ZERO},
        "paired_zero_bias": [index for index in configs if index in PAIRED_ZERO_BIAS],
        "zero_bias_cache": [index for index in configs if index in ZERO_BIAS_CACHE],
        "permute_zero_bias": [index for index in configs if index in PERMUTE_ZERO_BIAS],
        "prepared_zero_bias": [index for index in configs if index in PREPARED_ZERO_BIAS],
        "byte_zero_words": [index for index in configs if index in BYTE_ZERO_WORDS],
        "inline_reduction": [index for index in configs if index in INLINE_REDUCTION],
        "raster_group_m": {index: RASTER_GROUP_M.get(index,1) for index in configs},
        "stream_k_mode": {index: STREAM_K_MODE.get(index,0) for index in configs},
        "global_output_padding": {index: GLOBAL_OUTPUT_PADDING.get(index,8) for index in configs},
        "persistent_prefetch": [index for index in configs if index in PERSISTENT_PREFETCH],
        "driver_options": {str(index): DRIVER_OPTIONS.get(index,(0,0))
                           for index in configs if index in COOPERATIVE_K},
        "revision": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "actlize": dependency,
        "source_sha256": source_hashes,
        "source_snapshot": str(snapshot), "source_snapshot_sha256": sha(snapshot),
        "library": str(library), "library_sha256": sha(library), "commands": commands + [link],
        "scope": "FlashQuant R4 research subset; not a production or performance receipt",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"library": str(library), "sha256": manifest["library_sha256"]}), flush=True)
    return library


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", type=Path, default=Path(os.environ.get("PPU_SDK", "/usr/local/PPU_SDK")))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--configs", required=True, help="comma-separated R4 candidate IDs; select the intended subset")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--layout", choices=["kpack","classic"], default="kpack")
    parser.add_argument("--arch",choices=("ppu_10",),default="ppu_10")
    args = parser.parse_args()
    build(args.sdk, args.output, [int(value) for value in args.configs.split(",") if value], args.jobs, args.layout,arch=args.arch)


if __name__ == "__main__":
    main()
