#pragma once

#include <string>

#include <pybind11/embed.h>

namespace py = pybind11;


class Feature
{
public:
    static void run(const std::string &start, const std::string &name);

    Feature();
    void checkout(const std::string &start, const std::string &name) const;
    void list() const;

private:
    py::object m_utils;
    py::object m_repo;
    py::object m_git;
};
