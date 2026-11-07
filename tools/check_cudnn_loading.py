"""Verify the installed cv2 package can load cuDNN 9's sub-libraries at runtime.

cuDNN 9 is split into a small front DLL (cudnn64_9.dll) that cv2.pyd links against
and several sub-libraries (cudnn_graph64_9.dll, cudnn_ops64_9.dll, ...) that the
front DLL loads by name with LoadLibrary the first time a cuDNN function is called.
Those runtime loads do not search the cv2 package directory, so they only succeed if
the OpenCV loader put that directory on the DLL search path / PATH (via
BINARIES_PATHS in cv2/config*.py). When they fail, cuDNN prints "Cannot load symbol
cudnnGetVersion" and terminates the process (exit 127) instead of raising.

PE import analysis (tools/check_codec_linked.py) cannot see these loads, and the CI
runners have no GPU/driver so `import cv2` is impossible. This check needs neither:
none of the cuDNN DLLs import the NVIDIA driver, and the version-check entry points
do not touch the GPU. It reproduces the loader's path setup without importing cv2,
then loads cudnn64_9.dll with ctypes in a child process (so an abort is reported as
a failure) and calls each sub-library's version check, forcing every one to load.

Run it from a directory that is NOT the repo root (the repo has a cv2/ stub dir):

    python tools/check_cudnn_loading.py            # locate installed cv2 via sys.path
    python tools/check_cudnn_loading.py <cv2-dir>  # or point at a package dir
"""

import importlib.util
import os
import subprocess
import sys

# Child process: mimic cv2/__init__.py's DLL path setup, then exercise cuDNN.
CHILD = r"""
import ctypes, os, sys
cv2_dir = sys.argv[1]
paths = sys.argv[2:]
for p in paths:
    try:
        os.add_dll_directory(p)
    except OSError:
        pass
os.environ["PATH"] = ";".join(paths) + ";" + os.environ.get("PATH", "")
lib = ctypes.WinDLL(os.path.join(cv2_dir, "cudnn64_9.dll"))
lib.cudnnGetVersion.restype = ctypes.c_size_t
print("cudnnGetVersion() = %d" % lib.cudnnGetVersion())
failed = 0
for fn in ("cudnnGraphVersionCheck", "cudnnOpsVersionCheck",
           "cudnnCnnVersionCheck", "cudnnAdvVersionCheck"):
    f = getattr(lib, fn, None)
    if f is None:
        print("%s: not exported, skipped" % fn)
        continue
    status = f()
    print("%s() = %d %s" % (fn, status, "OK" if status == 0 else "FAIL"))
    failed += status != 0
print("CHILD_DONE")
sys.exit(1 if failed else 0)
"""


def find_cv2_dir():
    spec = importlib.util.find_spec("cv2")
    if spec is None or not spec.submodule_search_locations:
        sys.exit("cv2 package not found on sys.path")
    return os.path.abspath(list(spec.submodule_search_locations)[0])


def loader_binaries_paths(cv2_dir):
    """Evaluate cv2/config.py + config-3[.x].py the way cv2/__init__.py does."""
    scope = {
        "LOADER_DIR": cv2_dir,
        "PYTHON_EXTENSIONS_PATHS": [],
        "BINARIES_PATHS": [],
        "os": os,
        "sys": sys,
    }
    major, minor = sys.version_info[:2]
    candidates = [["config.py"], ["config-%d.%d.py" % (major, minor), "config-%d.py" % major]]
    for names in candidates:
        for name in names:
            path = os.path.join(cv2_dir, name)
            if os.path.exists(path):
                with open(path) as f:
                    exec(compile(f.read(), path, "exec"), scope)
                break
        else:
            sys.exit("missing loader config: %s" % " / ".join(names))
    return [os.path.abspath(p) for p in scope["BINARIES_PATHS"]]


def main():
    if os.name != "nt":
        print("SKIP: Windows-only check")
        return 0
    cv2_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else find_cv2_dir()
    print("cv2 package dir: %s" % cv2_dir)
    if not os.path.exists(os.path.join(cv2_dir, "cudnn64_9.dll")):
        print("FAIL: cudnn64_9.dll is not bundled in the cv2 package")
        return 1

    paths = loader_binaries_paths(cv2_dir)
    print("loader BINARIES_PATHS:")
    for p in paths:
        print("  %s" % p)

    # Minimal PATH so a cuDNN install elsewhere on the machine cannot mask a failure.
    sysroot = os.environ.get("SystemRoot", r"C:\Windows")
    env = dict(os.environ)
    env["PATH"] = ";".join([os.path.join(sysroot, "System32"), sysroot])
    proc = subprocess.run(
        [sys.executable, "-I", "-c", CHILD, cv2_dir] + paths,
        cwd=os.path.dirname(sys.executable), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
    )
    print(proc.stdout.rstrip())
    if proc.returncode != 0 or "CHILD_DONE" not in proc.stdout:
        print("FAIL: cuDNN could not load its sub-libraries (exit code %d). Is the cv2 "
              "package directory in BINARIES_PATHS (scripts/__init__.py)?" % proc.returncode)
        return 1
    print("PASS: cuDNN sub-libraries load from the cv2 package directory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
