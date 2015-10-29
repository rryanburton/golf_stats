#!/usr/bin/python

import csv
import sys


def get_data(name):
    f_name = name + '.csv'
    with open(f_name, 'r') as f:
        reader = csv.reader(f)
        data = {int(row[0]): row[1:] for row in reader}

    for k in data:
        data[k][1] = float(data[k][1])
        for i in [2, 3, 4]:
            data[k][i] = int(data[k][i])

    return data


def calculate(name):
    d = get_data(name)
    diffs = [(d[r][4] - d[r][1]) * 113 / d[r][2] for r in d]

    num_of_scores = len(diffs)
    if num_of_scores < 5:
        print('need more than 5 scores')
        return None
    elif num_of_scores < 17:
        num_of_diffs = int(num_of_scores - num_of_scores/2 - 1.5)
    elif num_of_scores < 20:
        num_of_diffs = num_of_scores - 10
    else:
        num_of_diffs = 10

    diffs = sorted(diffs)[:num_of_diffs]

    return str(sum(diffs) / len(diffs) * .96)[:4]


def get_stats(name):
    d = get_data(name)
    scores = [d[r][-2] for r in d]
    scoring_avg = round(sum(scores)/len(scores), 1)

    return str(scoring_avg)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        name = sys.argv[-1]
        handicap = calculate(name)
        print(name + "'s handicap: " + handicap)
    elif sys.argv[-1] == 'stats':
        name = sys.argv[-2]
        scoring_avg = get_stats(name)
        handicap = calculate(name)
        print(name + "'s stats: ")
        print("scoring average: " + scoring_avg)
        print("handicap index: " + handicap)
    else:
        print('error')
