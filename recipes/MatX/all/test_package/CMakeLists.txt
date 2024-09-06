cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CUDA)

find_package(pybind11)
find_package(matx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cu)
target_link_libraries(${PROJECT_NAME} PRIVATE matx::matx)
target_compile_features(${PROJECT_NAME} PRIVATE cuda_std_17)
set_property(TARGET ${PROJECT_NAME} PROPERTY CUDA_ARCHITECTURES 70)
