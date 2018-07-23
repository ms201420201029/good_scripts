import deal_data
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np
import random
import matplotlib
from matplotlib import pyplot as plt
import argparse


def read_params():
    parser = argparse.ArgumentParser(description='read params for find some species.')
    parser.add_argument('-i', '--input', metavar='input', dest='input_file', required=True, type=str,
                        help='input abund file. first row is sample name, sample name should in unit file.')
    parser.add_argument('-n', '--fea_number', metavar='fea_number', dest='fea_number', required=True, type=int,
                        help='input want select feature number. 2 or more, suggest less than or equal to five.')
    parser.add_argument('-o', '--output_dir', metavar='output_dir', dest='output_dir', required=True, type=str,
                        help='output dirname.')
    args = parser.parse_args()
    params = vars(args)
    return params


def draw_useful(sample_info, useful_species_select, output_dir):
    '''
    绘制有益菌单菌的图形
    :param sample_info_select:
    :param useful_species_select: 菌中文翻译的字典
    :return:
    '''
    color = ['#00447E', '#F34800', '#64A10E', '#930026', '#464E04', '#049a0b', '#4E0C66', '#D00000', '#FF6C00',
             '#FF00FF', '#c7475b', '#00F5FF', '#BDA500', '#A5CFED', '#f0301c', '#2B8BC3', '#FDA100', '#54adf5',
             '#CDD7E2', '#9295C1']
    unit = list(set(sample_info['name']))

    # 设置绘图风格
    plt.style.use('fivethirtyeight')
    # 设置绘图legend字体，使其可以绘制中文字体
    zhfont = matplotlib.font_manager.FontProperties(fname='msyhbd.ttc')

    y = sample_info['mouths']
    xtick = set(y)
    xtick_label = []
    # 统计mouths的集合，将没有样本的月份设为空
    for i in range(1, max(y) + 1):
        if i in xtick:
            xtick_label.append(max(y) - i + 1)
        elif xtick_label:
            xtick_label.append('')
    # print(sample_info)
    # print(xtick_label)

    for species in useful_species_select.keys():
        fig, ax = plt.subplots(sharey=True, figsize=(15, 8))
        fig.canvas.set_window_title('%s' % species)

        for i, u in enumerate(unit):
            print(sample_info[sample_info['name'] == u][['species_hat', 'mouths']])
            x_points = [max(y) - i + 1 for i in sample_info[sample_info['name'] == u]['mouths']]
            y_points = sample_info[sample_info['name'] == u][species]
            print(x_points, y_points)
            ax.plot(x_points, y_points, color=color[i])

        ax.set_title('%s' % (useful_species_select[species]), fontproperties=zhfont, fontsize=20)
        ax.set_xlabel('The time before death(mouths)', fontproperties=zhfont, fontsize=15)
        ax.set_ylabel('Percentage(%)', fontproperties=zhfont, fontsize=15)
        ax.legend(labels=unit, loc='best', prop=zhfont)
        ax.set_xticks(range(max(y) - max(y) + 1, max(y) - min(y) + 1 + 1))
        ax.set_xticklabels(xtick_label)
        plt.savefig('%s/%d_%s.png' % (output_dir, len(useful_species_select[species].split(',')), useful_species_select[species]))
        plt.close()


