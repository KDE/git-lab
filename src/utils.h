#pragma once

#include <string>
#include <filesystem>

#include <pybind11/pytypes.h>

namespace py = pybind11;

namespace TextFormatting {
    static std::string purple = "\033[0;95m";
    static std::string cyan = "\033[0;36m";
    static std::string darkcyan = "\033[0;96m";
    static std::string blue = "\033[0;34m";
    static std::string green = "\033[0;32m";
    static std::string yellow = "\033[0;33m";
    static std::string red = "\033[0;31m";
    static std::string lightred = "\033[1;31m";
    static std::string bold = "\033[1m";
    static std::string underline = "\033[4m";
    static std::string end = "\033[0m";
}

template<class T>
std::optional<T> py_cast_optional(const pybind11::object &&source) {
    if (source.is_none()) {
        return std::nullopt;
    }

    return source.cast<T>();
}

int run_process(const std::vector<std::string> &command);
std::optional<std::string> get_environment_variable(const std::string &variable);

enum LogType {
    Info,
    Warning,
    Error
};

class Utils
{
public:

    Utils();

    static void log(LogType type, const std::string &message);
    static std::string normalize_url(const std::string &url);
    static std::string ssh_url_from_http(const std::string &url);
    static std::string str_id_for_url(const std::string &url);
    static std::string gitlab_instance_url(const std::string &repository_url);
    static void xdg_open(const std::string &path);
    static bool ask_bool(const std::string &question);
    static std::optional<std::string> find_dotgit(const std::filesystem::path &root_path);
    static py::object get_cwd_repo();
    static std::vector<std::string> editor();

private:
    static std::string string_replace(std::string string, const std::string &from, const std::string &to);
};
