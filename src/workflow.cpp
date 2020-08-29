#include "workflow.h"

#include <pybind11/embed.h>

namespace py = pybind11;

void Workflow::run(bool fork, bool workbranch)
{
    auto repository_config = py::module::import("lab.config").attr("RepositoryConfig")();
    auto workflowEnum = py::module::import("lab.config").attr("Workflow");
    if (fork) {
        repository_config.attr("set_workflow")(workflowEnum(int(WorkflowType::ForkWorkflow)));
    } else if (workbranch) {
        repository_config.attr("set_workflow")(workflowEnum(int(WorkflowType::WorbranchWorkflow)));
    }
    repository_config.attr("save")();
}
