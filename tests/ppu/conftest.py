"""Device tests are opt-in via an explicit test path, and fail on missing setup."""
import ctypes as C
import os
from pathlib import Path

import pytest

from flashquant.affine import Library
from .support import SDK


@pytest.fixture(scope="session")
def affine_library():
    return Library()


@pytest.fixture(scope="session")
def sdk():
    rt = SDK(Path(os.environ.get("PPU_SDK", "/usr/local/PPU_SDK")))
    pointer = C.c_void_p
    for name, args in {
        "hggcStreamCreateWithFlags": [C.POINTER(pointer), C.c_uint],
        "hggcStreamDestroy": [pointer],
        "hggcStreamBeginCapture": [pointer, C.c_int],
        "hggcStreamEndCapture": [pointer, C.POINTER(pointer)],
        "hggcGraphInstantiateWithFlags": [C.POINTER(pointer), pointer, C.c_uint64],
        "hggcGraphLaunch": [pointer, pointer],
        "hggcGraphExecDestroy": [pointer],
        "hggcGraphDestroy": [pointer],
    }.items():
        function = getattr(rt.lib, name)
        function.argtypes, function.restype = args, C.c_int
    return rt
