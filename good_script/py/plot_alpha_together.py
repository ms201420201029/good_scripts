# /usr/bin/python3
# -*- coding : utf-8 -*-
# 计算每组的中值，并加入两个时间点的中间值以达到耿直的折线
# __author__ = mas


import argparse
import numpy as np
import pandas as pd
import math
import regex as re
from scipy import stats
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot as plt


def read_params():
    parser = argparse.ArgumentParser(description='read params for group.')
    parser.add_argument('-g', '--group', metavar='group', dest='group_file', required=True, type=str,
                        help='input group file.')
    parser.add_argument('-u', '--unit', metavar='unit', dest='unit_file', required=True, type=str,
                        help='input unit file.')
    parser.add_argument('-a', '--alpha', metavar='alpha', dest='alpha_file', required=True, type=str,
                        help='input alpha file.')
    args = parser.parse_args()
    params = vars(args)
    return params


def find_pos(df):
    '''
    去除df前后全为nan的列，中间全为nan的列则保留
    '''
    df_describe = df.describe()

    for i in range(df.shape[1]):
        if df.describe().loc['count'].iloc[-i-1] > 0:
            end = -i
            break

    if end == 0:
        df = df
    else:
        df = df[df.keys()[0:end]]
    return df


def get_points(df):
    '''
    获取每个时间点的坐标，并取两个中间时间点的坐标点，确保能构成耿直的折线
    '''
    df_mean = []
    for key in df.keys():
        not_nan = [i for i in df[key] if not math.isnan(i)]
        if not_nan:
            df_mean.append(sum(not_nan) / len(not_nan))
        else:
            df_mean.append(float('nan'))

    x_points = []
    y_points = []
    front = 0
    front_value = False
    for i, mean in enumerate(df_mean):
        if i == 0 and not math.isnan(df_mean[i]):
            x_points.append(i + 1)
            y_points.append(df_mean[i])
            front = i
            front_value = True
        elif i > 0:
            if not math.isnan(df_mean[i]):
                if front_value:
                    x_points.append((i + 1 + front + 1) / 2)
                    y_points.append(df_mean[front])
                    x_points.append((i + 1 + front + 1) / 2)
                    y_points.append(df_mean[i])
                    x_points.append(i + 1)
                    y_points.append(df_mean[i])
                    front = i

                else:
                    x_points.append(i + 1)
                    y_points.append(df_mean[i])
                    front = i

    return x_points, y_points, df_mean


if __name__ == '__main__':
    params = read_params()
    group = params['group_file']
    unit = params['unit_file']
    alpha = params['alpha_file']

    group = pd.read_csv(group, sep='\t', header=None, index_col=0)
    unit = pd.read_csv(unit, sep=',', header=0, index_col=0)
    alpha = pd.read_csv(alpha, sep='\t', header=0, index_col=0)

    groups = list(set(group[1]))
    groups_mean = []
    colors = ['#00447E', '#F34800', '#64A10E', '#930026', '#464E04', '#049a0b', '#4E0C66', '#D00000', '#FF6C00',
            '#FF00FF', '#c7475b', '#00F5FF', '#BDA500', '#A5CFED', '#f0301c', '#2B8BC3', '#FDA100', '#54adf5',
            '#CDD7E2', '#9295C1']

    # 设置绘图风格
    plt.style.use('fivethirtyeight')
    # 设置绘图legend字体，使其可以绘制中文字体
    zhfont = matplotlib.font_manager.FontProperties(fname='msyhbd.ttc')

    fig, ax = plt.subplots(sharey=True, figsize=(15, 8))
    fig.canvas.set_window_title('PD1_species_number')

    for i, g in enumerate(groups):
        gu = list(set([s.split('_')[0] for s in group[group[1] == g].index]))
        units = [u for u in unit.index if u.split('_')[0] in gu]

        df = pd.DataFrame(index=units, columns=unit.keys())
        for u in units:
            u_alpha = []
            for s in unit.loc[u]:
                if isinstance(s, str):
                    u_alpha.append(np.float64(alpha.loc[s]))
                else:
                    u_alpha.append(np.float64('nan'))
            df.loc[u] = u_alpha

        df = find_pos(df)

        x_points_df, y_points_df, df_mean = get_points(df)
        # 去除nan值
        df_mean = [i for i in df_mean if not math.isnan(i)]
        groups_mean.append(df_mean)

        ax.plot(x_points_df, y_points_df, color=colors[i])

    if len(groups_mean) == 2:
        p = stats.ranksums(groups_mean[0], groups_mean[1]).pvalue
        p_x_position = ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) / 15
        p_y_position = ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.9
        ax.text(x=p_x_position, y=p_y_position, s='pvalue : %4f' % p, color='white', fontproperties=zhfont, bbox=dict(boxstyle="round"))

    ax.set_title('PD1 species number\n', fontproperties=zhfont, fontsize=20)
    ax.set_xlabel('\nThe time get sample', fontproperties=zhfont, fontsize=15)
    ax.set_ylabel('mean species number', fontproperties=zhfont, fontsize=15)
    ax.legend(labels=groups, loc='best', prop=zhfont)

    plt.xticks(rotation=15)
    ax.set_xticks(range(1, len(unit.keys()) + 1))
    ax.set_xticklabels(list(unit.keys()))
    plt.savefig('PD1_mean_species_number.png')
    plt.close()

