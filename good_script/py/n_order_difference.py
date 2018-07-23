# !/usr/bin/python3
# -*- coding: utf-8 -*-
# calculate time series n order difference
# __author__ = mas

import argparse
import pandas as pd
import math


def read_params():
    parser = argparse.ArgumentParser(description='read params for n order difference.')
    parser.add_argument('-i', '--input', metavar='input', dest='input_file', required=True, type=str,
                        help='input abund file. first row is sample name, sample name should be SampleName_roundn (roundn is the n th sample of SampleName)')
    parser.add_argument('-u', '--unit', metavar='unit', dest='unit', required=True, type=str,
                        help='unit table file, it can show which place need to insert data.')
    parser.add_argument('-n', '--n_order', metavar='n_order', dest='n_order', type=int, default=1,
                        help='input n of n order difference.')
    args = parser.parse_args()
    params = vars(args)
    return params


def find_nan(l):
    nan_list = []
    nan = []
    for i, s in enumerate(l):
        if isinstance(s, str):
            if nan:
                nan_list.append(nan)
                nan = []
        else:
            nan.append(i)

    return l, nan_list


def insert_data(abund, unit):
    df = pd.DataFrame(index=abund.index)
    for u in list(unit.index):
        '''
        除去sample list中前面的和后面的nan，中间的nan则需要填充
        '''
        u_samples = list(unit.loc[u])
        for i, s in enumerate(u_samples):
            try:
                if math.isnan(u_samples[i]):
                    continue
            except:
                u_samples = u_samples[i:]
                break
        for i, s in enumerate(u_samples):
            try:
                if math.isnan(u_samples[-i-1]):
                    continue
            except:
                if not i == 0:
                    u_samples = u_samples[:-i]
                break

        # print(type(u), u_samples)
        '''
        找出个体当中nan的位置
        '''
        u_samples, nan_list = find_nan(u_samples)
        nan = []
        for i in nan_list:
            nan += i

        '''
        将非nan的sample填入到df中，并完成更名
        '''
        prefix = str(u)
        k = 0
        for i in range(len(u_samples)):
            if i not in nan:
                if k != 0:
                    print('because %d nan before, sample %s name change to %s' % (k, prefix + '_' + str(i+1-k), prefix + '_' + str(i+1)))
                else:
                    print('copy %s sample to df.' % (prefix + '_' + str(i+1)))
                df[prefix + '_' + str(i+1)] = abund[prefix + '_' + str(i+1-k)]
            else:
                k += 1

        '''
        将nan的sample填入到df中（由于样品顺序打乱，因此后面做差分需要根据样品名来计算）
        '''
        for na in nan_list:
            start = u_samples[na[0]-1]
            end = u_samples[na[-1]+1]
            for i in na:
                print('insert sample: %s' % (prefix + '_' + str(i+1)))
                df[prefix + '_' + str(i+1)] = abund[start] + (abund[start]+abund[end])/(len(na)+1)

    return df


def one_order_difference(df, unit):
    samples = {}
    for u in list(unit.index):
        samples[str(u)] = []

    for s in list(df.keys()):
        samples[s.split('_')[0]].append(int(s.split('_')[1]))

    n = 0
    for k in samples.keys():
        if len(samples[k]) <= 1:
            n += 1
            print('%s个体样本量不足，无法继续进行这轮差分.' % k)
    if n > 0:
        exit()

    '''
    进行差分
    '''
    df_diff = pd.DataFrame(index=df.index)
    for k in samples:
        for i in range(1,len(samples[k])):
            be_diff_sample = k + '_' + str(samples[k][i])
            diff_sample = k + '_' + str(samples[k][i-1])
            df_diff[be_diff_sample] = df[be_diff_sample] - df[diff_sample]

    '''
    差分结束，去除数值都为0的行
    '''
    for i in list(df_diff.index):
        if not all(df_diff.loc[i]):
            df_diff.drop(i)

    return df_diff


def n_order_difference(input, unit, n):
    abund = pd.read_csv(input, sep='\t', header=0, index_col=0)
    unit = pd.read_csv(unit, sep=',', header=0, index_col=0)
    df = insert_data(abund, unit)
    print('将要进行%d阶差分.' % n)
    for i in range(n):
        print('############################################\n正在进行%d阶差分.' % (i+1))
        df = one_order_difference(df, unit)
        print('%d阶差分结束.' % (i+1))
        df.to_csv('%s_%d.order.difference' % (input, (i+1)), sep='\t', header=True, index=True)


if __name__ == '__main__':
    params = read_params()
    input = params['input_file']
    unit = params['unit']
    n = params['n_order']
    n_order_difference(input, unit, n)

