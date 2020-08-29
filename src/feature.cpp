#include "feature.h"

#include <iostream>

#include "utils.h"

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
    , m_repo(Utils::get_cwd_repo())
    , m_git(m_repo.attr("git"))
{
}

void Feature::checkout(const std::string &start, const std::string &name) const
{
    try {
        if (m_repo.attr("refs").contains(name)) {
            m_git.attr("checkout")(name);

            Utils::log(LogType::Info, "Switched to branch '" + name + "'");
        } else {
            m_git.attr("checkout")(start, "b"_a=name);
            Utils::log(LogType::Info, "Switched to a new branch '" + name + "'");
        }
    }  catch (const py::error_already_set &git_error) {
        Utils::log(LogType::Error, git_error.value().attr("stderr").attr("strip")().cast<std::string>());
    }
}

void Feature::list() const
{
    std::cout << m_git.attr("branch")().cast<std::string>();
}