def sgd_and_draw(df, fea_selected, death_unit, death_sample, output_dir, reverse=False):
    # 梯度下降 每次随机挑选一个样本对模型采用梯度下降
    print('SGD!')
    a = [5 for i in fea_selected]
    b = 5
    rate = 0.001
    max_error = 1
    n = 20000
    print('初始化！y,学习数率为：%f,最大误差不超过：%f,最大迭代次数：%d' % (rate, max_error, n))

    x = np.array(df[fea_selected])
    if reverse:
        y = list(reversed(df[['mouths']]))
    else:
        y = np.array(df[['mouths']])
    # print(x)
    # print(y)

    i = 0
    min_error = float('inf')
    random.seed(319)
    while i <= n:
        i += 1
        s = random.sample(range(x.shape[0]), 1)

        for index in range(len(a)):
            diff = (sum([i * j for i, j in zip(a, x[s][0])]) + b) - y[s][0][0]
            a[index] = a[index] - rate * diff

        diff = (sum([i * j for i, j in zip(a, x[s][0])]) + b) - y[s][0][0]
        b = b - rate * diff

        error = 0
        for p, q in zip(x, y):
            error += abs(q[0] - (sum([i * j for i, j in zip(a, p)]) + b))
        # print('经过第%d次拟合后函数变为：y, 错误大小：%f' % (i, error))

        if min_error > error:
            min_error = error
            min_error_a = [round(i, 2)for i in a]
            min_error_b = round(b, 2)
        if abs(error) <= x.shape[0] * max_error:
            print('end')
            print('运行过程中的最小错误：%f' % error)
            # print('拟合%d次后，最终拟合函数为：y = %fx + %f' % (i, min_error_a, min_error_b))
            break

    print('运行过程中的最小错误：%f' % min_error)
    print(','.join(fea_selected))
    reg_hanshu = ['%s * %s' % (i, j) for i, j in zip(min_error_a, fea_selected)]
    reg_hanshu = ' + '.join(reg_hanshu) + ' + %s' % min_error_b
    print(reg_hanshu)

    # fea_selected_array = [i * np.array(sample_info_death[j]) for i, j in zip(a, fea_selected[0])]
    df['species_hat'] = sum([i * np.array(df[j]) for i, j in zip(min_error_a, fea_selected)]) + min_error_b
    # print([i * np.array(j) for i, j in zip(a, sample_info_death[fea_selected[0]])])


    # 整理成一个dataframe:sample是index;mouth和name作为列名
    sample_name = deal_data.sample_label(death_unit, change=False)
    df['name'] = sample_name['name']


    species_type = deal_data.classify(df.loc[death_sample], 'species_hat')
    if species_type:
        if reverse:
            draw_useful(df.loc[death_sample], {'species_hat': 'reversed_' + ','.join(fea_selected) + '(%s)' % species_type}, output_dir)
        else:
            draw_useful(df.loc[death_sample], {'species_hat': 'noreversed_' + ','.join(fea_selected) + '(%s)' % species_type}, output_dir)
    else:
        # 是否绘制我们认为不重要的特征
        # draw_useful(df.loc[death_sample], {'species_hat': 'delete_' + ','.join(fea_selected)}, output_dir)  # 绘制
        pass
    # if species_type == 'reduce':
    #     draw_useful(df.loc[death_sample], {'species_hat': ','.join(fea_selected) + '(reduce)'}, output_dir)
    # elif species_type == 'increase':
    #     draw_useful(df.loc[death_sample], {'species_hat': ','.join(fea_selected) + '(increase)'}, output_dir)
    # else:
    #     draw_useful(df.loc[death_sample], {'species_hat': 'delete_' + ','.join(fea_selected)}, output_dir)


