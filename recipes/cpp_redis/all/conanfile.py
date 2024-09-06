from conans import ConanFile, CMake, tools


class CppredisConan(ConanFile):
    name = 'cpp_redis'
    version = '4.4.0'
    license = 'The MIT License (MIT)'
    url = 'https://github.com/offscale/conan-cpp_redis'
    description = 'Conan recipe for Cpp_Redis'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = 'shared=False'
    generators = 'cmake'

    exports = '0001-conan-patch.patch'

    def source(self):
        git = tools.Git(folder='cpp_redis')
        url = 'https://github.com/cpp-redis/cpp_redis.git'
        git.clone(url, f'{self.version}-beta.1', shallow=True)
        self.run('cd cpp_redis && git submodule update --init --recursive')
        tools.patch(base_path='cpp_redis', patch_file='0001-conan-patch.patch')

    def _configure(self):
        cmake = CMake(self)
        cmake.configure(source_folder='cpp_redis')

        return cmake

    def build(self):
        self._configure().build()

    def package(self):
        self._configure().install()

    def package_info(self):
        self.cpp_info.libs = ['cpp_redis','tacopie']
