#pragma once

#include <pybind11/embed.h>

namespace  py = pybind11;

class RepositoryConnection
{
public:
    RepositoryConnection();

private:
    void login(const std::string &instance_url, const std::string &token);

    py::object m_config; /* Config */

protected:
    py::object m_connection; /* Gitlab */
    py::object m_local_repo; /* Repo */
    py::object m_remote_project; /* Project */

};
