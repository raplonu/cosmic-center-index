# cmake-conan

CMake dependency provider for the Conan C and C++ package manager based on the [Conan CMake](https://github.com/conan-io/cmake-conan) package.

## Usage

Copy the `cmake/` directory to your project next to your `CMakeLists.txt` file.

```bash
cd [your-project]
mkdir build
cmake -B build -S . -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=../cmake/conan_provider.cmake -DCMAKE_BUILD_TYPE=Release
```

## Notes

The original `conan_provider.cmake` was found to be hard to be used in the scope a python package with a C/C++ extension. This version modify the build folder hierarchy to be more compatible with the `scikit-build-core` build system.

If you want to use the original `conan_provider.cmake` you can find it [here](https://raw.githubusercontent.com/conan-io/cmake-conan/refs/heads/develop2/conan_provider.cmake).

If you want to apply the changes to the original `conan_provider.cmake` you can find the patch file: `conan_provider.patch` using:

```bash
patch conan_provider.cmake < conan_provider.patch
```
