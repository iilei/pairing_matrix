#! /usr/bin/env python

import argparse

# import os
import asyncio
import os
from typing import Optional, Sequence, Union, List, Type
from pytz import all_timezones

from config42 import ConfigManager
from dotenv import find_dotenv
from datemath import dm as datemath
import pairing_matrix.clients as clients

import re

from .defaults import DEFAULT_CONFIG, DEFAULT_OPTS


class Main:
    def __init__(self, config):
        self.config = config.as_dict()
        self.APIS_AVAILABLE = ['github', 'gitlab']
        self.NOW_REGEX = r'[\(;,]?\s*\bnow:\s*([^\s\);,]+)\s*\)?'
        self.options = self.config.get('options')
        self.client_configs = self.config.get('clients')
        self.client_handlers = self.map_apis_to_client_handlers()
        timespan_string = self.config.get('timespan', DEFAULT_OPTS.get('timespan'))
        self.timespan = self.get_time_range(timespan_string)

        for handler in self.client_handlers:
            print(handler.get_commits())

    def map_apis_to_client_handlers(
        self,
    ) -> List[Union[Type[clients.GithubClient], Type[clients.GitlabClient]]]:
        handlers = []
        for client_config in self.client_configs:
            api = self.get_or_guess_api(client_config)
            # based on the api name (e.g 'github'),
            # derive the respective class name (e.g. 'GithubClient')
            client = getattr(clients, f'{api.capitalize()}Client')(**client_config)
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

    # async def get_client(self, config):
    #     api = self.get_or_guess_api(config)
    #     # let's be defensive and not mutate the original config;
    #     options = config.get('options')
    #     repos = config.get('repos')
    #
    #     if api == 'github':
    #         await self.get_github_history(options, repos)
    #     else:
    #         await self.get_gitlab_history(options, repos)

    # async def get_github_history(self, config, repos):
    #     # testing
    #     _config = {**config, 'login_or_token': os.environ.get('ACCESS_TOKEN_GITHUB')}
    #
    #     g = Github(**_config)
    #     for repo in g.get_user().get_repos():
    #         if repo.name in repos:
    #             print(repo.name)
    #
    # async def get_gitlab_history(self, config):
    #     g = Gitlab(**config)
    #     print(g)
    #
    # async def gather_commits(self, clients, from_time, to_time):
    #     await asyncio.gather(*map(self.get_client, clients))


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
