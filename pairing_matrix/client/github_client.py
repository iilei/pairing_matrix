import os

import ramda
from github import Github

from . import BaseClient


class GithubClient(BaseClient):
    def __init__(self, timespan, **kwargs):
        self.base = BaseClient.__init__(self, timespan, **kwargs)

    def instantiate_client(self):
        return Github(
            **{
                **self._options.get('options'),
                'login_or_token': os.environ.get('ACCESS_TOKEN_GITHUB'),
            }
        )

    def get_pairs(self):
        repo_matchers = self.repos_to_matchers()
        since, until = self.timespan
        repos = []
        search = self.options.get('search', None)

        if isinstance(search, str):
            search = [search]

        if len(search) == 0:
            _repos = self.client.get_user().get_repos()
        else:
            _repos = []
            for _search in search:
                _repos = [*_repos, *self.client.search_repositories(query=_search)]

        # filter repos based on match-handlers
        for repo in _repos:
            if ramda.any_pass(repo_matchers, repo.full_name) or ramda.any_pass(
                repo_matchers, repo.name
            ):
                repos.append(repo)

                for c in repo.get_commits(since=since, until=until):
                    message = c.commit.raw_data.get('message')

                    author = {
                        'email': c.commit.author.email,
                        'name': c.commit.author.name,
                    }

                    alias = self._output_aliases.get(c.commit.author.email)
                    if isinstance(alias, str) and c.author and c.author.login == alias:
                        author.update({**c.author.raw_data, 'alias': alias})

                    self.track_pairing(author, *self.determine_coauthors(message))
