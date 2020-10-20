import io
import textwrap

from faker import Faker
from github import Github

from pairing_matrix.pairing_matrix import main
from tests.author_mocks import authors

fake = Faker()
fake.seed_instance(4711)


class Author:
    def __init__(self, email, date='2020-10-03T10:04:09+00:00'):
        self.author = authors.get(email, {'email': email})
        self._date = date

    @property
    def login(self):
        return self.author.get('alias')

    @property
    def html_url(self):
        return self.author.get('html_url')

    @property
    def email(self):
        return self.author.get('email')

    @property
    def name(self):
        return self.author.get('name')

    @property
    def date(self):
        return self._date

    @property
    def raw_data(self):
        return {
            'email': self.email,
            'name': self.name,
            'avatar_url': self.author.get('avatar_url'),
            'html_url': self.author.get('html_url'),
            'alias': self.login,
        }


class Commit:
    def __init__(self, author_a, *co_authors, date='2020-10-03T10:04:09+00:00'):
        self._co_authors = co_authors
        self._committer = author_a
        self._date = date

    @property
    def commit(self):
        return self

    @property
    def avatar_url(self):
        return self.get_raw_data().get('avatar_url')

    @property
    def html_url(self):
        return self.get_raw_data().get('html_url')

    @property
    def alias(self):
        return self.get_raw_data().get('alias')

    @property
    def committer(self):
        return Author(self._committer, date=self._date)

    @property
    def author(self):
        return Author(self._committer, date=self._date)

    @property
    def raw_data(self):
        return self.get_raw_data()

    def get_raw_data(self):
        co_author_trailer_lines = []
        co_author_mentions = []

        for co_author in self._co_authors:
            _author = authors.get(co_author)
            _name = _author.get('name')
            _alias = _author.get('alias')
            co_author_trailer_lines.append(f'Co-authored-by: {_name} <{co_author}>')
            co_author_mentions.append(f'{fake.sentence()} Thanks to @{_alias}!')
        co_author_mentions = '\n'.join(co_author_mentions)
        co_author_trailer_lines = '\n'.join(co_author_trailer_lines)

        return {
            'message': textwrap.dedent(
                f"""
                feat: Some random {fake.word()}

                {fake.sentence()} ...

                {co_author_mentions}

                {co_author_trailer_lines}
            """
            ).strip()
        }


class MockGHGetRepos:
    @property
    def name(self):
        return 'pairing_matrix'

    @staticmethod
    def get_commits(
        since='2020-10-01T21:59:59+00:00', until='2020-10-01T22:59:59+00:00'
    ):
        return [
            # a commit just one second after the time frame of interest
            Commit(
                'jim.jensen@example.com',
                'joy.joysen@example.com',
                date='2020-10-03T22:00:01+00:00',
            ),
            Commit(
                'jim.jensen@example.com',
                'jil.jonsen@example.com',
                'joy.joysen@example.com',
            ),
            Commit(
                'joy.joysen@example.com',
            ),
            Commit(
                'joy.joysen@example.com',
            ),
            Commit(
                'joy.joysen@example.com',
            ),
            Commit(
                'jil.jonsen@example.com',
                'joy.joysen@example.com',
            ),
            Commit(
                'jil.jonsen@example.com',
                'joy.joysen@example.com',
            ),
            Commit(
                'jil.jonsen@example.com',
                'joy.joysen@example.com',
            ),
            Commit(
                'jil.jonsen@example.com',
                'joy.joysen@example.com',
            ),
            Commit(
                'jim.jensen@example.com',
                'joy.joysen@example.com',
            ),
            Commit(
                'jim.jensen@example.com',
            ),
            Commit(
                'jim.jensen@example.com',
            ),
            # a commit just one second before the time frame of interest
            Commit(
                'jim.jensen@example.com',
                'joy.joysen@example.com',
                date='2020-10-02T21:59:59+00:00',
            ),
        ]


class MockGHGetUser:
    @staticmethod
    def get_repos():
        return [MockGHGetRepos()]


def test_pairing_matrix(monkeypatch):
    def mock_get_user(_):
        return MockGHGetUser()

    monkeypatch.setattr('sys.stdin', io.StringIO(''))
    monkeypatch.setattr(Github, 'get_user', mock_get_user)
    # todo mock gilab client

    result = main(
        argv=[
            '--config-path',
            '.test.pairing-matrix.conf.yaml',
            '--config-format',
            'yaml',
            '--timespan',
            'now-1d/d - now Europe/Berlin (now: 2020-10-04T22:00:00+00:00)',
        ]
    )

    assert result.matrix == [
        {
            'author': {
                'email': 'jil.jonsen@example.com',
                'name': 'Jil Jonsen',
                'avatar_url': 'https://example.com/user/img/jil',
                'html_url': 'https://example.com/user/jil',
                'alias': 'jil',
                'profile_url': 'https://example.com/user/jil',
            },
            'matrix': [None, 1, 5],
        },
        {
            'author': {
                'email': 'jim.jensen@example.com',
                'name': 'Jim Jensen',
                'profile_url': None,
                'avatar_url': None,
                'alias': 'Jim Jensen',
            },
            'matrix': [1, None, 2],
        },
        {
            'author': {
                'email': 'joy.joysen@example.com',
                'name': 'Joy Joysen',
                'avatar_url': 'https://example.com/user/img/joy',
                'html_url': 'https://example.com/user/joy',
                'alias': 'joy',
                'profile_url': 'https://example.com/user/joy',
            },
            'matrix': [5, 2, None],
        },
    ]

    assert result.authors == {
        'joy.joysen@example.com': {
            'email': 'joy.joysen@example.com',
            'name': 'Joy Joysen',
            'avatar_url': 'https://example.com/user/img/joy',
            'html_url': 'https://example.com/user/joy',
            'alias': 'joy',
            'profile_url': 'https://example.com/user/joy',
        },
        'jil.jonsen@example.com': {
            'email': 'jil.jonsen@example.com',
            'name': 'Jil Jonsen',
            'avatar_url': 'https://example.com/user/img/jil',
            'html_url': 'https://example.com/user/jil',
            'alias': 'jil',
            'profile_url': 'https://example.com/user/jil',
        },
        'jim.jensen@example.com': {
            'email': 'jim.jensen@example.com',
            'name': 'Jim Jensen',
            'profile_url': None,
            'avatar_url': None,
            'alias': 'Jim Jensen',
        },
    }
