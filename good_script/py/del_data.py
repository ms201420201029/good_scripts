# /usr/bin/env python3
# -*- encoding -*-

__author__ = "mas"

import os
import sys
import pandas as pd


def data_statistic(input_file, interval=100):
    '''
    删除2006年以前的数据，根据2006年以后的黄金数据，统计数据个数的天数，如：100个数据：2天，200个数据：4天
    :param input_file: 黄金数据输入文件
    :param interval: 时间间隔,一分钟为100
    :return: 统计的dict
    '''
    output_dir = os.path.dirname(input_file)
    output_statistic = os.path.basename(input_file).split('.')[0] + '_%dminute.statistic' % (interval/100)
    output_data = os.path.basename(input_file).split('.')[0] + '.day'
    print(output_statistic)
    print(output_data)

    with open(input_file, 'r') as g:
        fields = g.readline()
        d = g.readline()
        data = {}
        while d:
            '''
            有些数据读入就直接是list格式
            '''
            try:
                d = d.split(',')
            except:
                d = d

            day = d[1]
            if int(day) <= 20060000:
                # print(day)
                d = g.readline()
                continue
            else:
                # print(day)
                minute = int(d[2])
                if day in data.keys() and minute % interval == 0:
                    data[day] += 1
                elif day not in data.keys():
                    data[day] = 1
                d = g.readline()

        data_set = {}
        for i in set(data.values()):
            data_set[str(i)] = list(data.values()).count(i)

        day_keys = sorted([int(i) for i in data])
        with open(r'%s/%s' % (output_dir, output_data), 'w') as f:
            f.write('这是美元黄金每天数据个数的统计文件：\n')
            for i in day_keys:
                f.write('\t%d 的数据个数为：%d\n' % (i, data[str(i)]))

        data_keys = sorted([int(i) for i in data_set.keys()], reverse=True)
        with open(r'%s/%s' % (output_dir, output_statistic), 'w') as f:
            f.write('这是%s的结果统计文件\n' % '美元黄金')
            for i in data_keys:
                f.write('\t%d个数据的天数为：%d\n' % (i, data_set[str(i)]))

        return data_set


def pick_days(input_file, pick_number=1200):
    '''
    选择那些数据超过制定个数的天
    :param input_file: data_statistic函数输出的.day文件
    :param pick_number: 挑选的最低个数
    :return: None
    '''
    output_dir = os.path.dirname(input_file)
    output_pick = os.path.basename(input_file) + '.pick'
    with open(input_file, 'r') as f, open(r'%s/%s' % (output_dir, output_pick), 'w') as o:
        o.write('这是一天中美元黄金数大于%d个的统计文件：\n' % pick_number)
        f.readline()
        data = f.readline()
        while data:
            day = int(data.strip().split(' ')[0])
            number = int(data.strip().split('：')[1])
            if number >= pick_number:
                o.write('\t%d 的数据个数为：%d\n' % (day, number))
            data = f.readline()


def fill_data(data_file, day_file, outdir):
    '''
    数据存在，则输出到输出文件中，若不存在，则按照两数据阶梯上升填充空值
    :param data_file: 数据文件
    :param day_file: pick_days的输出文件
    :param outfile: 数据输出文件
    :return:
    '''
    days = []
    with open(day_file, 'r') as day:
        # 描述文件的行
        day.readline()
        line = day.readline()
        while line:
            days.append(int(line.strip().split(' ')[0]))
            line = day.readline()

    # 将一个list拆分成多个连续的时间的list组成的list
    n = 0
    l = []
    days_trans = []
    for i in days:
        if i - n == 1:
            l.append(i)
            n = i
        else:
            if l:
                days_trans.append(l)
            l = [i]
            n = i
    if l:
        days_trans.append(l)

    # 读进原始数据并对空值进行填补
    with open(data_file, 'r') as d:
        # 字段行
        fields = d.readline().strip()
        if isinstance(fields, str):
            fields = fields.split(',')
        # print(fields)

        print('总共将输出%d个文件' % len(days_trans))
        for i_days in days_trans:
            # i_days = sorted(i_days)
            outfile = outdir + '/' + os.path.basename(data_file).split('.')[0] + \
                      '_%s.csv' % ('-'.join([str(i) for i in sorted(list(set([i_days[0], i_days[-1]])))]))
            print(outfile)
            data_keys = []
            for i in i_days:
                data_keys += ['%d_%s%s' % (i, str(t).zfill(2), str(m).zfill(4)) for t in range(0, 24) for m in range(0, 6000, 100)]

            data_i = pd.DataFrame(columns=data_keys, index=fields)
            n = 0
            while True:
                data = d.readline().strip()
                # print(data)
                if data == '':
                    break
                if isinstance(data, str):
                    data = data.split(',')
                # print(int(data[1]), data_i)
                if int(data[1]) in i_days:
                    n = 1
                    data_i[data[1] + '_' + data[2]] = data
                else:
                    if n == 0:
                        continue
                    else:
                        # 还未填充nan值，需要填充完nan值后输出
                        data_i.T.to_csv(outfile, sep=',', header=True, index=False)
                        break


def del_main(input, output):
    '''
    删除2006年以前的数据；在黄金每分钟数据文件中，如果一天数据缺少三个数据以上，就删除一天的数据
    :param input:输入文件
    :param output:输出文件
    :return:None
    '''
    pass
