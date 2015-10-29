#!/usr/bin/python

import pandas as pd

from pandas import read_csv
from sys import argv


def get_data(golfer):
    file_name = golfer + '.csv'
    return read_csv(file_name, parse_dates=['date'], index_col='index')


def save_data(d, golfer):
    file_name = golfer + '.csv'
    d.to_csv(file_name, float_format='%.1f')


def calc_handicap(d):
    diffs = [i for i in (d['adj_score'] - d['rating']) * 113 / d['slope']]
    num_of_scores = len(diffs)
    diffs_used_table = {5: 1, 6: 1, 7: 2, 8: 2, 9: 3, 10: 3, 11: 4, 12: 4,
                        13: 5, 14: 5, 15: 6, 16: 6, 17: 7, 18: 8, 19: 9}
    if num_of_scores < 5:
        print('not enough scores')
        return False
    elif num_of_scores > 19:
        num_of_diffs = 10
    else:
        num_of_diffs = diffs_used_table[num_of_scores]

    diffs = sorted(diffs)[:num_of_diffs]
    return sum(diffs) / len(diffs) * .96


def average(s):
    return s.sum()/len(s)


def ema(series, period):
    return pd.ewma(series, period)


def print_handicap(name):
    d = get_data(name)
    handicap = calc_handicap(d)
    if handicap:
        print(name + "'s handicap: " + str(handicap)[:4])


def print_stats(name):
    print(name + "'s stats:")

    d = get_data(name)
    handicap = str(calc_handicap(d))[:4]
    print('handicap: ' + handicap)

    scoring_avg = str(round(average(d['score']), 1))
    print('scoring avg: ' + scoring_avg)

    putting_avg = str(round(average(d['putts']), 2))
    print('putting avg: ' + putting_avg)


if __name__ == "__main__":

    if len(argv) == 2:
        name = argv[-1]
        print_handicap(name)
    elif argv[-1] == 'stats':
        name = argv[-2]
        print_stats(name)
