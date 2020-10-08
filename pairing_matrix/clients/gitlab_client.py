from . import BaseClient
from gitlab import Gitlab


class GitlabClient(BaseClient):
    def __init__(self, **kwargs):
        BaseClient.__init__(**kwargs)

    def instantiate_client(self):
        g = Gitlab()
