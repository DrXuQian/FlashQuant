import ctypes as C
import os
from pathlib import Path

class Problem(C.Structure):
    _fields_ = [("version", C.c_uint32), ("size", C.c_uint32)] + [
        (name, C.c_int32) for name in ("m", "n", "k", "group_size", "config", "split", "zero_mode")
    ]


class Buffers(C.Structure):
    _fields_ = [("version", C.c_uint32), ("size", C.c_uint32)] + [
        (name, C.c_void_p) for name in ("input", "weight", "scales", "zeros", "output", "workspace")
    ] + [("workspace_bytes", C.c_uint64), ("stream", C.c_void_p)]


class Config(C.Structure):
    _fields_ = [("version", C.c_uint32), ("size", C.c_uint32)] + [
        (name, C.c_int32) for name in ("id", "tm", "tn", "tk", "wm", "wn", "stages")
    ]


class Info(C.Structure):
    _fields_ = [("version", C.c_uint32), ("size", C.c_uint32),
                ("workspace_bytes", C.c_uint64), ("shared_bytes", C.c_uint64),
                ("threads", C.c_int32), ("reserved", C.c_int32)]


def problem(m, n, k, *, group_size=32, config=-1, split=1, zero_mode=0):
    values = (m, n, k, group_size, config, split, zero_mode)
    if any(type(value) is not int for value in values):
        raise ValueError("W4A16 problem fields must be integers")
    if m <= 0 or n <= 0 or k <= 0 or n % 256 or k % 256:
        raise ValueError("W4A16 requires positive M and N/K multiples of 256")
    if max(m * n, m * k, n * k) > 2**31 - 1:
        raise ValueError("W4A16 extent exceeds indexing range")
    if group_size != 32 or zero_mode not in (0, 1):
        raise ValueError("unsupported W4A16 quantization contract")
    if not -1 <= config <= 2**31-1 or split not in (1, 2, 4, 8):
        raise ValueError("unsupported W4A16 candidate")
    return Problem(1, C.sizeof(Problem), *values)


class Library:
    def __init__(self, path=None):
        if path is None:
            path = os.environ.get("FLASHQUANT_LIBRARY") or Path(__file__).resolve().parents[2] / "build/libflashquant.so"
        self.path = Path(path).resolve(strict=True)
        self.lib = C.CDLL(str(self.path), mode=C.RTLD_LOCAL)
        functions = {
            "mapping": ([], C.c_uint64),
            "config_count": ([], C.c_int),
            "config": ([C.c_int, C.POINTER(Config)], C.c_int),
            "pack_host": ([C.c_void_p, C.c_int32, C.c_int32, C.c_void_p, C.c_uint64], C.c_int),
            "query": ([C.POINTER(Problem), C.POINTER(Info)], C.c_int),
            "prepare": ([C.POINTER(Problem), C.POINTER(Buffers), C.POINTER(C.c_void_p)], C.c_int),
            "run": ([C.c_void_p, C.c_void_p], C.c_int),
            "destroy": ([C.c_void_p], None),
            "error": ([], C.c_char_p),
        }
        for name, (arguments, result) in functions.items():
            function = getattr(self.lib, "quactlize_ppu_w4a16_" + name + "_v1")
            function.argtypes, function.restype = arguments, result
            setattr(self, name, function)
        self.config_zero_mode = getattr(self.lib, "quactlize_ppu_w4a16_config_zero_mode_v1", None)
        if self.config_zero_mode is not None:
            self.config_zero_mode.argtypes = [C.c_int, C.POINTER(C.c_int32)]
            self.config_zero_mode.restype = C.c_int
        self.select = getattr(self.lib, "quactlize_ppu_w4a16_select_v1", None)
        if self.select is not None:
            self.select.argtypes = [C.POINTER(Problem),C.POINTER(Config)]
            self.select.restype = C.c_int

    def check(self, status):
        if status:
            raise RuntimeError(f"W4A16 status={status}: {self.error().decode(errors='replace')}")

    def configurations(self):
        values = []
        for index in range(self.config_count()):
            item = Config()
            self.check(self.config(index, C.byref(item)))
            value = {name: getattr(item, name) for name, _ in Config._fields_[2:]}
            mode = C.c_int32()
            if self.config_zero_mode is not None:
                self.check(self.config_zero_mode(index, C.byref(mode)))
            value["zero_mode"] = mode.value
            values.append(value)
        return values

    def selected_config(self, p):
        if self.select is None:
            raise RuntimeError("This native build predates W4A16 default selection")
        selected=Config()
        self.check(self.select(C.byref(p),C.byref(selected)))
        return {name:getattr(selected,name) for name,_ in Config._fields_[2:]}
