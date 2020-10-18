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
                    committer = c.committer.raw_data

                    author = {
                        'email': c.commit.author.email,
                        'name': c.commit.author.name,
                    }

                    if committer.get('email') == c.commit.author.email:
                        author.update(
                            {
                                'avatar': committer.get('avatar_url'),
                                'url': committer.get('html_url'),
                                'alias': committer.get('login'),
                            }
                        )

                    keep = last_mod >= since and until <= last_mod

                    self.track_author(**author)

                    if not keep:
                        if last_mod < since:
                            break
                        return

                    self.track_pairing(author, *self.determine_coauthors(message))

                    # TODO
                    # keep track of co-authored commit count
