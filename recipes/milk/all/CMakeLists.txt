cmake_minimum_required(VERSION 3.15)

project(milk LANGUAGES C)

# For simplicity, libraries are created in the root build directory
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
# When having multiple shared libraries, this ensures that they are all linked to each other.
set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")

add_subdirectory(milk)