if __name__ == '__main__':
    params = read_params()
    input_file = params["input_file"]
    fea_number = params["fea_number"]
    output_dir = params["output_dir"]

    abund = pd.read_csv(input_file, sep='\t', header=0, index_col=0).T
    # print(abund.index)
    # print(abund.keys())
    death_unit = pd.read_csv('death_unit/death_unit.info', sep=',', header=0, index_col=0)

    # 整理成一个dataframe:sample是index;mouth和name作为列名
    sample_info_death = deal_data.sample_label(death_unit, change=False)

    # 将特征加入样本的dataframe中
    features = list(abund.keys())
    sample_info_death = deal_data.add_feature(sample_info_death, abund, features)

    # 由于某些sample不存在，因此去除不存在的样本行
    sample_info_death = sample_info_death.dropna(axis=0, how='any')
    death_sample = deal_data.select_sample(sample_info_death, n=3).index  # 为了后面bagging样本，达到平衡后取出最原始的样本

    # 对特征进行标准化
    sample_info_death_std = deal_data.dataframe_std(sample_info_death[features])
    # print(sample_info_std)

    # 去除方差为0的特征，但还是保留之前的丰度值不变
    select_vt_features = deal_data.dataframe_vt(sample_info_death_std, threshold=0)
    sample_info_death = sample_info_death[select_vt_features + ['mouths']]


    # 选择时间的最大最小值，计算label
    # 原先最大值为10，最小值为4；但经过mouths转化，最小值为8，最大值为14
    max_mouths = 7
    min_mouths = 6
    # print(sample_info.keys())
    sample_info_death = deal_data.get_label(sample_info_death, max_mouths=max_mouths, min_mouths=min_mouths)

    # 由于某些label不存在，因此去除label不存在的样本行
    sample_info_death = sample_info_death.dropna(axis=0, how='any')
    # print(sample_info_death['label'])

    # 去除秩和检验p值小于0.5的特征
    # deal_data.dataframe_wilcox(sample_info_death, p_threshold=0.5)
    select_p_features = deal_data.dataframe_wilcox(sample_info_death, p_threshold=0.5)
    sample_info_death = sample_info_death[select_p_features]

    # 由于label之间不平衡，因此对label少的那类样本随机采样，使两类数据平衡
    sample_info_death = deal_data.label_balance(sample_info_death)
    # print(sample_info_death['label'])

    ######################################
    # 读取验证集数据
    alive_unit = pd.read_csv('alive_unit/alive_unit.info', sep=',', header=0, index_col=0)

    # 整理成一个dataframe:sample是index;mouth和name作为列名
    sample_info_alive = deal_data.sample_label(alive_unit, change=False)

    # 将特征加入样本的dataframe中
    features = list(abund.keys())
    sample_info_alive = deal_data.add_feature(sample_info_alive, abund, features)

    # 由于某些sample不存在，因此去除不存在的样本行
    sample_info_alive = sample_info_alive.dropna(axis=0, how='any')
    # print(sample_info_alive)

    #######################################

    # 选取1个特征，逐渐递增，最多五个特征
    all_features = set(select_p_features).difference(['mouths', 'label'])
    lda = LinearDiscriminantAnalysis()
    for n in range(1, fea_number + 1):  # 选择特征的个数：后面数字减去前面数字
        auc = {}
        if n == 1:
            for i in all_features:  # all_features
                lda.fit(np.array(sample_info_death[i]).reshape(-1, 1), sample_info_death['label'])
                val = np.array(sample_info_alive[sample_info_alive['mouths'] >= max_mouths - 4][i]).reshape(-1, 1)
                label_pre = lda.predict(val)
                auc[i] = list(label_pre).count(1) / val.shape[0]
                auc_max = max(auc.values())
                # 这里最好加上秩和检验
                fea_selected = [k for k in auc if auc[k] == auc_max]
        else:
            if len(fea_selected) > 1:
                # fea_selected中有多种情况的时候
                for i in fea_selected:
                    if isinstance(i, str):
                        # fea_selected内每个元素只有1个特征的时候
                        others = all_features.copy()
                        others.remove(i)
                        for j in others:  # others
                            lda.fit(np.array(sample_info_death[[i, j]]), sample_info_death['label'])
                            val = np.array(sample_info_alive[sample_info_alive['mouths'] >= max_mouths - 4][[i, j]])
                            label_pre = lda.predict(val)
                            auc[','.join([i, j])] = list(label_pre).count(1) / val.shape[0]
                    else:
                        # fea_selected内每个元素有多个特征的时候
                        others = all_features.copy()
                        for f in i:
                            others.remove(f)
                        for j in others:  # others
                            lda.fit(np.array(sample_info_death[i + [j]]), sample_info_death['label'])
                            val = np.array(sample_info_alive[sample_info_alive['mouths'] >= max_mouths - 4][i + [j]])
                            label_pre = lda.predict(val)
                            auc[','.join(i + [j])] = list(label_pre).count(1) / val.shape[0]
                auc_max = max(auc.values())
                fea_selected = [k.split(',') for k in auc if auc[k] == auc_max]

            else:
                # fea_selected中只有一种情况的时候
                if isinstance(fea_selected[0], str):
                    # fea_selected内每个元素只有1个特征的时候
                    others = all_features.copy()
                    others.remove(fea_selected[0])
                    for j in others:  # others
                        lda.fit(np.array(sample_info_death[[fea_selected[0], j]]), sample_info_death['label'])
                        val = np.array(sample_info_alive[sample_info_alive['mouths'] >= max_mouths - 4][[fea_selected[0], j]])
                        label_pre = lda.predict(val)
                        auc[','.join([fea_selected[0], j])] = list(label_pre).count(1) / val.shape[0]
                else:
                    # fea_selected内每个元素有多个特征的时候
                    others = all_features.copy()
                    for f in fea_selected[0]:
                        others.remove(f)
                    for j in others:  # others
                        lda.fit(np.array(sample_info_death[fea_selected[0] + [j]]), sample_info_death['label'])
                        val = np.array(sample_info_alive[sample_info_alive['mouths'] >= max_mouths - 4][fea_selected[0] + [j]])
                        label_pre = lda.predict(val)
                        auc[','.join(fea_selected[0] + [j])] = list(label_pre).count(1) / val.shape[0]
                auc_max = max(auc.values())
                fea_selected = [k.split(',') for k in auc if auc[k] == auc_max]

    # print(fea_selected)

    ####################################
    fea_selected = deal_data.del_repeat_list(fea_selected)
    print('------共选取了%d种情况------' % len(fea_selected))
    for fea in fea_selected:
        sgd_and_draw(sample_info_death, fea, death_unit, death_sample, output_dir)
        sgd_and_draw(sample_info_death, fea, death_unit, death_sample, output_dir, reverse=True)

    # ###################################
    # # 梯度下降 每次随机挑选一个样本对模型采用梯度下降
    # print('SGD!')
    # a = [3 for i in fea_selected[0]]
    # b = 5
    # rate = 0.001
    # max_error = 1
    # n = 10000
    # print('初始化！y,学习数率为：%f,最大误差不超过：%f,最大迭代次数：%d' % (rate, max_error, n))
    #
    # x = np.array(sample_info_death[fea_selected[0]])
    # y = np.array(sample_info_death[['mouths']])
    # # print(x)
    # # print(y)
    #
    # i = 0
    # min_error = float('inf')
    # while i <= n:
    #     i += 1
    #     s = random.sample(range(x.shape[0]), 1)
    #
    #     for index in range(len(a)):
    #         diff = (sum([i * j for i, j in zip(a, x[s][0])]) + b) - y[s][0][0]
    #         a[index] = a[index] - rate*diff
    #
    #     diff = (sum([i * j for i, j in zip(a, x[s][0])]) + b) - y[s][0][0]
    #     b = b - rate*diff
    #
    #     error = 0
    #     for p, q in zip(x, y):
    #         error += abs(q[0] - (sum([i * j for i, j in zip(a, p)]) + b))
    #     print('经过第%d次拟合后函数变为：y, 错误大小：%f' % (i, error))
    #
    #     if min_error > error:
    #         min_error = error
    #     if abs(error) <= x.shape[0]*max_error:
    #         print('end')
    #         print('运行过程中的最小错误：%f' % error)
    #         # print('拟合%d次后，最终拟合函数为：y = %fx + %f' % (i, a, b))
    #         break
    #
    # print('运行过程中的最小错误：%f' % min_error)
    # print(fea_selected)
    # print(a, b)
    #
    # # fea_selected_array = [i * np.array(sample_info_death[j]) for i, j in zip(a, fea_selected[0])]
    # sample_info_death['species_hat'] = sum([i * np.array(sample_info_death[j]) for i, j in zip(a, fea_selected[0])]) + b
    # # print([i * np.array(j) for i, j in zip(a, sample_info_death[fea_selected[0]])])
    #
    #
    # # 整理成一个dataframe:sample是index;mouth和name作为列名
    # sample_name = deal_data.sample_label(death_unit, change=False)
    # sample_info_death['name'] = sample_name['name']
    #
    # draw_useful(sample_info_death.loc[death_sample], {'species_hat': 'ok'})
