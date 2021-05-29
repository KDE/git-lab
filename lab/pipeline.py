"""
This module contains code for the pipeline command
"""
import argparse
import os
import sys
from enum import Enum
from typing import List, Optional, Dict

from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import ProjectPipeline

from lab.repositoryconnection import RepositoryConnection
from lab.table import Table
from lab.utils import TextFormatting, Utils, LogType


class PipelineStatus(Enum):
    """
    Currently supported Pipeline Status from Gitlab.

    Allowed : https://docs.gitlab.com/ce/api/pipelines.html#list-project-pipelines
    """

    WAITING = "waiting_for_resource"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    SCHEDULED = "scheduled"

    @classmethod
    def _missing_(cls, value: object) -> None:
        """
        Called if a given value does not exist.
        Supported in all version of Python since 3.6.
        """
        Utils.log(LogType.WARNING, f"Invalid status '{str(value)}'")
        sys.exit(1)

    @staticmethod
    def format(status: str) -> str:
        """
        Transform a status into a formatted string, that is a colored string.
        If no color is defined for the given status, this is a NO-OP.
        """
        formatting = {
            "success": TextFormatting.GREEN,
            "failed": TextFormatting.RED,
            "running": TextFormatting.BLUE,
            "canceled": TextFormatting.PURPLE,
            "pending": TextFormatting.BLUE,
            "waiting_for_resource": TextFormatting.YELLOW,
        }

        if status in formatting:
            # Only format if there is a defined color for the status
            return f"{formatting.get(status, '')}{status}{TextFormatting.END}"

        # If color is associated with the status, do nothing
        return status

    @property
    def formatted(self) -> str:
        """
        Formatted string representation of a status.
        """
        return self.format(str(self))

    @property
    def finished(self) -> bool:
        """
        Is the pipeline finished, that is either skipped, canceled, failed or succeeded.
        """
        finished_states = (
            PipelineStatus.SKIPPED,
            PipelineStatus.SUCCESS,
            PipelineStatus.FAILED,
            PipelineStatus.CANCELED,
        )
        return self in finished_states

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for pipeline command
    :param subparsers: subparsers object from global parser
    :return: search subparser
    """
    pipeline_parser: argparse.ArgumentParser = subparsers.add_parser(
        "pipeline", help="Fetch pipeline status from GitLab."
    )

    # Optionally filter by status. This is None by default.
    pipeline_parser.add_argument(
        "--status",
        help=f"Filter pipelines by status, one of: [{', '.join(str(s) for s in PipelineStatus)}]",
        metavar="",
        type=PipelineStatus,
        default=None,
        choices=list(PipelineStatus),
    )

    pipeline_parser.add_argument(
        "--ref",
        help="Filter pipelines by reference, e.g. 'master'",
        metavar="ref",
        type=str,
        nargs="?",
    )

    pipeline_parser.add_argument(
        "pipeline_id",
        help="Show pipeline by id if provided",
        metavar="pipeline_id",
        type=int,
        nargs="?",
    )

    return pipeline_parser


def run(args: argparse.Namespace) -> None:
    """
    :param args: parsed arguments
    """
    if args.pipeline_id is not None:
        pipeline: PipelineShow = PipelineShow(args.pipeline_id)
        print(pipeline)

    else:
        lister: PipelineList = PipelineList(args.status, ref=args.ref)
        lister.print_formatted_list()


class PipelineShow(RepositoryConnection):
    """
    Show single pipeline
    """

    def __init__(self, pipeline_id: int) -> None:
        RepositoryConnection.__init__(self)
        try:
            self.pipeline: ProjectPipeline = self._remote_project.pipelines.get(
                pipeline_id, lazy=False
            )
        except GitlabGetError:
            Utils.log(LogType.WARNING, f"No pipeline with ID {pipeline_id}")
            sys.exit(1)

    def __str__(self) -> str:
        """
        Human readable representation of a pipeline.
        Output looks like:
        "Pipeline #25794 for master triggered by some one(Someone) 2 months ago
        finished after 1m 52s with status: success"
        """
        status: PipelineStatus = PipelineStatus(self.pipeline.status)

        text_buffer: str = ""
        text_buffer += (
            f"Pipeline {TextFormatting.BOLD}#{self.pipeline.id}"
            + f"{TextFormatting.END} for {self.pipeline.ref} "
            + f"triggered by {self.pipeline.user['name']}({self.pipeline.user['username']}) "
            + f"{Utils.pretty_date(self.pipeline.created_at)} "
        )

        if status.finished:
            text_buffer += (
                f"finished after {Utils.pretty_time_delta(self.pipeline.duration or 0)} "
                + f"with status: {status.formatted}"
            )
        else:
            text_buffer += f"is currently {status.formatted}"

        text_buffer += os.linesep
        return text_buffer


class PipelineList(RepositoryConnection):
    """
    Search class
    """

    def __init__(self, status: Optional[PipelineStatus] = None, ref: Optional[str] = None) -> None:
        RepositoryConnection.__init__(self)

        self.status: Optional[PipelineStatus] = status
        self.ref: Optional[str] = ref

        if ref is not None and ref not in self._local_repo.refs:
            # Print a warning, if the ref is not found LOCALLY
            # The remote may contain refs, that do not exists inside the local copy,
            # therefore only a warning is printed.
            Utils.log(LogType.WARNING, f"Ref '{ref}' is not found locally.")

    def print_formatted_list(self) -> None:
        """
        Print the list of pipelines to terminal formatted as a table
        """
        table = Table()

        # Compute args that are sent to GitLab
        args: Dict[str, str] = {}
        if self.status is not None:
            # Only yield pipelines that have the specific status
            # If empty all pipelines will be returned by GitLab
            args["status"] = str(self.status)

        if self.ref is not None:
            # Only yield pipeline that match a given reference
            args["ref"] = self.ref

        # Build the printable table
        pipelines: List[ProjectPipeline] = self._remote_project.pipelines.list(**args)
        for pipeline in pipelines:
            row: List[str] = [
                TextFormatting.BOLD + "#" + str(pipeline.id) + TextFormatting.END,
                pipeline.ref,
                Utils.pretty_date(pipeline.created_at),
                PipelineStatus.format(pipeline.status),
            ]
            table.add_row(row)

        table.print()
