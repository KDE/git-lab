add_executable(git-lab main.cpp)

target_link_libraries(git-lab Qt5::Core pybind11::embed)
