import os
import arrow
from . import BaseClient
from github import Github
import ramda


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
                    author_email = c.commit.author.email
                    author_name = c.commit.author.name
                    author_avatar = c.commit.author.raw_data.get('avatar_url')
                    author_url = c.commit.author.raw_data.get('url')

                    keep = last_mod >= since and until <= last_mod

                    self.track_author(
                        email=author_email,
                        name=author_name,
                        url=author_url,
                        avatar=author_avatar,
                    )

                    if keep:
                        print(last_mod, message)

                    if last_mod < since:
                        break

        repo.get_commits()
