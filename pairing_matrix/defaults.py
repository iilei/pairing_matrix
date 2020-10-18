import functools

from config42 import ConfigManager
from dotenv import find_dotenv


DEFAULT_CONFIG_PATH = '.default.pairing-matrix.conf.yaml'


@functools.lru_cache()
def get_config():
    config_file_path = find_dotenv(
        filename=DEFAULT_CONFIG_PATH, raise_error_if_not_found=True
    )

    return ConfigManager(path=config_file_path, extension='yaml').as_dict()


DEFAULT_CONFIG = get_config()
