import ramda


def stats_to_matrix_prep(acc, cur):
    pair, count = cur
    pair_a, pair_b = pair.split('; ')
    print(pair, count)
    acc.append([[pair_a, pair_b, count], [pair_b, pair_a, count]])
    return acc


def stats_to_matrix(pair_stats, authors={}):
    result_stats = []
    pairs = ramda.to_pairs(pair_stats)
    _pair_list = ramda.reduce(stats_to_matrix_prep, [], pairs)
    pair_list = ramda.reduce(lambda acc, cur: [*acc, *cur], [], _pair_list)
    authors_emails = sorted(ramda.uniq(ramda.pluck(0, pair_list)))

    for author_a in authors_emails:
        author_a_pair_stats = []
        for author_b in authors_emails:
            if author_a == author_b:
                author_a_pair_stats.append(None)
            else:
                stat = ramda.find(
                    lambda pair: pair[0] == author_a and pair[1] == author_b, pair_list
                )
                author_a_pair_stats.append(stat[2])

        result_stats.append(
            {
                'author': authors.get(author_a, {}),
                'matrix': author_a_pair_stats,
            }
        )

    return result_stats

    # print(pair_list)
    #
    # [['jil.jonsen@example.com', 'jim.jensen@example.com', 8],
    #  ['jim.jensen@example.com', 'jil.jonsen@example.com', 8],
    #  ['jim.jensen@example.com', 'joy.joysen@example.com', 5],
    #  ['joy.joysen@example.com', 'jim.jensen@example.com', 5],
    #  ['jil.jonsen@example.com', 'joy.joysen@example.com', 3],
    #  ['joy.joysen@example.com', 'jil.jonsen@example.com', 3]]

    #     : jil | jim | joy
    # jil :  -     8     3
    # jim :  8     -     5
    # joy :  3     5     -
