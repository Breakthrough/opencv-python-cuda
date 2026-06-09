"""Probe whether cudacodec hardware decode/encode are actually compiled in.

Run from a neutral CWD (not the repo root) so the installed cv2 is used:
    cd %TEMP% && python <repo>\\tools\\probe_nvcodec.py
"""
import os
import tempfile

import cv2
import numpy as np

print("cv2:", cv2.__file__)
print("version:", cv2.__version__)
print("cudacodec present:", hasattr(cv2, "cudacodec"))

tmp = tempfile.mkdtemp(prefix="nvprobe_")
w, h, n = 320, 240, 30

# Make a CPU-encoded H.264/mp4 so the DECODE test does not depend on NVENC.
cpu_path = os.path.join(tmp, "cpu.mp4")
vw = cv2.VideoWriter(cpu_path, cv2.VideoWriter_fourcc(*"mp4v"), 30, (w, h))
for i in range(n):
    img = np.zeros((h, w, 3), np.uint8)
    img[:, (i * 8) % w:((i * 8) % w) + 20] = (0, 0, 255)
    vw.write(img)
vw.release()
print("cpu encode file:", os.path.getsize(cpu_path), "bytes")

# --- NVDEC decode probe ---
try:
    reader = cv2.cudacodec.createVideoReader(cpu_path)
    ok, frame = reader.nextFrame()
    print("NVDEC decode: OK  (ret=%s)" % ok)
except cv2.error as e:
    msg = str(e).splitlines()[0]
    print("NVDEC decode: FAILED ->", msg)

# --- NVENC encode probe ---
try:
    writer = cv2.cudacodec.createVideoWriter(
        os.path.join(tmp, "nv.mp4"), (w, h), cv2.cudacodec.H264)
    print("NVENC encode: OK (writer created)")
    writer.release()
except cv2.error as e:
    msg = str(e).splitlines()[0]
    print("NVENC encode: FAILED ->", msg)
