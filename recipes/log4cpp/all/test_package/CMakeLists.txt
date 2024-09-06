cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

find_package(log4cpp REQUIRED CONFIG)

add_executable(test_package example.cpp)
target_link_libraries(test_package log4cpp::log4cpp)
