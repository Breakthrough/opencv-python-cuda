# opencv-python-cuda

**Pre-built NVIDIA&reg; CUDA&trade; enabled OpenCV wheels for Python - batteries included.**

[![Latest release](https://img.shields.io/github/v/release/Breakthrough/opencv-python-cuda?include_prereleases&label=release)](https://github.com/Breakthrough/opencv-python-cuda/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20x64-blue)](https://github.com/Breakthrough/opencv-python-cuda/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](#licensing)

This is a fork of the official [opencv-python](https://github.com/opencv/opencv-python) project that ships fully standalone CUDA-enabled OpenCV builds. No CUDA Toolkit, cuDNN, or other NVIDIA SDK needs to be installed - every required runtime library is bundled in the wheel, including hardware video decoding and encoding (NVDEC/NVENC). Once installed, the following should *just work*:

```python
import cv2
print(cv2.cuda.getCudaEnabledDeviceCount())
```

See the [project homepage](https://breakthrough.github.io/opencv-python-cuda/) for more documentation.

## Requirements

- **Windows x64** (the only platform packages are currently produced for)
- **NVIDIA GPU** - Maxwell class (GeForce GTX 900 series) or newer
- **NVIDIA driver** - the wheel links directly against driver libraries, so an up-to-date driver must be installed for `import cv2` to succeed
- **Python 3.7 or newer** - a single abi3 wheel covers all supported Python versions

## Installation

1. Download the latest `opencv_python_cuda-*-win_amd64.whl` from the [Releases page](https://github.com/Breakthrough/opencv-python-cuda/releases).
2. Install it with `pip` (or another package manager like `uv`):

   ```
   pip install opencv_python_cuda-<version>-win_amd64.whl
   ```

3. Import the `cv2` package as usual.

> [!NOTE]
> If you have a previous manually-installed (not via `pip`) version of OpenCV (e.g. a `cv2` module in the root of Python's site-packages), remove it before installing to avoid conflicts. Also make sure your `pip` is up to date (19.3 is the minimum supported version): `pip install --upgrade pip`.

## What's included

- All OpenCV modules that can be built with CUDA support
- Hardware-accelerated video decoding and encoding via NVDEC/NVENC (`cv2.cudacodec`)
- FFmpeg for video I/O
- All required CUDA runtime libraries, bundled in the wheel

Non-free algorithms (e.g. SURF) are excluded - see the FAQ below.

## Documentation

- [Project homepage](https://breakthrough.github.io/opencv-python-cuda/) - downloads and overview
- [CUDA Compatibility Reference](https://breakthrough.github.io/opencv-python-cuda/cuda-compatibility.html) - GPU architectures, compute capabilities, and CUDA toolkit support
- [Workflow Guide](https://breakthrough.github.io/opencv-python-cuda/workflow.html) - repository setup, triggering builds, and wheel size strategy

## Frequently Asked Questions

For general OpenCV questions, refer to [the FAQ in the upstream project](https://github.com/opencv/opencv-python/?tab=readme-ov-file#frequently-asked-questions).

**Q: Why can't I `pip install opencv-python-cuda` from PyPI?**

A: The package is far too large for PyPI and exceeds its [project size limits](https://docs.pypi.org/project-management/storage-limits/). Download wheels from the [Releases page](https://github.com/Breakthrough/opencv-python-cuda/releases) instead.

**Q: Why does `import cv2` fail with "DLL load failed"?**

A: The wheel requires an NVIDIA driver to be installed. On machines without one (or with a very old driver), the bundled CUDA and video codec libraries cannot be loaded.

**Q: Why are non-free algorithms excluded?**

A: Non-free algorithms such as SURF are patented and cannot be distributed as built binaries. Note that SIFT *is* included, due to patent expiration as of OpenCV 4.3.0 / 3.4.10. See [opencv-python#126](https://github.com/skvark/opencv-python/issues/126) for more info.

## Licensing

The opencv-python-cuda package (i.e. the scripts in this repository) is available under the MIT license.

- OpenCV itself is available under the [Apache 2](https://github.com/opencv/opencv/blob/master/LICENSE) license.
- All wheels are distributed with [FFmpeg](http://ffmpeg.org), licensed under the [LGPLv2.1](http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html), and redistributable portions of the NVIDIA&reg; CUDA&trade; SDK under the [NVIDIA Software License Agreement (EULA)](https://docs.nvidia.com/cuda/eula/index.html).
- The packages include other binaries as well; the full list of licenses can be found in [LICENSE-3RD-PARTY.txt](https://github.com/opencv/opencv-python/blob/master/LICENSE-3RD-PARTY.txt).

By downloading and using the software, you agree to fully comply with the terms and conditions of the CUDA EULA.
