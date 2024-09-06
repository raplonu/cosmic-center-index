import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class Log4CppTest(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)


    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_package"), env="conanrun")


    # def build(self):
    #     cmake = CMake(self)
    #     # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
    #     # in "test_package"
    #     cmake.configure()
    #     cmake.build()

    # def imports(self):
    #     self.copy("*.dll", dst="bin", src="bin")
    #     self.copy("*.dylib*", dst="bin", src="lib")
    #     self.copy('*.so*', dst='bin', src='lib')

    # def test(self):
    #     if not tools.cross_building(self.settings):
    #         os.chdir("bin")
    #         self.run(".%sexample" % os.sep)
