"""PPU test utilities only; no GGUF runtime dependency."""
import ctypes as C
from pathlib import Path

import numpy as np


def checked(status, operation):
    if status:
        raise RuntimeError(f"{operation} failed: status={status}")


class SDK:
    def __init__(self, path):
        self.lib = C.CDLL(
            str(Path(path) / "lib/libhggc_wrapper.so"), mode=C.RTLD_GLOBAL
        )
        bindings = {
            "hggcMalloc": ([C.POINTER(C.c_void_p), C.c_size_t], C.c_int),
            "hggcFree": ([C.c_void_p], C.c_int),
            "hggcMemcpy": ([C.c_void_p, C.c_void_p, C.c_size_t, C.c_int], C.c_int),
            "hggcMemset": ([C.c_void_p, C.c_int, C.c_size_t], C.c_int),
            "hggcStreamSynchronize": ([C.c_void_p], C.c_int),
        }
        for name, (args, result) in bindings.items():
            fn = getattr(self.lib, name)
            fn.argtypes = args
            fn.restype = result

    def allocate(self, size):
        pointer = C.c_void_p()
        checked(self.lib.hggcMalloc(C.byref(pointer), size), "allocation")
        return pointer.value

    def free(self, pointer):
        if pointer:
            checked(self.lib.hggcFree(pointer), "free")

    def download(self, pointer, size):
        host = C.create_string_buffer(size)
        checked(self.lib.hggcMemcpy(host, pointer, size, 2), "D2H")
        return host.raw

    def fill(self, pointer, byte, size):
        checked(self.lib.hggcMemset(pointer, byte, size), "memset")

    def synchronize(self, stream):
        checked(self.lib.hggcStreamSynchronize(stream), "synchronize")


class Buffer:
    def __init__(self, arena, size):
        self.arena, self.size = arena, int(size)
        self.base = arena.sdk.allocate(self.size + 512)
        self.ptr = self.base + 256
        arena.buffers.append(self)
        assert self.ptr % 256 == 0
        arena.sdk.fill(self.base, 0xA5, self.size + 512)

    def write(self, value):
        value = np.ascontiguousarray(value)
        assert value.nbytes == self.size
        checked(self.arena.sdk.lib.hggcMemcpy(self.ptr, value.ctypes.data, value.nbytes, 1), "test upload")

    def guard(self):
        sdk = self.arena.sdk
        assert sdk.download(self.base, 256) == b"\xa5" * 256
        assert sdk.download(self.ptr + self.size, 256) == b"\xa5" * 256

    def bytes(self):
        self.guard()
        return self.arena.sdk.download(self.ptr, self.size)

    def poison(self):
        self.arena.sdk.fill(self.ptr, 0xff, self.size)


class Arena:
    def __init__(self, sdk):
        self.sdk, self.buffers, self.streams = sdk, [], []

    def buffer(self, size):
        return Buffer(self, size)

    def upload(self, value):
        result = self.buffer(value.nbytes)
        result.write(value)
        return result

    def stream(self):
        stream = C.c_void_p()
        checked(self.sdk.lib.hggcStreamCreateWithFlags(C.byref(stream), 1), "CI stream")
        self.streams.append(stream)
        return stream

    def sync(self):
        # Setup H2D uses the default stream; make its dependency explicit.
        self.sdk.synchronize(None)
        for stream in self.streams:
            self.sdk.synchronize(stream)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.sync()
        for buf in reversed(self.buffers):
            self.sdk.free(buf.base)
        for stream in reversed(self.streams):
            checked(self.sdk.lib.hggcStreamDestroy(stream), "destroy CI stream")


class Replay:
    def __init__(self, sdk, stream, launch, repeats):
        self.sdk, self.stream = sdk, stream
        self.graph, self.instance = C.c_void_p(), C.c_void_p()
        checked(sdk.lib.hggcStreamBeginCapture(stream, 0), "begin capture")
        try:
            for _ in range(repeats):
                checked(launch(), "capture selected call")
        except BaseException:
            sdk.lib.hggcStreamEndCapture(stream, C.byref(self.graph))
            self.close()
            raise
        checked(
            sdk.lib.hggcStreamEndCapture(stream, C.byref(self.graph)), "end capture"
        )
        try:
            checked(
                sdk.lib.hggcGraphInstantiateWithFlags(
                    C.byref(self.instance), self.graph, 0
                ),
                "instantiate",
            )
        except BaseException:
            self.close()
            raise

    def __call__(self):
        return self.sdk.lib.hggcGraphLaunch(self.instance, self.stream)

    def close(self):
        if self.instance:
            checked(
                self.sdk.lib.hggcGraphExecDestroy(self.instance),
                "destroy graph instance",
            )
            self.instance = C.c_void_p()
        if self.graph:
            checked(self.sdk.lib.hggcGraphDestroy(self.graph), "destroy graph")
            self.graph = C.c_void_p()
