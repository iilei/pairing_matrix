import itertools
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
        self._output_aliases = self._options.get('output_aliases', {})

        self.apply_options()
        self.run()

    def run(self):
        self.get_pairs()

    def instantiate_client(self):
        return GenericClient(None)

    def apply_options(self):
        self.matchers = self.repos_to_matchers()
        self.client = self.instantiate_client()
        self.coauthor_trailer_regex = re.compile(
            self._options.get('pattern'), re.RegexFlag.MULTILINE
        )
        self.coauthor_regex = re.compile(COAUTHOR_NAME_EMAIL_REGEX)

    def track_pairing(self, *coauthors):
        coauthor_emails = ramda.uniq(
            ramda.map(lambda _coauthor: _coauthor.get('email'), coauthors)
        )
        pairs = itertools.combinations(coauthor_emails, 2)

        for _author in coauthors:
            self.track_author(**_author)

        for pair in pairs:
            _a, _b = pair
            _a = ramda.find(lambda a: a.get('email') == _a, coauthors)
            _b = ramda.find(lambda a: a.get('email') == _b, coauthors)
            self._pairs.append(
                ramda.sort_by(lambda x: x.email, (Author(**_a), Author(**_b)))
            )

    @property
    def pairs(self):
        return self._pairs

    @property
    def pair_stats(self):
        return ramda.count_by(
            lambda pair: f'{pair[0].email}; {pair[1].email}', self._pairs
        )

    @property
    def authors(self):
        return self._authors

    @authors.setter
    def authors(self, authors):
        self._authors = authors

    def update_author(self, email, **kwargs):
        [target_instance] = list(filter(lambda b: b.email == email, self._authors))
        target_instance.update(email=email, **kwargs)

    def track_author(self, email, **kwargs):
        if not self.find_author(email=email):
            self._authors.append(Author(email=email, **kwargs))
        else:
            self.update_author(email, **kwargs)

    def find_author(self, email):
        return ramda.find(lambda a: a.email == email, self._authors)

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

            found_author = self.find_author(email)
            if found_author:
                result.append(found_author.as_dict())
            else:
                result.append({'email': email, 'name': name})

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
