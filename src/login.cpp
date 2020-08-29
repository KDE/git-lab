#include "login.h"

#include <pybind11/embed.h>

namespace py = pybind11;

void Login::run(const std::string &host, const std::string &token, const std::string &command)
{
    auto config = py::module::import("lab.config").attr("Config")();

    if (!command.empty()) {
        config.attr("set_auth_command")(host, command);
    } else {
        config.attr("set_token")(host, token);
    }

    config.attr("save")();
}
