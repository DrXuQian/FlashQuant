"""Native PPU accuracy and changed-input graph replay for the standalone DSO."""
import ctypes as C
import json

import numpy as np
import pytest

from flashquant.affine.configs import CONFIGS
from .support import Arena, Replay


def test_affine_native_specializations(affine_library):
    from flashquant.affine.native import Info as AffineInfo, problem
    library=affine_library
    checked=0
    for config in library.configurations():
        index=config["id"]
        spec = CONFIGS[index]
        sn, sk = spec.value("StaticN"), spec.value("StaticK")
        if spec.family != "CooperativeKernel":
            continue
        n,k=sn or 1024,sk or 3072
        workers=spec.value("StreamKWorkers")
        m=spec.value("StaticM") or (512 if workers else 16)
        mode=config["zero_mode"]
        split=spec.value("GlobalSlices")
        p=problem(m,n,k,config=index,split=split,zero_mode=mode)
        info=AffineInfo()
        library.check(library.query(C.byref(p),C.byref(info)))
        assert info.threads>0 and 0<info.shared_bytes<=262144
        wrong_mode=problem(m,n,k,config=index,split=split,zero_mode=1-mode)
        assert library.query(C.byref(wrong_mode),C.byref(AffineInfo()))!=0
        assert b"quantization mode" in library.error()
        if spec.value("StaticM"):
            rejected=problem(m+1,n,k,config=index,split=split,zero_mode=mode)
            assert library.query(C.byref(rejected),C.byref(AffineInfo()))!=0
            assert b"specialized M" in library.error()
        elif split==1 and not workers:
            # An explicit zero denotes dynamic M, just like an absent entry.
            dynamic=problem(m+1,n,k,config=index,split=split,zero_mode=mode)
            library.check(library.query(C.byref(dynamic),C.byref(AffineInfo())))
        for wrong_n,wrong_k in ([(n+256,k)] if sn else [])+([(n,k+512)] if sk else []):
            rejected=problem(m,wrong_n,wrong_k,config=index,split=split,zero_mode=mode)
            assert library.query(C.byref(rejected),C.byref(AffineInfo()))!=0
            assert b"specialized" in library.error()
        checked+=1
    assert checked>0,"the supplied native build contains no specialized kernels"


def test_affine_native_default_selection(affine_library):
    from flashquant.affine.native import Info as AffineInfo, Problem, problem
    library=affine_library
    available={config["id"]:config for config in library.configurations()}
    for mode in (0,1):
        for m,n,k in ((1,1024,3072),(12,2048,3072),(512,2048,3072),
                       (7,512,256),(24,3072,8192),(128,8192,8192)):
            p=problem(m,n,k,zero_mode=mode)
            selected=library.selected_config(p)
            assert available[selected["id"]]["zero_mode"]==mode
            automatic,explicit=AffineInfo(),AffineInfo()
            library.check(library.query(C.byref(p),C.byref(automatic)))
            forced=Problem.from_buffer_copy(p)
            forced.config=selected["id"]
            library.check(library.query(C.byref(forced),C.byref(explicit)))
            assert bytes(automatic)==bytes(explicit)
            assert p.config==-1


@pytest.mark.parametrize("mode",(0,1),ids=("symmetric","integer-zero"))
@pytest.mark.parametrize("shape",((7,512,256),(24,512,512),(128,512,256),
                                 (12,2048,3072),(512,2048,3072),(16,3072,1024)))
