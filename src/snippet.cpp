#include "snippet.h"

#include <map>
#include <iostream>
#include <fstream>

#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include "utils.h"

Snippet::Snippet() : RepositoryConnection()
{
}

void Snippet::run(const std::optional<std::string> &filename, const std::optional<std::string> &title)
{
    Snippet snippet;

    std::string content;
    if (filename) {
        auto file = std::ifstream(*filename);
        if (!file.is_open()) {
            Utils::log(LogType::Error, "Failed to open file" + *filename);
            std::exit(1);
        }
        for (std::string line; std::getline(file, line); ) {
            content += line;
        }
    } else {
        std::cin >> content;
    }

    snippet.paste(filename.value_or("stdin"), content, title.value_or("Empty title"));
}

void Snippet::paste(const std::string &file_name, const std::string &content, const std::string &title)
{
    std::map<std::string, std::string> options {
        {"title", title},
        {"file_name", file_name},
        {"content", content},
        {"visibility", "public"}
    };

    auto snippet = m_connection.attr("snippets").attr("create")(options);

    Utils::log(LogType::Info, "Created snippet at " + snippet.attr("web_url").cast<std::string>());
    std::cout << "You can access it raw at " << snippet.attr("raw_url").cast<std::string>();
}
