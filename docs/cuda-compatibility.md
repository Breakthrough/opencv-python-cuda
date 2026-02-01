# CUDA Compatibility Reference

## CUDA Toolkit vs Compute Capability Support

| CUDA Version | Min Compute | Max Compute | Notes |
|--------------|-------------|-------------|-------|
| 13.x | 7.5 | 12.0+ | Drops Maxwell, Pascal, Volta |
| 12.x | 5.0 | 10.0+ | Current LTS, drops Kepler |
| 11.x | 3.5 | 8.6+ | Legacy, includes Kepler |

## GPU Architectures

| Compute Capability | Architecture | Example GPUs | Released |
|--------------------|--------------|--------------|----------|
| 10.0 | Blackwell | RTX 50 series | 2025 |
| 9.0 | Hopper | H100, H200 | 2022 |
| 8.9 | Ada Lovelace | RTX 40 series | 2022 |
| 8.6 | Ampere (consumer) | RTX 30 series | 2020 |
| 8.0 | Ampere (datacenter) | A100, A30 | 2020 |
| 7.5 | Turing | RTX 20 series, GTX 16 series | 2018 |
| 7.0 | Volta | V100, Titan V | 2017 |
| 6.1 | Pascal (consumer) | GTX 10 series | 2016 |
| 6.0 | Pascal (datacenter) | P100 | 2016 |
| 5.2 | Maxwell v2 | GTX 900 series, Titan X | 2014 |
| 5.0 | Maxwell v1 | GTX 750 Ti | 2014 |
| 3.5 | Kepler | GTX 600/700 series | 2012 |

## SASS vs PTX

- **SASS** (Shader Assembly): Native GPU code, runs directly on matching architecture
- **PTX** (Parallel Thread Execution): Intermediate code, JIT-compiled at runtime

PTX is forward-compatible only (e.g. PTX 10.0 works on GPUs ≥10.0, not older). SASS is required for older GPUs that are lower than the PTX version. A GPU needs either matching SASS or older PTX which it can JIT compile.



## References

- [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)
- [CUDA GPUs - Compute Capability](https://developer.nvidia.com/cuda-gpus)
- [CuDNN Archive](https://developer.nvidia.com/cudnn-archive)
- [Video Codec SDK](https://developer.nvidia.com/video-codec-sdk)
