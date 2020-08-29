#include "fork.h"

#include <pybind11/embed.h>

namespace py = pybind11;

void Fork::run()
{
    auto creator = py::module::import("lab.mergerequestcreator").attr("MergeRequestCreator")("master", true);
    creator.attr("fork");
}
