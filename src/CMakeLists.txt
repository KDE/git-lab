add_executable(git-lab
    main.cpp
    fork.cpp
    workflow.cpp
    login.cpp
    feature.cpp
    repositoryconnection.cpp
    snippet.cpp
    utils.cpp)

target_link_libraries(git-lab pybind11::embed)

install(TARGETS git-lab DESTINATION bin)
