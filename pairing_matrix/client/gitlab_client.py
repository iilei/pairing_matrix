import os

import ramda
from gitlab import Gitlab

from . import BaseClient


class GitlabClient(BaseClient):
    def __init__(self, timespan, **kwargs):
        self.base = BaseClient.__init__(self, timespan, **kwargs)

    def instantiate_client(self):
        return Gitlab(
            **{
                **self._options.get('options'),
                'private_token': os.environ.get('ACCESS_TOKEN_GITLAB'),
                'url': os.environ.get('GITLAB_BASE_URL'),
            }
        )

    def get_pairs(self):
        repo_matchers = self.repos_to_matchers()

        since, until = self.timespan
        repos = []
        search = self.options.get('search', None)

        if not isinstance(search, list):
            search = [search]

        if len(search) == 0:
            search = [None]

        for _search in search:
            projects = self.client.projects.list(search=_search)
            for project in projects:
                if ramda.any_pass(
                    repo_matchers, project.path_with_namespace
                ) or ramda.any_pass(repo_matchers, project.name):
                    repos.append(project)

                    commits = project.commits.list(since=since, until=until)

                    for commit in commits:
                        message = commit.message
                        author = {
                            'name': commit.author_name,
                            'email': commit.author_email,
                        }

                        self.track_pairing(author, *self.determine_coauthors(message))
                else:
                    print(project.name)
