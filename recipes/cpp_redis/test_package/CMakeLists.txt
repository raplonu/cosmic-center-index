cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX CUDA)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(CUDAToolkit)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE ${CONAN_LIBS})

if(CUDAToolkit_FOUND)
    target_link_libraries(example PRIVATE CUDA::cudart)
endif()

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
