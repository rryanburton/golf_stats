#!/usr/bin/python

import pandas
import pickle
import sys


def get_courses():
    with open('data/courses.pk', 'rb') as f:
        data = pickle.load(f)
    return data


def save_courses(data):
    with open('data/courses.pk', 'wb') as f:
        pickle.dump(data, f)


def get_data(golfer):
    file_name = 'data/' + golfer + '.csv'
    return pandas.read_csv(file_name, parse_dates=['date'])


def save_data(data, golfer):
    file_name = golfer + '.csv'
    data.to_csv(file_name, float_format='%.1f')


def add_score(golfer):
    print('add new score')
    scorecard = [
        input('date: (yyyy-mm-dd) '),
        input('course: '),
        input('rating: '),
        input('slope: '),
    ]

    holes = [str(i) for i in range(1, 19)]
    print('enter scores')
    for i in holes:
        scorecard.append(input('hole ' + i + ': '))

    print('enter putts')
    for i in holes:
        scorecard.append(input('hole ' + i + ': '))

    score_csv = scorecard[0]
    for i in range(1, len(scorecard)):
        score_csv += ',' + scorecard[i]

    total, total_putts = 0, 0
    for i in range(4, 22):
        total += int(scorecard[i])
        total_putts += int(scorecard[i+18])

    print('scorecard:')
    print(score_csv)
    print('score: ', total)
    print('putts: ', total_putts)

    if input('correct? [y]/n: ') in ['y', 'yes', '']:
        with open('data/' + golfer + '.csv', 'a') as f:
            f.write(score_csv + '\n')


def fill_data(d):
    d['score'] = d.loc[:, '1':'18'].sum(axis=1)
    d['putts'] = d.loc[:, 'p1':'p18'].sum(axis=1)

    adj_scores = [d['score'][i] for i in range(len(d))]
    handicap_indexes = []
    pre_round_index = 50.0

    for i in range(len(d)):
        # go through each round, one at a time
        course_handicap = round(pre_round_index * d['slope'][i] / 113, 0)
        if course_handicap < 20:
            max_score = 7
        elif course_handicap < 30:
            max_score = 8
        else:
            max_score = 9

        # calculate adjusted score for current round
        adj_strokes = [min(d[c][i], max_score) for c in d.loc[:, '1':'18']]
        adj_scores[i] = (sum(adj_strokes))
        d['adj_score'] = adj_scores

        # use only last 20 rounds
        last = i + 1  # since pandas does not include endpoint
        round_handicap_index = calc_handicap(d[-20: last])
        handicap_indexes.append(round_handicap_index)
        pre_round_index = round_handicap_index

    d['hindex'] = handicap_indexes

    return d


def calc_handicap(d):
    diffs = [i for i in (d['adj_score'] - d['rating']) * 113 / d['slope']]
    num_of_scores = len(diffs)
    diffs_used_table = {
        5: 1, 6: 1, 7: 2, 8: 2, 9: 3, 10: 3, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 6, 16: 6, 17: 7, 18: 8, 19: 9, 20: 10
    }
    if num_of_scores < 5:
        return 50.0
    else:
        num_of_diffs = diffs_used_table[num_of_scores]

    diffs = sorted(diffs)[:num_of_diffs]
    return sum(diffs) / len(diffs) * .96


def average(series):
    return series.sum()/len(s)


def ema(series, period):
    return pandas.ewma(series, period)


def print_handicap(name):
    data = fill_data(get_data(name))
    handicap = str(data['hindex'][len(data)-1])[:4]
    print(name + "'s handicap: " + handicap)


def print_stats(name):
    print(name + "'s stats:")

    data = fill_data(get_data(name))
    handicap = str(data['hindex'][len(data)-1])[:4]
    print('handicap: ' + handicap)

    scoring_avg = str(round(sma(data['score'])[len(data)-1], 1))
    print('scoring avg: ' + scoring_avg)

    putting_avg = str(round(sma(data['putts'])[len(data)-1], 2))
    print('putting avg: ' + putting_avg)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        name = sys.argv[-1]
        print_handicap(name)
    elif sys.argv[-1] == 'stats':
        name = sys.argv[-2]
        print_stats(name)
    elif sys.argv[-1] == 'add':
        add_score(argv[-2])
    else:
        print('error with args')
