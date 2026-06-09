"""Verify the installed cv2 extension module links the NVIDIA Video Codec DLLs.

Checks the PE import table of cv2*.pyd for nvcuvid.dll and nvEncodeAPI64.dll
WITHOUT importing cv2 (importing needs the NVIDIA driver DLLs, which are not
present on GPU-less CI runners). Exits nonzero if either DLL is missing, which
would mean the Video Codec SDK was not detected at build time and hardware
video decode/encode got silently compiled out.

Usage: python tools/check_codec_linked.py
Requires: pip install pefile
"""
import glob
import importlib.util
import os
import sys

import pefile

REQUIRED_DLLS = ("nvcuvid.dll", "nvencodeapi64.dll")


def main():
    spec = importlib.util.find_spec("cv2")
    if spec is None or not spec.submodule_search_locations:
        print("ERROR: cv2 package not found on sys.path")
        return 1
    pkg_dir = list(spec.submodule_search_locations)[0]
    print("cv2 package:", pkg_dir)

    pyds = glob.glob(os.path.join(pkg_dir, "cv2*.pyd"))
    if not pyds:
        print("ERROR: no cv2*.pyd in %s "
              "(resolved the source stub instead of the installed wheel?)" % pkg_dir)
        return 1
    pyd = pyds[0]
    print("extension module:", pyd)

    pe = pefile.PE(pyd, fast_load=True)
    pe.parse_data_directories(
        directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
    imports = sorted(
        entry.dll.decode("ascii", "replace").lower()
        for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []))
    pe.close()
    print("imported DLLs:")
    for name in imports:
        print("  " + name)

    missing = [d for d in REQUIRED_DLLS if d not in imports]
    if missing:
        print("FAIL: codec DLLs not linked: %s" % ", ".join(missing))
        return 1
    print("PASS: nvcuvid.dll and nvEncodeAPI64.dll are linked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
