import os

import arrow
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

    def get_commits(self):
        repo_matchers = self.repos_to_matchers()
        since, until = self.timespan
        repos = []

        # filter repos based on match-handlers
        for repo in self.client.get_user().get_repos():
            if ramda.any_pass(repo_matchers, repo.name):
                repos.append(repo)

                for c in repo.get_commits():
                    last_mod = arrow.get(c.commit.author.date)
                    message = c.commit.raw_data.get('message')

                    author = {
                        'email': c.commit.author.email,
                        'name': c.commit.author.name,
                    }

                    alias = self._output_aliases.get(c.commit.author.email)
                    if isinstance(alias, str) and c.author and c.author.login == alias:
                        author.update({**c.author.raw_data, 'alias': alias})

                    keep = last_mod <= until and last_mod >= since

                    if not keep:
                        if last_mod < since:
                            break
                        else:
                            print(1)
                    else:
                        self.track_author(**author)
                        self.track_pairing(author, *self.determine_coauthors(message))
