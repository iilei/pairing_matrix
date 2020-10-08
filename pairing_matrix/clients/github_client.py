import os

from . import BaseClient
from github import Github
import ramda


class GithubClient(BaseClient):
    def __init__(self, **kwargs):
        self.base = BaseClient.__init__(self, **kwargs)

    def instantiate_client(self):
        return Github(
            **{
                **self._options.get('options'),
                'login_or_token': os.environ.get('ACCESS_TOKEN_GITHUB'),
            }
        )

    def get_commits(self):
        repo_matchers = self.repos_to_matchers()
        repos = []

        # filter repos based on match-handlers
        for repo in self.client.get_user().get_repos():
            if ramda.any_pass(repo_matchers, repo.name):
                repos.append(repo)

        # proceed;
        # :param sha: string
        # :param path: string
        # :param since: datetime.datetime
        # :param until: datetime.datetime
        # :param author: string or :class:`github.NamedUser.NamedUser` or :class:`github.AuthenticatedUser.AuthenticatedUser`
        # :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.Commit.Commit`
        repo.get_commits(since='20220-01-01', until='20220-01-01')
