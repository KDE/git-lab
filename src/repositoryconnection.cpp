#include "repositoryconnection.h"
#include <iostream>

#include "utils.h"

using namespace pybind11::literals;

RepositoryConnection::RepositoryConnection()
    : m_config(py::module::import("lab.config").attr("Config")())
    , m_local_repo(Utils::get_cwd_repo())
{
    auto utilsModule = py::module::import("lab.utils");
    auto utils = utilsModule.attr("Utils");

    py::object origin;
    try {
        origin = m_local_repo.attr("remote")("name"_a="origin");
    }  catch (const py::error_already_set &valueError) {
        Utils::log(LogType::Error, "No origin remote exists");
        std::exit(1);
    }

    std::string repository = (*origin.attr("urls").begin()).cast<std::string>();
    std::string gitlab_url = Utils::gitlab_instance_url(repository);

    std::string gitlab_hostname;
    auto urlparse = py::module::import("urllib.parse").attr("urlparse");
    if (const auto parseResult = urlparse(gitlab_url); !parseResult.is_none()) {
        gitlab_hostname = parseResult.attr("hostname").cast<std::string>();
    } else {
        Utils::log(LogType::Error, "Failed to detect GitLab hostname");
        std::exit(1);
    }

    auto optional_token = py_cast_optional<std::string>(m_config.attr("token")(gitlab_hostname));
    if (!optional_token) {
        Utils::log(LogType::Error, "No authentication token found. ");
        std::cout << "Please create a token with the api and write_repository scopes on " + gitlab_url + "/profile/personal_access_tokens.";
        std::cout << R"(Afterwards use "git lab login --host )" << gitlab_hostname << R"( --token t0k3n")";

        std::exit(1);
    }

    login(gitlab_url, *optional_token);
    if (m_connection.is_none()) {
        Utils::log(LogType::Error, "Failed to connect to GitLab");
        std::exit(1);
    }

    m_remote_project = m_connection.attr("projects").attr("get")(Utils::str_id_for_url(Utils::normalize_url(repository)));
}

void RepositoryConnection::login(const std::string &instance_url, const std::string &token)
{
    try {
        m_connection = py::module::import("gitlab").attr("Gitlab")(instance_url, "private_token"_a=token);
        m_connection.attr("auth")();
    }  catch (const py::error_already_set &error) {
        Utils::log(LogType::Error, "Could not log into GitLab: " + instance_url);
        std::exit(1);
    }
}
