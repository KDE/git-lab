cmake_minimum_required(VERSION 3.16)

project(git-lab)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 REQUIRED)

add_subdirectory(src)
