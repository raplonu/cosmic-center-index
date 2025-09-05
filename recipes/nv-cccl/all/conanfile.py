import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class NvCCCL(ConanFile):
    name = "nv-cccl"
    description = "CUDA Core Compute Libraries"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIA/cccl"
    topics = ("cpp", "hpc", "gpu", "modern-cpp", "parallel-computing", "cuda", "nvidia", "gpu-acceleration", "cuda-kernels", "gpu-computing", "parallel-algorithm", "parallel-programming", "nvidia-gpu", "gpu-programming", "cuda-library", "cpp-programming", "cuda-programming", "accelerated-computing", "cuda-cpp")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    # TODO: add header_only=False option

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "7",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.15 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # Install via CMake to ensure headers are configured correctly
        tc = CMakeToolchain(self)

        tc.cache_variables["CCCL_ENABLE_C"] = False
        tc.cache_variables["CCCL_ENABLE_CUB"] = False
        tc.cache_variables["CCCL_ENABLE_CUDAX"] = False
        tc.cache_variables["CCCL_ENABLE_LIBCUDACXX"] = False
        tc.cache_variables["CCCL_ENABLE_THRUST"] = False
        tc.cache_variables["CCCL_ENABLE_UNSTABLE"] = True

        tc.cache_variables["CCCL_ENABLE_EXAMPLES"] = False
        tc.cache_variables["CCCL_ENABLE_TESTING"] = False

        tc.cache_variables["CUB_ENABLE_INSTALL_RULES"] = True
        tc.cache_variables["Thrust_ENABLE_INSTALL_RULES"] = True
        tc.cache_variables["libcudacxx_ENABLE_INSTALL_RULES"] = True
        tc.cache_variables["cudax_ENABLE_INSTALL_RULES"] = False

        tc.generate()
        VirtualBuildEnv(self).generate()

    # def _patch_sources(self):
    #     # Don't look for CUDA, we're only installing the headers
    #     replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "include(${CMAKE_CURRENT_SOURCE_DIR}/CUDA.cmake)",
    #                                                                              """
    #                                                                              if(NOT CUTLASS_ENABLE_HEADERS_ONLY)
    #                                                                              include(${CMAKE_CURRENT_SOURCE_DIR}/CUDA.cmake)
    #                                                                              endif()""")

    def build(self):
        # self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cccl")
        # Removes the -xxx suffix from the version (e.g. 3.2.0-dev -> 3.2.0)
        mmp_version = self.version.split('-')[0]
        self.cpp_info.set_property("system_package_version", mmp_version)
        # self.cpp_info.set_property("cmake_target_name", "CCCL::CCCL")
        # self.cpp_info.set_property("cmake_module_file_name", "CCCL")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        cmake_base_path = os.path.join("lib", "cmake", "cccl")
        self.cpp_info.builddirs = [cmake_base_path]

        cmake_file = os.path.join(cmake_base_path, "cccl-config.cmake")
        self.cpp_info.set_property("cmake_build_modules", [cmake_file])
