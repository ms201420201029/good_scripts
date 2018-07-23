import pandas as pd
import numpy as np
import collections
import argparse
import sys


class colors:
    BLACK         = '\033[0;30m'
    DARK_GRAY     = '\033[1;30m'
    LIGHT_GRAY    = '\033[0;37m'
    BLUE          = '\033[0;34m'
    LIGHT_BLUE    = '\033[1;34m'
    GREEN         = '\033[0;32m'
    LIGHT_GREEN   = '\033[1;32m'
    CYAN          = '\033[0;36m'
    LIGHT_CYAN    = '\033[1;36m'
    RED           = '\033[0;31m'
    LIGHT_RED     = '\033[1;31m'
    PURPLE        = '\033[0;35m'
    LIGHT_PURPLE  = '\033[1;35m'
    BROWN         = '\033[0;33m'
    YELLOW        = '\033[1;33m'
    WHITE         = '\033[1;37m'
    DEFAULT_COLOR = '\033[00m'
    RED_BOLD      = '\033[01;31m'
    ENDC          = '\033[0m'


def readParams():
    parser = argparse.ArgumentParser(description='Read parameters')
    parser.add_argument('-i', '--file', dest='file', metavar='file', type=str, default=None, required=False)
    parser.add_argument('-o', '--outfile', dest='outfile', metavar='outfile', type=str, required=True)
    args = parser.parse_args()
    params = vars(args)
    return params


def changeVisual(info, split, outfile, info_type='file'):
    if info_type == 'file':
        with open(info, 'r') as f:
            lines = f.readlines()
            lines = [line.rstrip('\n') for line in lines]
    else:
        lines = info.split('\n')[:-1]
    lines_split = [line.split(split) for line in lines]
    columns = max([len(l) for l in lines_split])
    rows = len(lines)
    data = pd.DataFrame(np.zeros([rows,columns]))
    for i in range(len(lines_split)):
        for j in range(len(lines_split[i])):
            data[j][i] = len(lines_split[i][j])
    columns_max = list(data.describe().loc['max'])

    # 直接打印
    with open(outfile, 'w') as fn:

        fn.write(colors.RED + '-'* int(sum(columns_max) +len(columns_max)*3+1) + colors.ENDC)
        fn.write('\n')
        for i in range(len(lines_split)):
            fn.write('|')
            for j in range(len(lines_split[i])):
                fn.write(' ' + lines_split[i][j] + ' '*int(columns_max[j]-len(lines_split[i][j])+1) + '|')
            fn.write('\n')
        fn.write('-' * int(sum(columns_max) + len(columns_max) * 3 + 1))


def change_all(info, outfile, info_type='file'):
    top_5lines = []
    if info_type == 'file':
        with open(info, 'r') as f:
            for i in range(5):
                top_5lines.append(f.readline().rstrip('\n'))
    else:
        txt_list = txt.split('\n')[:-1]
        if len(txt_list) >= 5:
            for i in range(5):
                top_5lines.append(f.readline().rstrip('\n'))
        else:
            top_5lines = txt_list

    split_number = []
    splits = ['\t',' ',',']
    for s in splits:
        split_number.append([len(i.split(s)) for i in top_5lines])
        if len(set(split_number[-1])) == 1 and split_number[-1][1] != 1:
            split = s
            break

    try:
        # split exists
        split
        changeVisual(info, split, outfile, info_type)

    except:
        result = []
        for l in range(len(split_number)):
            split_number[l] = [i for i in split_number[l] if i != 1]
        for l in split_number:
            count = collections.Counter(l)
            summ = 0
            for i in count:
                summ += i**count[i]
            result.append(summ)
        index = result.index(max(result))
        split = splits[index]
        changeVisual(info, split, outfile, info_type)


if __name__ == '__main__':
    file = readParams()['file']
    outfile = readParams()['outfile']
    if file:
        change_all(file, outfile, info_type='file')
    else:
        txt = sys.stdin.read()
        change_all(txt, outfile, info_type='txt')

