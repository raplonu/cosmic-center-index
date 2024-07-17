from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, rm, replace_in_file
import os
from copy import deepcopy

class Milk(ConanFile):
    name = 'milk'
    homepage = 'https://milk-org.github.io/milk/'
    description = 'Image processing functions, optimized for execution speed and high speed I/O'
    topics = 'real-time' 'fps' 'astronomy' 'image-processing' 'image-analysis' 'processinfo'
    url = 'https://github.com/milk-org/milk'
    license = 'BSD-3-Clause'
    settings = 'os', 'arch', 'compiler', 'build_type'

    exports_sources = 'CMakeLists.txt'

    options = {
        'cuda': [True, False],
        'magma': [True, False],
        'max_semaphore': ['ANY'],
        # 'file_io':       [True, False],
        # 'cutensor':      [True, False],
        # 'cutlass':       [True, False],
        # 'visualization': [True, False],
        # 'multi_gpu':     [True, False],
        # 'nvtx':          [True, False],
        # 'cub_cache':     [True, False],
        # 'pybind11':      [True, False]
    }

    default_options = {
        'cuda': False,
        'magma': False,
        'max_semaphore': '10',
        # 'file_io':       False,
        # 'cutensor':      False,
        # 'cutlass':       False,
        # 'visualization': False,
        # 'multi_gpu':     False,
        # 'nvtx':          False,
        # 'cub_cache':     False,
        # 'pybind11':      False
    }

    def source(self):
        # Just in case, do not modify the original conan_data.
        milk_data = deepcopy(self.conan_data["sources"][self.version])
        image_stream_io_data = milk_data.pop('image_stream_io')

        get(self, **milk_data, destination='milk', strip_root=True)
        get(self, **image_stream_io_data, strip_root=True, destination='milk/src/ImageStreamIO')

        rm(self, "milk/src/milk_config.h", self.source_folder)
        rm(self, "milk/src/milk/plugins/milk-extra-src", self.source_folder)


    # Cannot be optional (link to the use of cuda or not).
    python_requires = 'conan_cuda/1.0.0'

    def generate(self):
        milk_dir = os.path.join(self.source_folder, 'milk')

        if self.options.cuda:
            replace_in_file(self, os.path.join(milk_dir, 'src', 'ImageStreamIO', 'ImageStruct.h'),
                        'GPU_IMAGE_PLACEHOLDER    0', 'GPU_IMAGE_PLACEHOLDER  128')

        max_semaphore = int(self.options.max_semaphore)
        if max_semaphore != 10:
            replace_in_file(self, os.path.join(milk_dir, 'src', 'ImageStreamIO', 'ImageStruct.h'),
                        'SEMAPHORE_MAXVAL        10', f'SEMAPHORE_MAXVAL {max_semaphore}')

        # Why ?
        replace_in_file(self, os.path.join(milk_dir, 'scripts', 'milk-procCTRL'),
            'milk -n ', 'milk -p 49 -n ')


        tc = CMakeToolchain(self)

        tc.variables['GIT_SUBMODULE'] = False
        tc.variables['build_python_module'] = False

        tc.variables['USE_CUDA'] = self.options.cuda
        tc.variables['USE_MAGMA'] = self.options.magma

        tc.generate()

    def build(self):
        cmake = CMake(self)

        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        # Install headers and cmake files.
        cmake.install()

    def package_info(self):
        self.cpp_info.components['CLIcore'].libs = [
            'milkCOREMODarith',
            'milkCOREMODmemory',
            'CLIcore',
            'milkCOREMODiofits',
            'milkCOREMODtools'
        ]
        self.cpp_info.components['CLIcore'].includedirs += [
            'include/CommandLineInterface'
        ]

        self.cpp_info.components['ImageStreamIO'].libs = [
            'ImageStreamIO'
        ]
        self.cpp_info.components['ImageStreamIO'].includedirs += [
            'include/ImageStreamIO'
        ]
        if self.options.cuda:
            cuda_prop = self.python_requires['conan_cuda'].module.properties()

            self.cpp_info.components['ImageStreamIO'].defines = ['HAVE_CUDA']
            self.cpp_info.components['ImageStreamIO'].system_libs = ['cuda', 'cudart']
            self.cpp_info.components['ImageStreamIO'].libdirs += [cuda_prop.library]
            self.cpp_info.components['ImageStreamIO'].includedirs += [cuda_prop.include]

