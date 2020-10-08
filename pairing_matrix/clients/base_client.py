import re

from typing import NewType, Union, Type
from github import Github
from gitlab import Gitlab

GenericClient = NewType('GenericClient', Union[Type[Github], Type[Gitlab], None])


class BaseClient:
    def __init__(self, **kwargs):
        self._options = {**kwargs}
        self.client = GenericClient(None)
        self.apply_options()

    def instantiate_client(self):
        return GenericClient(None)

    def apply_options(self):
        self.matchers = self.repos_to_matchers()
        self.client = self.instantiate_client()

    @property
    def options(self):
        return self.options

    @options.setter
    def options(self, value):
        self.options = value
        self.apply_options()

    def repos_to_matchers(self):
        matchers = []
        for repo in self._options.get('repos'):
            # determine regex / plain string
            if re.match(r'^/.+/$', repo):
                # strip slashes at the start and end
                regex = re.compile(repo[1:][:-1])
                matchers.append(lambda x: bool(regex.match(x)))
            else:
                matchers.append(lambda x: bool(x == repo))
        return matchers
