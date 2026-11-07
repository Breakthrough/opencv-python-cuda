PYTHON_EXTENSIONS_PATHS = [
    LOADER_DIR
] + PYTHON_EXTENSIONS_PATHS

# The bundled CUDA/cuDNN DLLs live next to cv2.pyd. cuDNN 9's cudnn64_9.dll loads its
# sub-libraries (cudnn_graph64_9.dll, cudnn_cnn64_9.dll, ...) with LoadLibrary at runtime,
# which does not search the calling DLL's directory, so the DNN CUDA backend aborts the
# process ("Cannot load symbol cudnnGetVersion") unless the package dir is on PATH.
# The loader adds every BINARIES_PATHS entry to the DLL search path and PATH.
BINARIES_PATHS = [
    LOADER_DIR
] + BINARIES_PATHS
