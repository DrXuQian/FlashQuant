"""Check the real C packer without a PPU; compute the expected words independently."""
import ctypes as C
from pathlib import Path
import struct
import subprocess

import pytest


@pytest.fixture(scope="module")
def pack(tmp_path_factory):
    root = Path(__file__).resolve().parents[1] / "flashquant"
    library = tmp_path_factory.mktemp("host-pack") / "pack.so"
    subprocess.run(["c++", "-std=c++17", "-shared", "-fPIC", "-O2", "-x", "c++",
                    "-I", str(root / "include"), str(root / "affine/pack.cu"),
                    "-o", str(library)], check=True)
    fn = C.CDLL(str(library)).quactlize_ppu_w4a16_pack_host_v1
    fn.argtypes = [C.c_void_p, C.c_int32, C.c_int32, C.c_void_p, C.c_uint64]
    fn.restype = C.c_int
    return fn


def test_kpack_codes_and_invalid_input(pack):
    n, k = 256, 512
    # Non-periodic across rows/groups; a transpose or swapped nibble is visible.
    from random import Random
    rng = Random(810)
    codes = bytearray(rng.randrange(16) for _ in range(n * k))
    source = (C.c_uint8 * len(codes)).from_buffer(codes)
    out = (C.c_uint8 * (n * k // 2))()
    assert pack(source, n, k, out, len(out)) == 0
    expected = bytearray()
    for group in range(0, k, 32):
        for residue in range(8):
            for row in range(n):
                base = row * k + group + residue
                word = sum(codes[base + 8 * i] << (4 * i) for i in range(4))
                expected.extend(struct.pack("<H", word))
    assert bytes(out) == expected
    codes[-1] = 16
    assert pack(source, n, k, out, len(out)) != 0
    assert bytes(out) == expected
    assert pack(source, n, k, source, len(out)) != 0
    assert pack(source, n, k, out, len(out) - 1) != 0
