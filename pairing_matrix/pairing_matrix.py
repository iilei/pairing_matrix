#! /usr/bin/env python

import argparse

# import os
import asyncio
from typing import Optional, Sequence
from pytz import all_timezones

from config42 import ConfigManager
from dotenv import find_dotenv
from gitlab import Gitlab
from github import Github
from datemath import dm as datemath
import re

from .defaults import DEFAULT_CONFIG, DEFAULT_OPTS


APIS_AVAILABLE = ['github', 'gitlab']
NOW_REGEX = r'[\(;,]?\s*\bnow:\s*([^\s\);,]+)\s*\)?'


def get_time_range(timespan):
    (tz,) = list(
        filter(lambda _tz: re.match(fr'.*\b{_tz}\b.*', timespan), all_timezones)
    ) or ['UTC']
    timespan = re.sub(fr'[ ;/\-\s,]*{tz}[ ;/\-\s,]*', ' ', timespan)
    now = re.search(NOW_REGEX, timespan)
    timespan = re.sub(NOW_REGEX, '', timespan).strip()
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


def get_or_guess_api(config):
    api = config.get('api', None)
    base_url = config.get('options', {}).get('base_url', '')
    if api:
        return api
    apis_by_base_url = list(filter(lambda _api: _api in base_url, APIS_AVAILABLE)) or [
        None
    ]

    if len(apis_by_base_url) == 1:
        return apis_by_base_url[0]
    raise AttributeError(f'Insufficient options for ${base_url}')


async def get_client(config):
    api = get_or_guess_api(config)
    # let's be defensive and not mutate the original config;
    options = config.get('options')

    if api == 'github':
        await get_github_history(options)
    else:
        await get_gitlab_history(options)


async def get_github_history(config):
    g = Github(**config)
    print(g)


async def get_gitlab_history(config):
    g = Gitlab(**config)
    print(g)


async def gather_commits(clients, from_time, to_time):
    await asyncio.gather(*map(get_client, clients))


def main(argv: Optional[Sequence[str]] = None) -> int:
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

    timespan_string = config.as_dict().get('timespan', DEFAULT_OPTS.get('timespan'))
    timespan = get_time_range(timespan_string)
    loop = asyncio.get_event_loop()
    clients = config.as_dict().get('clients')
    loop.run_until_complete(gather_commits(clients, *timespan))

    return 0
