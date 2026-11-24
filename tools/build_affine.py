"""Build the shipping ppu_10 affine registry into one standalone library."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flashquant.affine.configs import CONFIGS, dynamic_m_twin
from flashquant.affine.selection import PRODUCTION_CONFIGS, describe, render


# Keep the measured ppu_10 codegen flags. No GGUF compiler or JIT is involved.
FLAGS = [
    "--forward-unknown-to-host-compiler", "--forward-unknown-to-host-linker",
    "-arch=ppu_10", "-x", "hg", "-DSWITCH_TO_HGGCRT", "-std=c++17", "-O3",
    "-Xcompiler", "-ftemplate-depth=8192", "-Xllvm", "-wno-loop-miss-transform",
    "-Xllvm", "-ppu-simt-branch=false", "-Xllvm", "-ppu-patch-fence-ppu=false",
    "-Xllvm", "-ppu-cg-to-kp1=true", "-Xllvm", "-ppu-fix-uninit=true",
    "--expt-relaxed-constexpr", "-DUSE_CLANG", "-DCUTLASS_USE_PACKED_TUPLE=1",
    "-DCUTE_USE_PACKED_TUPLE=1", "-fPIC",
]
LIBRARIES = ("hggc_wrapper", "hggcrt1", "hggc", "hg_wrapper")


def sha(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def actlize_revision(root):
    dependency = root / "third_party/actlize"
    record = subprocess.check_output(
        ["git", "-C", str(root), "ls-tree", "HEAD", "third_party/actlize"], text=True
    ).split()
    if len(record) != 4 or record[:2] != ["160000", "commit"]:
        raise ValueError("FlashQuant has no pinned actlize gitlink")
    if not (dependency / "include/ppu_include.hpp").is_file():
        raise ValueError("initialize the dependency: git submodule update --init third_party/actlize")
    actual = subprocess.check_output(["git", "-C", str(dependency), "rev-parse", "HEAD"], text=True).strip()
    if actual != record[2]:
        raise ValueError(f"actlize checkout differs from gitlink: expected {record[2]}, got {actual}")
    subprocess.run(["git", "-C", str(dependency), "diff", "--exit-code", "--quiet", "HEAD", "--",
                    "include", "tools/util/include", "examples/common"], check=True)
    return actual


def generate(work, ids, configs=CONFIGS):
    sources, declarations, entries = [], [], []
    for index in ids:
        cfg = configs[index]
        symbol = f"w4a16_{index}"
        query = f"qwa_info_v1 {symbol}_query(qwa_problem_v1 const& p)"
        prepare = f"quactlize::affine::Plan* {symbol}_prepare(qwa_problem_v1 const& p, qwa_buffers_v1 const& b)"
        unit = work / (symbol + ".cu")
        unit.write_text(
            f'#include "{cfg.header}"\nusing K = quactlize::affine::{cfg.specialization()};\n'
            f"{query} {{ return K::query(p); }}\n{prepare} {{ return K::prepare(p,b); }}\n"
        )
        sources.append(unit)
        declarations.extend((query + ";", prepare + ";"))
        geometry = ",".join(map(str, cfg.tile))
        entries.append(f"{{{{1,sizeof(qwa_config_v1),{index},{geometry}}},"
                       f"{symbol}_query,{symbol}_prepare,{cfg.value('IntegerZero')}}}")
    registry = work / "registry.cpp"
    registry.write_text('#include "internal.hpp"\n' + "\n".join(declarations) +
                        "\nnamespace quactlize::affine {\nEntry const entries[] = {\n" +
                        ",\n".join(entries) + f"\n}};\nint const entry_count = {len(entries)};\n" +
                        render(ids) + "\n}\n")
    return [*sources, registry, ROOT / "flashquant/affine/runtime.cpp", ROOT / "flashquant/affine/pack.cu"]


def build(sdk, output, ids, jobs, *, relax_m1=False):
    configs = dict(CONFIGS)
    if relax_m1:
        # Only explicit IDs reach these twins. No fabricated measurement or
        # change to the established default selector, even in an opt-in build.
        twins = {10000+i: dynamic_m_twin(CONFIGS[i]) for i in ids
                 if i in CONFIGS and CONFIGS[i].value("StaticM")==1}
        if not twins:
            raise ValueError("--relax-m1 requires an M1 config")
        configs.update(twins)
        ids = [*ids,*twins]
    if not ids or len(set(ids)) != len(ids) or not set(ids) <= configs.keys():
        raise ValueError("--configs must name distinct shipping configuration IDs")
    if jobs < 1:
        raise ValueError("--jobs must be positive")
    sdk = sdk.resolve(strict=True)
    compiler = (sdk / "bin/hgcc").resolve(strict=True)
    actlize = actlize_revision(ROOT)
    output = output.resolve()
    output.mkdir(exist_ok=False)
    work = output / "work"
    work.mkdir()
    includes = [ROOT / "flashquant/affine", ROOT / "flashquant/include",
                ROOT / "third_party/actlize/include", ROOT / "third_party/actlize/tools/util/include",
                ROOT / "third_party/actlize/examples/common", sdk / "include"]
    flags = [str(compiler), *FLAGS, *("-I" + str(p) for p in includes), "-DQUACTLIZE_W4A16_CLASSIC_WEIGHTS=0"]
    env = dict(os.environ, PATH=str(sdk / "bin") + os.pathsep + os.environ.get("PATH", ""),
               LD_LIBRARY_PATH=str(sdk / "lib") + os.pathsep + os.environ.get("LD_LIBRARY_PATH", ""))
    sources = generate(work, ids, configs)
    objects = [work / (src.stem + ".o") for src in sources]
    commands = [[*flags, "-c", str(src), "-o", str(obj)] for src, obj in zip(sources, objects)]
    library = output / "libflashquant.so"
    link = ["g++", "-shared", "-Wl,-Bsymbolic", "-Wl,-z,defs", *map(str, objects),
            "-L" + str(sdk / "lib"), *("-l" + name for name in LIBRARIES), "-o", str(library)]
    (work / "commands.json").write_text(json.dumps([*commands, link], indent=2) + "\n")

    def run(command):
        log = work / (Path(command[-1]).name + ".log")
        with log.open("w") as stream:
            rc = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT).returncode
        if rc:
            tail = "\n".join(log.read_text(errors="replace").splitlines()[-10:])
            raise RuntimeError(f"native build failed (rc={rc}): {log}\n{tail}")

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for done, _ in enumerate(pool.map(run, commands), 1):
            print(f"FlashQuant: {done}/{len(commands)} objects", flush=True)
    run(link)
    header = output / "include/flashquant/affine/api.h"
    header.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "flashquant/affine/api.h", header)
    source_files = [p for p in (ROOT / "flashquant").rglob("*") if p.suffix in
                    {".h", ".hpp", ".cuh", ".cu", ".cpp", ".py", ".inc", ".inl"}]
    manifest = {
        "arch": "ppu_10", "abi": 1, "group_size": 32, "mapping_id": "0x51344b5034540001",
        "quantization": "unsigned affine INT4; FP16 input/weights/output; FP32 accumulation and reduction",
        "revision": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "actlize": actlize, "sdk_release": (sdk / "release.yaml").read_text().strip(),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sorted([*source_files, Path(__file__).resolve()])},
        "selection": describe(ids), "configurations": list(ids), "library": library.name,
        "library_sha256": sha(library), "header_sha256": sha(header),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"FlashQuant: {library} (sha256={manifest['library_sha256']})", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, default=Path(os.environ.get("PPU_SDK", "/usr/local/PPU_SDK")))
    parser.add_argument("--output", type=Path, default=ROOT / "build", help="new output directory")
    parser.add_argument("--configs", help="optional comma-separated subset of shipping IDs")
    parser.add_argument("--relax-m1", action="store_true",
                        help="also build dynamic-M twins (explicit ID=10000+original); keep default selection")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    ids = PRODUCTION_CONFIGS if args.configs is None else [int(i) for i in args.configs.split(",")]
    build(args.sdk, args.output, ids, args.jobs, relax_m1=args.relax_m1)


if __name__ == "__main__":
    main()
