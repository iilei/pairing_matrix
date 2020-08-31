import argparse
from typing import Optional
from typing import Sequence
from config42 import ConfigManager
from config42.handlers import FileHandler
from pathlib import Path
import pprint

from .find_ancestor_file import find_ancestor_file

pp = pprint.PrettyPrinter(indent=4)


def pairing_matrix(conf):
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        type=str,
        default=".pairing-matrix.conf.yaml",
        help='Path to configuration file (yaml or json)',
    )

    args = parser.parse_args(argv)

    config_file_path = find_ancestor_file(str(Path.cwd()), args.config)
    config = ConfigManager(handler=FileHandler, path=config_file_path).handler.config

    pp.pprint(config)

    return 0


if __name__ == '__main__':
    exit(main())
