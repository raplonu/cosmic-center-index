from conan import ConanFile
from conan.tools.cmake import CMakeToolchain

try:
    from cuda_arch import compute_capabilities
except :
    print('Error importing cuda_arch: cannot load cuda library.')

from cuda_toolkit_properties import properties, append_cuda

class Pkg(ConanFile):
    name = 'conan_cuda'
    version = '1.0.0'
    package_type = 'python-require'
    exports = 'cuda_arch.py', 'cuda_toolkit_properties.py'
