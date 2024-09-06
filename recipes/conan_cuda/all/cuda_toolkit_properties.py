import tempfile
from subprocess import Popen, PIPE
import shutil

class CudaLibrary:
    def __init__(self, include, library, target, version, major, minor, patch) -> None:
        self.include = include
        self.library = library
        self.target = target
        self.version = version
        self.major = major
        self.minor = minor
        self.patch = patch

__file_content = '''
cmake_minimum_required(VERSION 3.17)
project(cuda)
find_package(CUDAToolkit)
message(STATUS "@CAPTURE include = ${CUDAToolkit_INCLUDE_DIRS}")
message(STATUS "@CAPTURE library = ${CUDAToolkit_LIBRARY_DIR}")
message(STATUS "@CAPTURE target = ${CUDAToolkit_TARGET_DIR}")
message(STATUS "@CAPTURE version = ${CUDAToolkit_VERSION}")
message(STATUS "@CAPTURE major = ${CUDAToolkit_VERSION_MAJOR}")
message(STATUS "@CAPTURE minor = ${CUDAToolkit_VERSION_MINOR}")
message(STATUS "@CAPTURE patch = ${CUDAToolkit_VERSION_PATCH}")
'''

def properties() -> CudaLibrary:

    # Get random tmp directory for cmake to put its garbage.
    dirpath = tempfile.mkdtemp()

    file = open(f'{dirpath}/CMakeLists.txt', 'w+')

    file.write(__file_content)
    file.close()

    # Capture both stdout & stderr to prevent trashing terminal.
    process = Popen(f'cmake {file.name} -B {dirpath}'.split(), stdout=PIPE, stderr=PIPE)

    ouput, err = process.communicate()
    exit_code = process.wait()

    result = CudaLibrary('', '', '', '', '', '', '')

    if exit_code != 0:
        print(f'Error cmake returned {exit_code} with messages {err}')
    else:
        # split lines
        entries = ouput.split(b'\n')

        # Convert lines to string
        entries = map(bytes.decode, entries)

        def capture(s:str) -> bool:
            return s.startswith('-- @CAPTURE')

        # Only takes entries that start with '@CAPTURE'
        entries = list(filter(capture, entries))

        def remove_capture(s:str) -> str:
            return s.removeprefix('-- @CAPTURE')

        # Removes prefix.
        entries = list(map(remove_capture, entries))

        # Separate key and value based on '=' sign. Removes unwanted whitespace.
        key_value = map(lambda s: tuple(map(str.strip, s.split('='))), entries)

        result = CudaLibrary(**dict(key_value))

    shutil.rmtree(dirpath, ignore_errors=True)

    return result

def append_cuda(cpp_info, cuda_libs = ['cuda', 'cudart']):
    cuda_prop = properties()

    cpp_info.includedirs.append(cuda_prop.include)
    cpp_info.libdirs.append(cuda_prop.library)
    cpp_info.system_libs += cuda_libs

    return cpp_info
