DEFAULT_OPTS = {
    # absolute path or filename for directory tree traversal search
    'config_path': '.pairing-matrix.conf.yaml',
    # overrides the extension seen in `config_path` - useful when
    # subprocess redirection is employed
    # example;
    # pairing_matrix --config-path <( \
    #                       godotenv -f .env \
    #                       gomplate --file ./.test.pairing-matrix.conf.yaml
    #                ) --config-format yaml \
    #                --timespan
    #
    'config_format': 'yaml',
    # `<from> - <to> <TZ?> <now?>`
    # -- see https://github.com/nickmaccarthy/python-datemath
    'timespan': 'now-14d/d - now UTC',
}
DEFAULT_CONFIG = {
    'timespan': DEFAULT_OPTS.get('timespan'),
    'pattern': r'/(?<=Co-authored-by:\s)[^<\n]*[^\s<]/g',
    'clients': [],
}
