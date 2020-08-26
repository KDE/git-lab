add_executable(git-lab main.cpp)

target_link_libraries(git-lab pybind11::embed)

install(TARGETS git-lab DESTINATION bin)
