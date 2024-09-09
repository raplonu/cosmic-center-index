from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.files import get
from copy import deepcopy
from conan.tools.files import export_conandata_patches, apply_conandata_patches

class CppredisConan(ConanFile):
    name = 'cpp_redis'
    license = 'The MIT License (MIT)'
    url = 'https://github.com/offscale/conan-cpp_redis'
    description = 'Conan recipe for Cpp_Redis'
    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {
        'shared': [True, False],
        'fPIC': [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        # Just in case, do not modify the original conan_data.
        redis = deepcopy(self.conan_data["sources"][self.version])
        tacopie = redis.pop('tacopie')

        get(self, **redis, strip_root=True)
        get(self, **tacopie, strip_root=True, destination='tacopie')


    # def source(self):
        # git = tools.Git(folder='cpp_redis')
        # url = 'https://github.com/cpp-redis/cpp_redis.git'
        # git.clone(url, f'{self.version}-beta.1', shallow=True)
        # self.run('cd cpp_redis && git submodule update --init --recursive')

    generators = 'CMakeToolchain'

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)

        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        # Install headers and cmake files.
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['cpp_redis','tacopie']
