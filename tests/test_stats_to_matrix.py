import json

import numpy as np
import pandas as pd

from pairing_matrix.stats_to_matrix import stats_to_matrix

EXAMPLE_STATS = {
    'jil.jonsen@example.com; jim.jensen@example.com': 8,
    'jim.jensen@example.com; joy.joysen@example.com': 5,
    'jil.jonsen@example.com; joy.joysen@example.com': 3,
}

authors = {
    'joy.joysen@example.com': {
        'email': 'joy.joysen@example.com',
        'name': 'Joy Joysen',
        'url': None,
        'avatar': None,
        'alias': 'joy',
    },
    'jil.jonsen@example.com': {
        'email': 'jil.jonsen@example.com',
        'name': 'Jil Jonsen',
        'url': None,
        'avatar': None,
        'alias': 'jil',
    },
    'jim.jensen@example.com': {
        'email': 'jim.jensen@example.com',
        'name': 'Jim Jensen',
        'url': None,
        'avatar': None,
        'alias': 'jim',
    },
}


def test_stats_to_matrix():
    stats = stats_to_matrix(EXAMPLE_STATS, authors=authors)
    assert stats == [
        {
            'author': {
                'email': 'jil.jonsen@example.com',
                'name': 'Jil Jonsen',
                'url': None,
                'avatar': None,
                'alias': 'jil',
            },
            'matrix': [None, 8, 3],
        },
        {
            'author': {
                'email': 'jim.jensen@example.com',
                'name': 'Jim Jensen',
                'url': None,
                'avatar': None,
                'alias': 'jim',
            },
            'matrix': [8, None, 5],
        },
        {
            'author': {
                'email': 'joy.joysen@example.com',
                'name': 'Joy Joysen',
                'url': None,
                'avatar': None,
                'alias': 'joy',
            },
            'matrix': [3, 5, None],
        },
    ]

    json.dumps(stats)

    raw_data = pd.DataFrame(stats)
    _indexes = raw_data.author.apply(lambda x: x.get('alias')).values
    concise_data = (
        pd.DataFrame(
            [*raw_data.matrix.values],
            index=_indexes,
            columns=_indexes,
            dtype=np.dtype('int32'),
        )
        .fillna(value='-')
        .astype(float, errors='ignore')
    )
    # by adding two spaces, tabulate does not mistreat vales as floats
    concise_data = concise_data.applymap(lambda x: x if '-' == ' - ' else f' {int(x)} ')

    print(
        concise_data.to_markdown(
            tablefmt='fancy_grid', stralign='center', colalign=('right', 'center')
        )
    )

    print(concise_data.to_markdown(stralign='center', colalign=('right', 'center')))
    print(concise_data.to_string())
    print(concise_data.to_csv())
    print(raw_data.to_json(orient='records'))

    # |     |  jil  |  jim  |  joy  |
    # |----:|:-----:|:-----:|:-----:|
    # | jil |   -   |   8   |   3   |
    # | jim |   8   |   -   |   5   |
    # | joy |   3   |   5   |   -   |
