#include "utils.h"

#include <iostream>
#include <filesystem>

#include <unistd.h>
#include <sys/wait.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <spawn.h>

#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

Utils::Utils()
{

}

void Utils::log(LogType type, const std::string &message)
{
    std::string prefix = TextFormatting::bold;

    switch (type) {
    case LogType::Info:
        prefix += "Info";
        break;
    case LogType::Warning:
        prefix += TextFormatting::yellow + "Warning" + TextFormatting::end;
        break;
    case LogType::Error:
        prefix += TextFormatting::red + "Error" + TextFormatting::end;
        break;
    }

    prefix += TextFormatting::end;

    if (prefix.size() > 0) {
        prefix += ": ";
    }

    std::cout << prefix << message << std::endl;
}

std::string Utils::normalize_url(const std::string &url)
{
    auto parse_result = py::module::import("urllib.parse").attr("urlparse")(url);

    // url is already fine
    if (!parse_result.attr("scheme").cast<std::string>().empty())
        return url;

    if (url.find("@") != 0 && url.find(":") != 0) {
        return "ssh://" + string_replace(url, ":", "/");
    }

    Utils::log(LogType::Error, "Invalid url " + url);
    std::exit(0);
}

std::string Utils::ssh_url_from_http(const std::string &url)
{
    return string_replace(string_replace(url, "https://", "ssh://git@"), "http://", "ssh://git@");
}

std::string Utils::str_id_for_url(const std::string &url)
{
    std::string normalized_url = normalize_url(url);

    py::object parse_result = py::module::import("urllib.parse").attr("urlparse")(string_replace(normalized_url, ".git", ""));

    const std::string path = parse_result.attr("path").cast<std::string>();
    std::string repository_path(path.begin() + 1, path.end());
    return py::module::import("urllib.parse").attr("quote_plus")(repository_path).cast<std::string>();
}

std::string Utils::gitlab_instance_url(const std::string &repository_url)
{
    py::object repository_url_parse = py::module::import("urllib.parse").attr("urlparse")(repository_url);

    const auto scheme = py_cast_optional<std::string>(repository_url_parse.attr("scheme"));
    const auto hostname = py_cast_optional<std::string>(repository_url_parse.attr("hostname"));
    const auto path = py_cast_optional<std::string>(repository_url_parse.attr("path"));

    // Valid url
    if (scheme && path) {
        // If the repository is using some kind of http, can know whether to use http or https
        if ((*scheme).find("http") != std::string::npos) {
            if (!(*hostname).empty()) {
                return (*scheme) + "://" + *hostname;
            }
        }

        // else assume https
        // redirects don't work according to
        // https://python-gitlab.readthedocs.io/en/stable/api-usage.html.
        if (hostname) {
            return "https://" + *hostname;
        }
    }

    // non valid url (probably scp syntax)
    if (repository_url.find("@") != std::string::npos && repository_url.find(":") != std::string::npos) {
        // create url in form of ssh://git@github.com/KDE/kaidan
        py::object ssh_repository_parse = py::module::import("urllib.parse").attr("urlparse")("ssh://" + string_replace(repository_url, ":", "/"));

        if (!ssh_repository_parse.attr("hostname").cast<std::string>().empty()) {
            return "https://" + ssh_repository_parse.attr("hostname").cast<std::string>();
        }
    }

    // If everything failed, exit
    Utils::log(LogType::Error, "Failed to detect GitLab instance url");
    std::exit(1);
}

void Utils::xdg_open(const std::string &path)
{
    run_process({"xdg-open", path});
}

bool Utils::ask_bool(const std::string &question)
{
    std::cout << question + " [y/n] ";

    std::string answer;
    std::getline(std::cin, answer);

    return answer == "y";
}

std::optional<std::string> Utils::find_dotgit(const std::filesystem::path &search_path)
{
    // Check if search path has a directory called .git
    const auto it = std::filesystem::directory_iterator(search_path);
    bool found = std::any_of(std::filesystem::begin(it), std::filesystem::end(it), [](const std::filesystem::directory_entry &entry) {
        return entry.path().filename() == ".git";
    });

    if (found) {
        return search_path;
    }

    // Search the parent directory
    const auto parent_dir = search_path.parent_path();

    // Stop if no parent directory exists
    if (parent_dir == search_path) {
        return std::nullopt;
    }

    return find_dotgit(parent_dir);
}

pybind11::object Utils::get_cwd_repo()
{
    const auto path = Utils::find_dotgit(std::filesystem::current_path());
    if (path) {
        try {
            return py::module::import("git").attr("Repo")(*path);
        } catch (const py::error_already_set &error) {
            // Move on to error reporting
        }
    }

    Utils::log(LogType::Error, "Current directory is not a git repository");
    std::exit(1);
}

std::vector<std::string> Utils::editor()
{
    auto repo = Utils::get_cwd_repo();
    auto config = repo.attr("config_reader")();

    std::string editor = config.attr("get_value")("core", "editor", "").cast<std::string>();
    if (editor.empty()) {
        if (const auto enveditor = get_environment_variable("EDITOR")) {
            editor = *enveditor;
        } else if (const auto enveditor = get_environment_variable("VISUAL")) {
            editor = *enveditor;
        } else if (bool exists = run_process({"which", "editor"}); exists) {
            editor = "editor";
        } else {
            editor = "vi";
        }
    }

    const auto split_string = py::module::import("shlex").attr("split")(editor).cast<py::list>();
    std::vector<std::string> command;

    std::transform(split_string.begin(), split_string.end(), std::back_inserter(command), [](const py::handle &item) {
        return item.cast<std::string>();
    });

    return command;
}

std::string Utils::string_replace(std::string string, const std::string &from, const std::string &to) {
    size_t start_pos = string.find(from);
    // Not found
    if(start_pos == std::string::npos)
        return string;

    string.replace(start_pos, from.length(), to);
    return string;
}

int run_process(const std::vector<std::string> &command) {
    // TODO proper implementation
    return py::module::import("subprocess").attr("call")(command).cast<int>();
}

std::optional<std::string> get_environment_variable(const std::string &variable)
{
    const auto value = std::getenv(variable.c_str());
    if (value == nullptr) {
        return std::nullopt;
    }

    return std::string(value);
}
