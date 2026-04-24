import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get
from conan.tools.env import VirtualBuildEnv

class EmuConan(ConanFile):
    name = 'emu'

    license = 'MIT'
    author = 'Julien Bernard jbernard@obspm.fr'
    url = 'https://gitlab.obspm.fr/cosmic/tools/emu'
    description = 'Set of utilities for C++, CUDA and python'

    settings = 'os', 'compiler', 'build_type', 'arch'

    exports_sources = 'CMakeLists.txt', 'include/*', 'src/*', 'test/*', 'cmake/*'

    # Generate the logic between shared and fPic
    implements = ['auto_shared_fpic']

    options = {
        'cuda'          : [True, False], # Build the emu cuda extension
        'python'        : [True, False], # Build the emu python tests, change nothing regarding the emu python extension
        'shared'        : [True, False],
        'fPIC'          : [True, False],
    }

    default_options = {
        'cuda'       : False,
        'python'     : False,
        'shared'     : False,
        'fPIC'       : True,
    }

    def requirements(self):
        data = self.conan_data['requirements'][self.version]

        self.requires(data['fmt'], transitive_headers=True, transitive_libs=True)
        self.requires(data['boost'], transitive_headers=True, transitive_libs=True)
        self.requires(data['ms-gsl'], transitive_headers=True)
        self.requires(data['mdspan'], transitive_headers=True)
        self.requires(data['half'], transitive_headers=True)
        self.requires(data['tl-expected'], transitive_headers=True)
        self.requires(data['tl-optional'], transitive_headers=True)
        self.requires(data['dlpack'], transitive_headers=True)

        if self.options.cuda:
            self.requires(data['cccl'], transitive_headers=True)

        if self.options.python:
            # Only required for the tests
            self.test_requires(data['pybind11'])

        self.tool_requires(data['cmake'])
        self.test_requires(data['gtest'])

    # Cannot be optional (link to the use of cuda or not).
    python_requires = 'conan_cuda/[>=1 <2]'

    def layout(self):
        cmake_layout(self)
        self.cpp.source.components['core'].includedirs = ['include/core']
        self.cpp.build.components['core'].libdirs = self.cpp.build.libdirs

        self.cpp.source.components['python'].includedirs = ['include/python']

        if self.options.cuda:
            cuda_prop = self.python_requires['conan_cuda'].module.properties()

            self.cpp.source.components['cuda'].includedirs = ['include/cuda', cuda_prop.include]
            self.cpp.build.components['cuda'].libdirs = [*self.cpp.build.libdirs, cuda_prop.library]
            self.cpp.build.components['cuda'].system_libs = ['cuda', 'cudart', 'cublas']

    def source(self):
        get(self, **self.conan_data['sources'][self.version], strip_root=True)

    generators = 'CMakeDeps'

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables['emu_build_cuda'] = self.options.cuda
        tc.cache_variables['emu_build_python_test'] = self.options.python
        tc.cache_variables['emu_boost_namespace'] = self.dependencies['boost'].options.namespace

        tc.generate()
        VirtualBuildEnv(self).generate()

    def build(self):
        cmake = CMake(self)

        cmake.configure()
        cmake.build()

        cmake.test()

    def package(self):
        copy(self, 'LICENSE', self.source_folder, os.path.join(self.package_folder, 'licenses'))

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        lib_location = 'lib' if self.settings.build_type == 'Release' else 'lib/debug'

        self.cpp_info.components['core'].libs = ['emucore']
        self.cpp_info.components['core'].libdirs = [lib_location]
        self.cpp_info.components['core'].requires = [
            'fmt::fmt',
            'ms-gsl::_ms-gsl',
            'mdspan::mdspan',
            'half::half',
            'tl-expected::tl-expected',
            'tl-optional::tl-optional',
            'dlpack::dlpack',
            'boost::boost',
        ]

        self.cpp_info.components['core'].defines = ['EMU_BOOST_NAMESPACE={}'.format(self.dependencies['boost'].options.namespace)]

        self.cpp_info.components['python'].bindirs = []
        self.cpp_info.components['python'].libdirs = []
        self.cpp_info.components['python'].requires = ['core']

        if self.options.cuda:
            self.cpp_info.components['cuda'].libs = ['emucuda']
            self.cpp_info.components['cuda'].libdirs = [lib_location]
            self.cpp_info.components['cuda'].requires = [
                'core',
                'cccl::cccl',
            ]
            #TODO: check if FMT_USE_CONSTEXPR is still needed to use {fmt} in .cu files
            self.cpp_info.components['cuda'].defines = ['EMU_CUDA', 'FMT_USE_CONSTEXPR=1']

            if not self.options.shared:
                # linker by default will not keep emu_cuda_device_pointer because it is not used explicitly.
                self.cpp_info.components['cuda'].exelinkflags = ['-Wl,-u,emu_cuda_device_pointer']
