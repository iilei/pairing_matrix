# import re


class BaseClient:
    def __init__(self):
        self._options = {}

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value

    def repos_to_matchers(self, repos):
        return 0
        # matchers = []
        # for repo in repos:
        #     # determine regex / plain string
        #     if re.match(r'^/.+/$', repo):
        #         print(repo)
        #     else:
        #         print(repo)
