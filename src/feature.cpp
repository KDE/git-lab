#include "feature.h"

#include <iostream>

using namespace pybind11::literals;

void Feature::run(const std::string &start, const std::string &name)
{
    Feature feature;
    if (!name.empty()) {
        feature.checkout(start, name);
    } else {
        feature.list();
    }
}

Feature::Feature()
    : m_utils(py::module::import("lab.utils").attr("Utils"))
    , m_repo(m_utils.attr("get_cwd_repo")())
    , m_git(m_repo.attr("git"))
{
}

void Feature::checkout(const std::string &start, const std::string &name) const
{
    auto logType = py::module::import("lab.utils").attr("LogType");

    try {
        if (m_repo.attr("refs").contains(name)) {
            m_git.attr("checkout")(name);

            m_utils.attr("log")(logType.attr("Info"), "Switched to branch '" + name + "'");
        } else {
            m_git.attr("checkout")(start, "b"_a=name);
            m_utils.attr("log")(logType.attr("Info"), "Switched to a new branch '" + name + "'");
        }
    }  catch (const py::error_already_set &git_error) {
        m_utils.attr("log")(logType.attr("Error"), git_error.value().attr("stderr").attr("strip")());
    }
}

void Feature::list() const
{
    std::cout << m_git.attr("branch")().cast<std::string>();
}
