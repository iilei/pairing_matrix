#! /usr/bin/env python
import argparse
import re
from typing import List
from typing import Optional
from typing import Sequence
from typing import Type
from typing import Union

from config42 import ConfigManager
from datemath import dm as datemath
from dotenv import find_dotenv
from pytz import all_timezones

from .defaults import DEFAULT_CONFIG
from .defaults import DEFAULT_OPTS
from pairing_matrix.client import GithubClient
from pairing_matrix.client import GitlabClient


class Main:
    def __init__(self, config):
        self.config = config.as_dict()
        self.APIS_AVAILABLE = ['github', 'gitlab']
        self.NOW_REGEX = r'[\(;,]?\s*\bnow:\s*([^\s\);,]+)\s*\)?'
        self.options = self.config.get('options')
        self.client_configs = self.config.get('clients')
        timespan_string = self.config.get('timespan', DEFAULT_OPTS.get('timespan'))
        self.fallback_pattern = self.config.get('pattern', DEFAULT_CONFIG.get('pattern'))

        self.timespan = self.get_time_range(timespan_string)

        self.client_handlers = self.map_apis_to_client_handlers()
        for handler in self.client_handlers:
            print(handler.pairs)

    def map_apis_to_client_handlers(
        self,
    ) -> List[Union[Type[GithubClient], Type[GitlabClient]]]:
        _clients = {
            'gitlab': GitlabClient,
            'github': GithubClient,
        }
        handlers = []
        for client_config in self.client_configs:
            api = self.get_or_guess_api(client_config)
            client = _clients.get(api)(
                timespan=self.timespan,
                **{
                    **client_config,
                    'pattern': client_config.get('client_config', self.fallback_pattern),
                },
            )
            handlers.append(client)
        return handlers

    def get_time_range(self, timespan):
        (tz,) = list(
            filter(lambda _tz: re.match(fr'.*\b{_tz}\b.*', timespan), all_timezones)
        ) or ['UTC']
        timespan = re.sub(fr'[ ;/\-\s,]*{tz}[ ;/\-\s,]*', ' ', timespan)
        now = re.search(self.NOW_REGEX, timespan)
        timespan = re.sub(self.NOW_REGEX, '', timespan).strip()
        src_timestamp = None
        if now and now[1]:
            src_timestamp = datemath(now[1])

        _time_a, _time_b = re.split(re.compile(r'\s+-\s+'), timespan)
        from_to = [
            datemath(_time_a.strip(), tz=tz, now=src_timestamp),
            datemath(_time_b.strip(), tz=tz, now=src_timestamp),
        ]
        from_to.sort()
        return from_to

    def get_or_guess_api(self, config):
        api = config.get('api', None)
        base_url = config.get('options', {}).get('base_url', '')
        if api:
            return api
        apis_by_base_url = list(
            filter(lambda _api: _api in base_url, self.APIS_AVAILABLE)
        ) or [None]

        if len(apis_by_base_url) == 1:
            return apis_by_base_url[0]

        raise AttributeError(f'Insufficient options for ${base_url}')


def main(argv: Optional[Sequence[str]] = None) -> int:
    # tbd; use click ?
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-path',
        type=str,
        default=DEFAULT_OPTS.get('config_path'),
        help='Path to configuration',
    )
    parser.add_argument(
        '--config-format',
        type=str,
        default=DEFAULT_OPTS.get('config_format'),
        help='Enforce config file parser; <[yaml]|json|ini|raw>',
    )
    parser.add_argument(
        '--timespan',
        type=str,
        default=None,
        help='\n'.join(
            [
                'Timespan `<from> - <to> <TZ?> <now?>`',
                'See https://github.com/nickmaccarthy/python-datemath.'
                'If it contains a timezone, that will be taken into account, too.',
            ]
        ),
    )

    args = parser.parse_args(argv)
    config = ConfigManager()
    config.set_many(DEFAULT_CONFIG)

    config_file_path = find_dotenv(
        filename=args.config_path, raise_error_if_not_found=True
    )

    config.set_many(
        ConfigManager(path=config_file_path, extension=args.config_format).as_dict()
    )

    if args.timespan:
        config.set('timespan', args.timespan)

    Main(config)

    return 0
