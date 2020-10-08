from . import BaseClient

# from gitlab import Gitlab


class GitlabClient(BaseClient):
    def __init__(self, timespan, **kwargs):
        self.base = BaseClient.__init__(self, timespan, **kwargs)

    # def instantiate_client(self):
    #     g = Gitlab()
