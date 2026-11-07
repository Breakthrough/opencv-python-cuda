"""Run a few small ONNX models on OpenCV's DNN CUDA backend (cuDNN) and check the output.

Needs an NVIDIA GPU + driver, so it is a local release check (like probe_nvcodec.py),
not a CI step. tools/check_cudnn_loading.py covers the GPU-less part in CI.

Models and reference outputs come from opencv_extra/testdata/dnn/onnx (the
opencv_extra submodule). Run it with the venv that has the wheel installed, from a
directory that is NOT the repo root (the repo has a cv2/ stub dir), unbuffered so
output survives if cuDNN aborts the process:

    python -u tools/probe_cudnn.py [<opencv_extra>/testdata/dnn/onnx]
"""

import os
import re
import sys

import numpy as np
import cv2

# The LSTM test models in opencv_extra fail in the ONNX importer itself (not cuDNN),
# so stick to convolution / normalization models.
MODELS = ["convolution", "two_convolution", "batch_norm"]
TOLERANCE = 1e-3


def main():
    default_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "opencv_extra", "testdata", "dnn", "onnx")
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else default_root)
    print("cv2: %s %s" % (cv2.__version__, cv2.__file__))
    for line in cv2.getBuildInformation().splitlines():
        if re.search(r"NVIDIA CUDA|cuDNN|NVIDIA GPU arch", line):
            print("  " + line.strip())
    devices = cv2.cuda.getCudaEnabledDeviceCount()
    print("CUDA devices: %d" % devices)
    if devices == 0:
        print("RESULT: FAIL (no CUDA device)")
        return 1
    # This is the call that aborted the process when cuDNN could not load its sub-libraries.
    targets = list(cv2.dnn.getAvailableTargets(cv2.dnn.DNN_BACKEND_CUDA))
    print("DNN CUDA targets: %s" % [int(t) for t in targets])
    if cv2.dnn.DNN_TARGET_CUDA not in targets:
        print("RESULT: FAIL (DNN_TARGET_CUDA unavailable)")
        return 1

    ok = True
    for name in MODELS:
        model = os.path.join(root, "models", name + ".onnx")
        inp = np.load(os.path.join(root, "data", "input_%s.npy" % name))
        ref = np.load(os.path.join(root, "data", "output_%s.npy" % name))
        net = cv2.dnn.readNet(model)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        net.setInput(inp)
        out = net.forward()
        err = float(np.max(np.abs(out.reshape(ref.shape) - ref)))
        good = err < TOLERANCE
        ok = ok and good
        print("  %-20s max_abs_err=%.2e %s" % (name, err, "OK" if good else "FAIL"))
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
