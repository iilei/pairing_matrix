#! /usr/bin/env python
import argparse
import os
import re
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import ramda
from config42 import ConfigManager
from datemath import dm as datemath
from deepmerge import Merger
from dotenv import find_dotenv
from git import Repo
from pytz import all_timezones

from pairing_matrix.client import GithubClient
from pairing_matrix.client import GitlabClient
from pairing_matrix.defaults import DEFAULT_CONFIG
from pairing_matrix.stats_to_matrix import stats_to_matrix

author_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [(list, ['override']), (dict, ['merge'])],
    # next, choose the fallback strategies,
    # applied to all other types:
    ['override'],
    # finally, choose the strategies in
    # the case where the types conflict:
    ['override'],
)


class Main:
    def __init__(self, config):
        self.clients_available = {
            'gitlab': GitlabClient,
            'github': GithubClient,
        }
        self.APIS_AVAILABLE = self.clients_available.keys()
        self.config = config
        self.NOW_REGEX = r'[\(;,]?\s*\bnow:\s*([^\s\);,]+)\s*\)?'
        self.options = self.config.get('options')
        self.client_configs = self.config.get('clients')
        timespan_string = self.config.get('timespan', DEFAULT_CONFIG.get('timespan'))
        self.fallback_pattern = self.config.get('pattern', DEFAULT_CONFIG.get('pattern'))

        self.timespan = self.get_time_range(timespan_string)

        self.client_handlers = self.map_apis_to_client_handlers()
        self._pair_stats = []
        self._authors = []
        self.pair_stats = {}
        self.authors = {}
        for handler in self.client_handlers:
            self._pair_stats.append(handler.pair_stats)
            self._authors.append(handler.authors)

        self.accumulate_pair_stats()
        self.accumulate_authors()

        self.matrix = stats_to_matrix(self.pair_stats, authors=self.authors)

    def accumulate_authors(self):
        _result = {}
        aliases = self.config.get('output', {}).get('aliases', {})
        for (_email, _alias) in aliases.items():
            _result[_email] = {'alias': _alias}

        _authors_instances = ramda.flatten(self._authors)
        for _author_instance in _authors_instances:
            _author = _author_instance.as_dict()
            _email = _author.get('email')
            _known = _result.get(_email, {})
            _result[_email] = author_merger.merge(_author, _known)
        self.authors = _result

    def accumulate_pair_stats(self):
        self.pair_stats = ramda.reduce(
            lambda a, b: ramda.merge_with(lambda _a, _b: _a + _b, a, b),
            {},
            self._pair_stats,
        )

    # def map_emails_to_aliases(self):

    def map_apis_to_client_handlers(
        self,
    ) -> List[Union[GithubClient, GitlabClient]]:
        handlers = []
        for client_config in self.client_configs:
            api = self.get_or_guess_api(client_config)
            client = self.clients_available.get(api)(
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


merge_config = Merger(
    [(list, ['override']), (dict, ['merge'])], ['override'], ['override']
).merge


def main(argv: Optional[Sequence[str]] = None) -> int:
    # tbd; use click ?
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-path',
        type=str,
        default='.pairing-matrix.conf.yaml',
        help='Path to configuration',
    )
    parser.add_argument(
        '--config-format',
        type=str,
        default='yaml',
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

    config_file_path = find_dotenv(
        filename=args.config_path, raise_error_if_not_found=True
    )

    user_config = ConfigManager(
        path=config_file_path, extension=args.config_format
    ).as_dict()
    config = merge_config(DEFAULT_CONFIG, user_config)
    config = merge_config(config, vars(args))

    try:
        output_opts = config.get('output', {})
        highlight = output_opts.get('highlight_user')
        if highlight and not isinstance(highlight, str):
            user_email = (
                Repo(os.path.dirname(config_file_path))
                .config_reader()
                .get('user', 'email')
            )
            output_opts['highlight_user'] = user_email
        config = merge_config(config, {'output': output_opts})
    except:  # noqa
        pass

    Main(config)

    return 0
