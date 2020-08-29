#pragma once

class Workflow
{
public:
    enum WorkflowType {
        ForkWorkflow = 1,
        WorbranchWorkflow
    };

    Workflow() = delete;
    static void run(bool fork, bool workbranch);
};
