from lab.repositoryconnection import RepositoryConnection
from gitlab.v4.objects import ProjectMergeRequest


class MergeRequestCheckout(RepositoryConnection):
    # private
    __mr: ProjectMergeRequest

    def __init__(self):
        RepositoryConnection.__init__(self)

    def checkout(self, id: int):
        self.__mr = self.remote_project().mergerequests.get(id, lazy=False)
        print("Checking out merge request \"{}\"...".format(self.__mr.title))
        print("  branch:", self.__mr.source_branch)

        fetch_info = self.local_repo().remotes.origin.fetch("merge-requests/{}/head".format(id))[0]
        head = self.local_repo().create_head(self.__mr.source_branch, fetch_info.ref)
        head.checkout()
