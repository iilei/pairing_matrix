import io

from dotenv import find_dotenv
from dotenv import load_dotenv

from pairing_matrix.pairing_matrix import main

load_dotenv(find_dotenv('.test.env'))


def test_pairing_matrix(monkeypatch):
    monkeypatch.setattr('sys.stdin', io.StringIO(''))
    assert (
        main(
            argv=[
                '--config-path',
                '.test.pairing-matrix.conf.yaml',
                '--config-format',
                'yaml',
                '--timespan',
                'now-1d/d - now Europe/Berlin (now: 2020-10-04)',
            ]
        )
        == 0
    )
