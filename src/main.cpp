#include "CLI11.hpp"
#include <pybind11/embed.h>
#include <pybind11/pytypes.h>

namespace py = pybind11;

int main(int argc, char* argv[]) {
    CLI::App parser("The arc of GitLab.");

    auto *mr_parser = parser.add_subcommand("mr", "Create a new merge request for the current branch");
    auto *checkout_parser = parser.add_subcommand("checkout", "check out a remote merge request");
    auto *mrs_parser = parser.add_subcommand("mrs", "List open merge requests");
    auto *feature_parser = parser.add_subcommand("feature", "Create branches and list branches");
    auto *login_parser = parser.add_subcommand("login", "Save a token for a GitLab instance");
    auto *search_parser = parser.add_subcommand("search", "Search for a repository");
    parser.add_subcommand("fork", "Create a fork of the project");
    auto *issues_parser = parser.add_subcommand("issues", "Gitlab issues");
    auto *snippet_parser = parser.add_subcommand("snippet", "Create a snippet from stdin or file");
    auto *workflow_parser = parser.add_subcommand("workflow", "Set the workflow to use for a project");

    std::string target_branch = "master";
    mr_parser->add_option("--target-branch", target_branch, "Use different target branch than master");

    int number;
    checkout_parser->add_option("number", number, "Merge request number to checkout")->required();

    bool mrs_for_project = false;
    bool mrs_opened = false;
    bool mrs_merged = false;
    bool mrs_closed = false;
    bool mrs_show_url = false;
    mrs_parser->add_flag("--project", mrs_for_project, "Show merge requests of the current project, not of the user");
    auto *mrs_opened_option = mrs_parser->add_flag("--opened", mrs_opened, "Show opened merge requests");
    auto *mrs_merged_option = mrs_parser->add_flag("--merged", mrs_merged, "Show merged merge requests")->excludes(mrs_opened_option);
    mrs_parser->add_flag("--closed", mrs_closed, "Show closed merge requests")->excludes(mrs_merged_option)->excludes(mrs_opened_option);
    mrs_parser->add_flag("--url", mrs_show_url, "Show web url of merge requests (default false)");

    std::string branch_start = "HEAD";
    std::string branch_name;
    feature_parser->add_option("name", branch_name, "name for the new branch");
    feature_parser->add_option("start", branch_start, "starting point for the new branch");

    std::string host;
    std::string token;
    std::string command;
    login_parser->add_option("--host", host, "GitLab host (e.g invent.kde.org)")->required();
    auto token_option = login_parser->add_option("--token", token, "GitLab api private token");
    login_parser->add_option("--command", command, "Command to run when a token is needed")->excludes(token_option);

    std::string search_query;
    search_parser->add_option("search_query", search_query, "Search query");

    int issue_id = -1;
    bool issues_opened = false;
    bool issues_closed = false;
    bool issues_assigned = false;
    bool issues_project = false;
    bool issues_web = false;
    issues_parser->add_option("issue_id", issue_id, "issue id");
    auto *opened_option = issues_parser->add_flag("--opened", issues_opened, "Show opened issues");
    issues_parser->add_flag("--closed", issues_closed, "Show closed issues")->excludes(opened_option);
    issues_parser->add_flag("--assigned", issues_assigned, "Show only issues assigned to me");
    issues_parser->add_flag("--project", issues_project, "Show all project issues and not only the one you authored");
    issues_parser->add_flag("--web", issues_web, "open on web browser");

    std::string snippet_title;
    std::string snippet_filename;
    snippet_parser->add_option("--title", snippet_title, "Add a custom title");
    snippet_parser->add_option("filename", snippet_filename, "File name to upload");

    bool workflow_fork = false;
    bool workflow_workbranch = false;
    workflow_parser->add_flag("--fork", workflow_fork, "Set the fork workflow (branch in a fork of the upstream repository)");
    workflow_parser->add_flag("--workbranch", workflow_workbranch, "Set the work branch workflow (branch in the upstream repository)");

    CLI11_PARSE(parser, argc, argv);

    py::scoped_interpreter guard {}; // start the interpreter and keep it alive

    // Run subcommand
//    try {
    if (parser.got_subcommand(mr_parser)) {
        py::module mergerequestcreator = py::module::import("lab.mergerequestcreator");
        mergerequestcreator.attr("run")(target_branch);
    } else if (parser.got_subcommand(checkout_parser)) {
        py::module checkout = py::module::import("lab.mergerequestcheckout");
        checkout.attr("run")(number);
    } else if (parser.got_subcommand(mrs_parser)) {
        py::module mrs = py::module::import("lab.mergerequestlist");
        if (mrs_opened) {
            mrs_closed = false;
            mrs_merged = false;
        } else if (mrs_closed) {
            mrs_opened = false;
            mrs_merged = false;
        } else if (mrs_merged) {
            mrs_opened = false;
            mrs_closed = false;
        } else {
            mrs_opened = true;
            mrs_merged = true;
            mrs_closed = true;
        }

        mrs.attr("run")(mrs_for_project, mrs_merged, mrs_opened, mrs_closed, mrs_show_url);
    } else if (parser.got_subcommand(feature_parser)) {
        py::module feature = py::module::import("lab.feature");
        feature.attr("run")(branch_start, branch_name);
    } else if (parser.got_subcommand(login_parser)) {
        py::module login = py::module::import("lab.login");
        login.attr("run")(host, token, command);
    } else if (parser.got_subcommand(search_parser)) {
        py::module search = py::module::import("lab.search");
        search.attr("run")(search_query);
    } else if (parser.got_subcommand(issues_parser)) {
        // If one of the options is set, disable the others
        if (issues_opened) {
            issues_closed = false;
        } else if (issues_closed) {
            issues_opened = false;
        } else {
            issues_closed = true;
            issues_opened = true;
        }

        py::module issues = py::module::import("lab.issues");
        issues.attr("run")(issue_id, issues_opened, issues_closed, issues_assigned, issues_project, issues_web);
    } else if (parser.got_subcommand(snippet_parser)) {
        py::module snippet = py::module::import("lab.snippet");
        snippet.attr("run")(snippet_filename, snippet_filename);
    } else if (parser.got_subcommand(workflow_parser)) {
        py::module workflow = py::module::import("lab.workflow");
        workflow.attr("run")(workflow_fork, workflow_workbranch);
    } else {
        std::cout << parser.help();
        return 1;
    }

    /*} catch (const py::error_already_set &error) {
        auto gitCommandError = py::module::import("git.exc").attr("GitCommandError");

        auto utils = py::module::import("lab.utils");
        auto log = utils.attr("Utils").attr("log");
        auto logTypeError = utils.attr("LogType").attr("Error");
        if (error.matches(gitCommandError)) {
            log(logTypeError, error.what());

            return 0;
        } else if (false)(error.matches(systemExit) || error.matches(keyboardInterrupt)) {
            std::cout << "Intentional exit";
            std::flush(std::cout);
            return 0;
        } else {
            log(logTypeError, "git-lab crashed. This should not happen.");
            const auto traceback = py::module::import("traceback");
            std::cout <<
                "Please help us to fix it by opening an issue on\n"
                "https://invent.kde.org/sdk/git-lab/-/issues.\n"
                "Make sure to include the information below:\n"
                "\n```\n"
                << traceback.attr("format_exc")().cast<std::string>()
                << "```";
            std::flush(std::cout);
        }
    }*/

    return 0;
}
