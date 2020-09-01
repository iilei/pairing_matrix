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


def get_time_range(timespan):
    (tz,) = list(
        filter(lambda _tz: re.match(fr'.*\b{_tz}\b.*', timespan), all_timezones)
    ) or ['UTC']
    timespan = re.sub(fr'[ ;/\-\s,]*{tz}[ ;/\-\s,]*', '', timespan)
    _time_a, _time_b = re.split(re.compile(r'\s+-\s+'), timespan)
    from_to = [datemath(_time_a, tz=tz), datemath(_time_b, tz=tz)]
    from_to.sort()
    return from_to


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
                'Timespan `<from> - <to> <TZ>`',
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

    print(*timespan)

    async def get_github_history(repo):
        g = Github(**repo)
        print(g)

    async def get_gitlab_history(repo):
        g = Gitlab(**repo)
        print(g)

    async def get_history():
        _apis = config.as_dict().get('apis', {})
        github_repos = _apis.get('github', [])
        gitlab_repos = _apis.get('gitlab', [])

        await asyncio.gather(
            *[
                *map(get_github_history, github_repos),
                *map(get_gitlab_history, gitlab_repos),
            ]
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_history())

    return 0
