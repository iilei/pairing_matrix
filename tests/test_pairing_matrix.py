import io

from pairing_matrix.pairing_matrix import main
from dotenv import find_dotenv, load_dotenv

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
                'now-14d/d - now+1d/d Europe/Berlin',
            ]
        )
        == 0
    )
