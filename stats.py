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


def new_score(golfer):
    print('add new score')
    course = [
        input('date: '),
        input('course: '),
        input('rating: '),
        input('slope: ')
    ]

    holes = [i for i in range(1, 19)]
    print('enter scores')
    scores = [input('hole ' + str(i) + ': ') for i in holes]
    print('enter putts')
    putts = [input('hole ' + str(i) + ': ') for i in holes]

    scorecard = course + scores + putts
    return scorecard


def fill_data(d):
    d['score'] = d.loc[:, '1':'18'].sum(axis=1)
    d['putts'] = d.loc[:, 'p1':'p18'].sum(axis=1)

    adj_scores = [d['score'][i] for i in range(len(d))]
    handicap_indexes = []
    pre_round_index = 50.0

    for i in range(len(d)):
        course_handicap = round(pre_round_index * d['slope'][i] / 113, 0)
        if course_handicap < 20:
            max_score = 7
        elif course_handicap < 30:
            max_score = 8
        else:
            max_score = 9

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

    d = fill_data(get_data(name))
    handicap = str(d['hindex'][len(d)-1])[:4]
    print('handicap: ' + handicap)

    scoring_avg = str(round(ema(d['score'], 20)[len(d)-1], 1))
    print('scoring avg: ' + scoring_avg)

    putting_avg = str(round(ema(d['putts'], 20)[len(d)-1], 2))
    print('putting avg: ' + putting_avg)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        name = sys.argv[-1]
        print_handicap(name)
    elif sys.argv[-1] == 'stats':
        name = sys.argv[-2]
        print_stats(name)
