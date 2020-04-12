from gitlab import Gitlab
from gitlab.v4.objects import Project, ProjectMergeRequest
from gitlab.exceptions import GitlabCreateError, GitlabAuthenticationError
from git import Repo

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils
from lab.editorinput import EditorInput

class MergeRequestCreator(RepositoryConnection):
    # private
    __remote_fork: Project
    __gitlab_token: str

    def __init__(self) -> None:
        RepositoryConnection.__init__(self)

    def fork(self) -> None:
        try:
            self.__remote_fork = self.remote_project().forks.create({})
            self.local_repo().create_remote("fork", url=self.__remote_fork.http_url_to_repo)
        except GitlabCreateError:
            print("Info: Fork already exists, continueing")
            id: str = Utils.str_id_for_url(self.local_repo().remotes.fork.url)
            self.__remote_fork = self.connection().projects.get(id)

        assert self.__remote_fork

    def push(self) -> None:
        self.local_repo().remotes.fork.push()

    def create_mr(self) -> None:
        e_input = EditorInput()

        try:
            mr = self.__remote_fork.mergerequests.create({
                "source_branch": self.local_repo().active_branch.name,
                "target_branch": "master",
                "title": e_input.title,
                "description": e_input.body,
                "target_project_id": self.remote_project().id
            })
            print("Info: Created merge request at", mr.web_url)
        except GitlabCreateError as e:
            if (e.response_code == 409):
                print("Info: Merge request already exists")
