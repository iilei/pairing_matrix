from pairing_matrix.stats_to_matrix import stats_to_matrix

EXAMPLE_STATS = {
    'jil.jonsen@example.com; jim.jensen@example.com': 8,
    'jim.jensen@example.com; joy.joysen@example.com': 5,
    'jil.jonsen@example.com; joy.joysen@example.com': 3,
}


def test_stats_to_matrix():
    stats = stats_to_matrix(EXAMPLE_STATS)
    assert stats == [
        ['jil.jonsen@example.com', [None, 8, 3]],
        ['jim.jensen@example.com', [8, None, 5]],
        ['joy.joysen@example.com', [3, 5, None]],
    ]
