from conan import ConanFile

from conan.tools.gnu import Autotools
from conan.tools.files import get

class Log4cppConan(ConanFile):
    name = 'log4cpp'
    license = 'GNU Lesser General Public'
    author = 'Bastiaan Bakker'
    url = 'http://log4cpp.sourceforge.net'
    description = 'Log4cpp is library of C++ classes for flexible logging'
    topics = 'log'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
    }

    def source(self):
        get(self, **self.conan_data['sources'][self.version], strip_root=True, filename='log4cpp.tar.gz')

    generators = 'AutotoolsDeps', 'AutotoolsToolchain'

    def build(self):
        autotools = Autotools(self)
        autotools.configure(build_script_folder='log4cpp', args=['--enable-doxygen=no'])
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ['log4cpp']
