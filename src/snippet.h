#pragma once

#include <optional>
#include <string>

#include "repositoryconnection.h"

class Snippet : RepositoryConnection
{
public:
    Snippet();

    static void run(const std::optional<std::string> &filename, const std::optional<std::string> &title);

    void paste(const std::string &file_name, const std::string &content, const std::string &title);
};
