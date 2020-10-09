import re
from typing import NewType
from typing import Type
from typing import Union

import ramda
from github import Github
from gitlab import Gitlab

from pairing_matrix.author import Author

GenericClient = NewType('GenericClient', Union[Type[Github], Type[Gitlab], None])

COAUTHOR_STRING_TEMPLATE = '{name} <{email}>'
COAUTHOR_NAME_EMAIL_REGEX = r'(\b.+\b)\s*<(.*)>'


class BaseClient:
    def __init__(self, timespan, **kwargs):
        self._options = {**kwargs}
        self.client = GenericClient(None)
        self.timespan = timespan
        self._authors = []
        self._pairs = []

        self.apply_options()
        self.run()

    def run(self):
        self.get_commits()

    def instantiate_client(self):
        return GenericClient(None)

    def apply_options(self):
        self.matchers = self.repos_to_matchers()
        self.client = self.instantiate_client()
        self.coauthor_trailer_regex = re.compile(
            self._options.get('pattern'), re.RegexFlag.MULTILINE
        )
        self.coauthor_regex = re.compile(COAUTHOR_NAME_EMAIL_REGEX)

    def track_pairing(self, author_a, author_b):
        pair = sorted((author_a, author_b), key=lambda author: author.email)
        self._pairs.append(pair)

    @property
    def pairs(self):
        return self._pairs

    @property
    def authors(self):
        return self._authors

    @authors.setter
    def authors(self, authors):
        self._authors = authors

    def author_is_tracked(self, email):
        return ramda.any(lambda a: a.email == email, self._authors)

    def update_author(self, author):
        [target_instance] = list(
            filter(lambda b: b.email == author.email, self._authors)
        )
        target_instance.update(
            email=author.email, name=author.name, url=author.url, avatar=author.avatar
        )

    def track_author(self, author):
        if not self.author_is_tracked(email=author.email):
            self._authors.append(author)
        else:
            self.update_author(author)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        self.apply_options()

    def determine_coauthors(self, msg=''):
        coauthors = self.coauthor_trailer_regex.findall(msg)
        result = []
        for coauthor in coauthors:
            found = self.coauthor_regex.findall(coauthor)
            if found and len(found) != 1:
                next()
            name, email = found[0]
            result.append(Author(email=email, name=name))
        return result

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
