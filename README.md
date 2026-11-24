# FlashQuant

Native PPU weight-only GEMM for ordinary affine INT4 (W4A16, group size 32).
This is the implementation compared against Humming on ZW810E, **not** a
wrapper around Humming. GGUF block types, file loading and GGUF model routing
belong to [FlashGGUF](https://github.com/DrXuQian/FlashGGUF/tree/develop).
Neither project needs the other's checkout or shared library to build.

[SIMT GEMV](flashquant/simt_gemv/) is separate from the affine Tensor Core
implementation. All current shipping configurations, including M=1, use TC.

## Build and test

On a PPU1.0 box with a configured PPU SDK and a C++17 host compiler:

```sh
git clone --recurse-submodules https://github.com/DrXuQian/FlashQuant.git
cd FlashQuant
python3 tools/build_affine.py --sdk "${PPU_SDK:-/usr/local/PPU_SDK}" --output build --jobs 8
python3 -m pip install -e '.[test]'
python3 -m pytest -q                 # Host: ABI, selector, schedule, byte packing
python3 -m pytest -q tests/ppu       # Real library + PPU: accuracy and graph replay
```

Use a **new** output directory per build. The default builds the 96 production
configurations for `ppu_10`; an explicit `--configs ID[,ID...]` produces a
subset of those 96, not a complete selector. There are two kernel families:
95 warp-K configurations and one cohort configuration (public ID 45).
The [shipping configuration table](flashquant/affine/configs.py) names C++
options; the [selector](flashquant/affine/selection.py) alone owns exact
shape matches and fallbacks. Its `MEASURED` map lists the observed M values
by (zero mode, N, K); an unlisted M uses `FALLBACKS`, even between two
measurements with the same winner. The full R4 sweep catalog and its controls
are preserved on [the experiment branch](https://github.com/DrXuQian/FlashQuant/tree/experiments/affine-sweep).
The deliverables are
`build/libflashquant.so`, `build/include/flashquant/affine/api.h` and the
build receipt `build/manifest.json`. Installing the Python bindings does
not compile or install the DSO. For a custom build directory or installed
bindings, set `FLASHQUANT_LIBRARY` to the absolute path of the DSO or pass
that path to `flashquant.affine.Library(path)`.

## Calling contract

For a bounded experiment, `--configs 535,625 --relax-m1` also builds
explicit IDs 10535 and 10625. They retain the original N/K, warp-K and
zero-point policy, but use runtime M, predicated stores and a real M-grid.
Neither the original M=1 binaries nor the automatic selector are replaced.
Pruned rows, compact output, Stream-K and cross-CTA slices are not relaxed.
Run `python3 -m pytest -q tests/ppu/test_affine.py -k dynamic_m_twins` on this build.

| Buffer | Type and logical shape |
| --- | --- |
| Host weight codes | `uint8[N,K]`, each in 0…15; `pack_host_v1` produces exactly `N*K/2` bytes |
| Device input / output | contiguous `FP16[M,K]` / `FP16[M,N]` |
| Scales / optional zero points | `FP16[K/32,N]` / `uint8[K/32,N]`; symmetric mode uses 8 |

`M > 0`; N and K must be positive multiples of 256. Reconstruct
`FP16((code - zero) * scale)`, then multiply with FP32 accumulation/reduction.
This is not the scale/min arithmetic of GGUF Q4_K.

Include `<flashquant/affine/api.h>` and link `-lflashquant`, or import
`Library, Buffers, Info, problem` from `flashquant.affine`. The existing
`quactlize_ppu_w4a16_*_v1` C symbols and structure layouts are preserved.
Query with `config=-1` for the default selector, allocate the returned
workspace (256-byte alignment), then prepare outside capture. Keep data
(16-byte aligned), plan and exclusive scratch alive until execution completes.
`run` does not allocate, JIT or synchronize. Inputs can change between graph
replays; changing bound addresses requires a new prepare.

## Provenance

Extracted from [FlashGGUF 537d7351](https://github.com/DrXuQian/FlashGGUF/commit/537d7351535ea7c5df58605db6658c4b78e0e520).
The selector, kernel sources, required C++ headers and pinned actlize revision
are retained. Some shared headers declare GGUF types; they are compile-time
dependencies, not GGUF entry points. Source notices and licenses are preserved.

The [R4 measurements](https://github.com/DrXuQian/FlashQuant/blob/experiments/affine-sweep/docs/evidence/affine-810e-r4-results.json) and
[integration receipt](https://github.com/DrXuQian/FlashQuant/blob/experiments/affine-sweep/docs/evidence/affine-810e-r4-integration.json) refer to
the **original** binary. Of 126 shapes, 86 had comparable Humming FP32
accumulation/reduction. Those results are not new timings for this DSO.