def test_affine_public_output_and_changed_graph(affine_library,sdk,mode,shape,record_property):
    from flashquant.affine import Buffers as AffineBuffers, Info as AffineInfo, problem
    library=affine_library
    m,n,k=shape
    rng=np.random.default_rng(1009+mode+m+n+k)
    codes=rng.integers(0,16,(n,k),dtype=np.uint8)
    scales=rng.uniform(.005,.025,(k//32,n)).astype(np.float16)
    zeros=rng.integers(0,16,(k//32,n),dtype=np.uint8) if mode else None
    center=zeros.T[...,None].astype(np.float32) if mode else 8
    golden=((codes.reshape(n,k//32,32).astype(np.float32)-center)*
            scales.T[...,None].astype(np.float32)).astype(np.float16).reshape(n,k).astype(np.float32)
    packed=np.empty(n*k//2,dtype=np.uint8)
    library.check(library.pack_host(codes.ctypes.data,n,k,packed.ctypes.data,packed.nbytes))
    p=problem(m,n,k,zero_mode=mode)
    selected=library.selected_config(p)
    info=AffineInfo()
    library.check(library.query(C.byref(p),C.byref(info)))
    record_property("affine_selected_config",str(selected["id"]))
    record_property("affine_checked_cells_per_replay",str(m*n))
    with Arena(sdk) as arena:
        weights=arena.upload(packed)
        scale=arena.upload(scales)
        zero=arena.upload(zeros) if mode else None
        inputs=arena.buffer(m*k*2)
        outputs=arena.buffer(m*n*2)
        workspace=arena.buffer(max(256,info.workspace_bytes))
        stream=arena.stream()
        arena.sync()
        buffers=AffineBuffers(1,C.sizeof(AffineBuffers),inputs.ptr,weights.ptr,scale.ptr,
                              zero.ptr if zero else None,outputs.ptr,workspace.ptr,
                              info.workspace_bytes,stream)
        handle=C.c_void_p()
        graph=None
        try:
            library.check(library.prepare(C.byref(p),C.byref(buffers),C.byref(handle)))
            if mode:
                # Integer-zero preparations own both metadata copies.
                scale.poison()
                zero.poison()
            def launch():
                return library.run(handle,stream)
            for repeat in range(3):
                source=rng.uniform(-.125,.125,(m,k)).astype(np.float16)
                inputs.write(source)
                outputs.poison()
                arena.sync()
                if repeat==1:
                    graph=Replay(sdk,stream,launch,1)
                library.check(graph() if graph else launch())
                arena.sync()
                got=np.frombuffer(outputs.bytes(),dtype=np.float16).reshape(m,n).astype(np.float32)
                reference=source.astype(np.float32)@golden.T
                assert np.isfinite(got).all()
                error=got-reference
                assert np.linalg.norm(error)/max(np.linalg.norm(reference),1e-12)<.001
                dot_norm=np.abs(source.astype(np.float32))@np.abs(golden).T
                assert np.max(np.abs(error)/np.maximum(dot_norm,1e-12))<.0005
                for allocation in arena.buffers:
                    allocation.guard()
        finally:
            arena.sync()
            if graph:
                graph.close()
            library.destroy(handle)


def test_affine_native_workspace_guards(affine_library,record_property):
    from flashquant.affine.native import Buffers as AffineBuffers, Info as AffineInfo, problem
    library=affine_library
    checked,fused=[],[]
    for config in library.configurations():
        index=config["id"]
        spec = CONFIGS[index]
        splits = spec.value("GlobalSlices")
        workers=spec.value("StreamKWorkers")
        n, k = spec.value("StaticN"), spec.value("StaticK")
        n,k=n or 1024,k or 3072
        m=spec.value("StaticM") or (512 if workers else 16)
        mode=config["zero_mode"]
        p=problem(m,n,k,config=index,split=splits,zero_mode=mode)
        info=AffineInfo()
        library.check(library.query(C.byref(p),C.byref(info)))
        if not info.workspace_bytes:
            continue
        assert info.workspace_bytes<=64*1024*1024
        if spec.value("PairedScales"):
            assert n*k//16<=info.workspace_bytes
        for field in ("input","weight","scales")+(("zeros",) if mode else ()):
            pointers=dict(input=0x10000000,weight=0x20000000,scales=0x30000000,
                          zeros=0x60000000 if mode else None)
            buffers=AffineBuffers(1,C.sizeof(AffineBuffers),pointers["input"],pointers["weight"],
                                  pointers["scales"],pointers["zeros"],0x40000000,pointers[field],
                                  info.workspace_bytes,None)
            handle=C.c_void_p()
            assert library.prepare(C.byref(p),C.byref(buffers),C.byref(handle))!=0
            assert not handle.value and b"workspace aliases" in library.error()
        buffers=AffineBuffers(1,C.sizeof(AffineBuffers),0x10000000,0x20000000,0x30000000,
                              0x60000000 if mode else None,0x40000000,0x50000000,
                              info.workspace_bytes-1,None)
        handle=C.c_void_p()
        assert library.prepare(C.byref(p),C.byref(buffers),C.byref(handle))!=0
        assert not handle.value and b"insufficient" in library.error()
        buffers.workspace_bytes=info.workspace_bytes
        buffers.zeros=None if mode else 0x60000000
        assert library.prepare(C.byref(p),C.byref(buffers),C.byref(handle))!=0
        assert not handle.value and b"invalid W4A16 pointers" in library.error()
        if workers or splits>1:
            partial_bytes=2*workers*config["tm"]*config["tn"]*4 if workers else splits*m*n*4
            assert partial_bytes<info.workspace_bytes
            if workers:
                larger=problem(1024,n,k,config=index,split=splits,zero_mode=mode)
                larger_info=AffineInfo()
                library.check(library.query(C.byref(larger),C.byref(larger_info)))
                assert larger_info.workspace_bytes==info.workspace_bytes
                if config["tm"]>=128:
                    undersupplied=problem(1,n,k,config=index,split=splits,zero_mode=mode)
                    assert library.query(C.byref(undersupplied),C.byref(AffineInfo()))!=0
                    assert b"contributors" in library.error()
            else:
                oversized=problem(config["tm"]+1,n,k,config=index,split=splits,zero_mode=mode)
                assert library.query(C.byref(oversized),C.byref(AffineInfo()))!=0
                assert b"one M tile" in library.error()
            fused.append(index)
        checked.append(index)
    assert checked,"the supplied native build contains no workspace-backed kernels"
    record_property("affine_workspace_configs",json.dumps(checked))
    record_property("affine_fused_partition_configs",json.dumps(fused))
