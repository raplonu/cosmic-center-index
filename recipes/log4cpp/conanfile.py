from conans import ConanFile, AutoToolsBuildEnvironment, tools
from packaging import version

class Log4cppConan(ConanFile):
    name = 'log4cpp'
    pversion = version.parse('1.1.3')
    version = pversion.public
    license = 'GNU Lesser General Public'
    author = 'Bastiaan Bakker'
    url = 'http://log4cpp.sourceforge.net'
    description = 'Log4cpp is library of C++ classes for flexible logging'
    topics = 'log'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = {'shared': False}
    generators = 'cmake'

    def source(self):
        full_v = self.pversion.public; pre_v =  '.'.join(map(str, self.pversion.release[0:2]))
        tools.get(f'https://sourceforge.net/projects/log4cpp/files/log4cpp-{pre_v}.x%20%28new%29/log4cpp-{pre_v}/log4cpp-{full_v}.tar.gz/download',
                md5='b9e2cee932da987212f2c74b767b4d8b', filename="log4cpp.tar.gz")

    def _configure(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir='log4cpp')
        return autotools

    def build(self):
        autotools = self._configure()
        autotools.make()

    def package(self):
        autotools = self._configure()
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ['log4cpp']

