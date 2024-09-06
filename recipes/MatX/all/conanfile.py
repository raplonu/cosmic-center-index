from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.files import get, apply_conandata_patches
import os

class MatX(ConanFile):
    name = 'matx'
    homepage = 'https://nvidia.github.io/MatX/'
    description = 'A modern C++ library for numerical computing on NVIDIA GPUs and CPUs.'
    topics = 'hpc', 'gpu', 'cuda', 'gpgpu', 'gpu-computing'
    url = 'https://github.com/NVIDIA/MatX'
    license = 'BSD-3-Clause'
    settings = 'os', 'arch', 'compiler', 'build_type'

    exports_sources = 'patches/*',

    options = {
        'file_io':       [True, False],
        'cutensor':      [True, False],
        'cutlass':       [True, False],
        'visualization': [True, False],
        'multi_gpu':     [True, False],
        'nvtx':          [True, False],
        'cub_cache':     [True, False],
        'pybind11':      [True, False]
    }

    default_options = {
        'file_io':       False,
        'cutensor':      False,
        'cutlass':       False,
        'visualization': False,
        'multi_gpu':     False,
        'nvtx':          False,
        'cub_cache':     False,
        'pybind11':      False
    }

    def source(self):
        get(self, **self.conan_data['sources'][self.version], strip_root=True)

    # def requirements(self):
    #     if self.options.file_io:
    #         self.requires('pybind11/[>2.10.0]')

    generators = 'CMakeToolchain' #'CMakeDeps',

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)

        # variables cannot be set in the generate method because they are
        # declare before the project command in the Matx/CMakeLists.txt file.
        # Doing that make them not visible if placed in cmake_toolchain.cmake file by CMaketoolchain generator.
        vars = {
            'MATX_EN_FILEIO':         bool(self.options.file_io),
            'MATX_EN_CUTENSOR':       bool(self.options.cutensor),
            'MATX_EN_CUTLASS':        bool(self.options.cutlass),
            'MATX_EN_VISUALIZATION':  bool(self.options.visualization),
            'MATX_EN_MULTIGPU':       bool(self.options.multi_gpu),
            'MATX_EN_NVTX':           bool(self.options.nvtx),
            'MATX_DISABLE_CUB_CACHE': not self.options.cub_cache,
            'MATX_EN_PYBIND11':       bool(self.options.pybind11)
        }

        # Header only, so no need to build, but the configure is needed to generate the cmake files.
        cmake.configure(variables=vars)

    def package(self):
        cmake = CMake(self)
        # Install headers and cmake files.
        cmake.install()

    def package_info(self):
         # matx generates its own cmake files so we disable cmake files generations ...
         self.cpp_info.set_property('cmake_find_mode', 'none')
         # ... and adds existing files to cmake path.
         self.cpp_info.builddirs.append(os.path.join('lib', 'cmake', 'matx'))

         # For header-only packages, libdirs and bindirs are not used
         # so it's necessary to set those as empty.
         self.cpp_info.bindirs = []
         self.cpp_info.libdirs = []
