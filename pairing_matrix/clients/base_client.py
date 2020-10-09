import re
from typing import NewType, Type, Union

import ramda
from github import Github
from gitlab import Gitlab

from pairing_matrix.author import Author

GenericClient = NewType('GenericClient', Union[Type[Github], Type[Gitlab], None])


class BaseClient:
    def __init__(self, timespan, **kwargs):
        self._options = {**kwargs}
        self.client = GenericClient(None)
        self.timespan = timespan
        self.apply_options()
        self._authors = []

    def instantiate_client(self):
        return GenericClient(None)

    def apply_options(self):
        self.matchers = self.repos_to_matchers()
        self.client = self.instantiate_client()

    @property
    def authors(self):
        return self._authors

    def author_is_tracked(self, email):
        ramda.any(lambda a: a.email == email, self._authors)

    def track_author(self, email, **kwargs):
        if not self.author_is_tracked(email=email):
            self._authors.append(Author(email=email, **kwargs))

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        self.apply_options()

    def repos_to_matchers(self):
        matchers = []
        repos = self._options.get('repos')

        if repos == '*':
            return [lambda: True]

        for repo in repos:
            # determine regex / plain string
            if re.match(r'^/.+/$', repo):
                # strip slashes at the start and end
                regex = re.compile(repo[1:][:-1])
                matchers.append(lambda x: bool(regex.match(x)))
            else:
                matchers.append(lambda x: bool(x == repo))
        return matchers
