#pragma once

#include <string>

class Login
{
public:
    Login() = default;
    static void run(const std::string &host, const std::string &token, const std::string &command);
};
