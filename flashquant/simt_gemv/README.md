# SIMT GEMV boundary

There is no shipping SIMT GEMV in FlashQuant yet. M=1 uses the same affine
Tensor Core selector as larger M; neither warp-K nor cohort is a SIMT GEMV.
This directory is intentionally not a build, dispatch or Python entry point.

A future SIMT reader belongs here and must consume FlashQuant's packed codes
and group-32 scales/integer zero points. The GGUF and legacy lowbit readers
use other buffer or arithmetic contracts; do not register them under this ABI.
