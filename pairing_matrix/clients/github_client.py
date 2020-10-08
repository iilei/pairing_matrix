from . import BaseClient


class GithubClient(BaseClient):
    def __init__(self, **kwargs):
        BaseClient.__init__(**kwargs)
