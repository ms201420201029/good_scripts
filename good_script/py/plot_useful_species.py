import pandas as pd
import regex as re
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot as plt


def sample_label(unit, change=False):
    '''
    将输入的表格做成dataframe
    mouths越大越接近死亡
    :param unit:
    :return:
    '''
    mouths = unit.columns.size
    unit = unit.dropna(axis=0, how='all')
    unit = unit.dropna(axis=1, how='all')
    samples = []
    mouth = []
    name = []
    for m in unit.keys():
        for n in unit.index:
            if isinstance(unit[m][n], str):
                samples.append(unit[m][n])
                if change:
                    mouth.append(mouths - int(m) + 1)
                else:
                    mouth.append(int(m))
                name.append(n)
    sample_info = pd.DataFrame({'mouths': mouth, 'name': name}, index=samples)
    return sample_info


def add_feature(sample_info, abund, feature):
    '''
    需要考虑情况：
        1、feature是str的时候：
        2、feature是list的时候：
            （1）、循环feature，
    :param sample_info:
    :param abund:
    :param feature:
    :return:
    '''
    if isinstance(feature, str):
        # 得到给出的feature在丰度表中的名称
        is_in = [species for species in abund.keys() if feature in species][0]
        feature_value = []
        for sample in sample_info.index:
            if sample in abund.index:
                feature_value.append(abund[is_in][sample])
            else:
                feature_value.append(float('nan'))
                print('%s is not in abundance profile, fill nan in it!' % sample)
        sample_info[feature] = feature_value
        return sample_info
    elif isinstance(feature, list):
        for f in feature:
            unexist_sample = []
            is_in = [species for species in abund.keys() if f in species][0]
            f_value = []
            for sample in sample_info.index:
                if sample in abund.index:
                    f_value.append(abund[is_in][sample])
                else:
                    f_value.append(float('nan'))
                    unexist_sample.append(sample)
            sample_info[f] = f_value
        unexist_sample = list(set(unexist_sample))
        for s in unexist_sample:
            for i in range(1, len(s)):
                pipei_s = re.compile(r'(%s){e<=%d}' % (s, i))
                pipei_result = [i for i in abund.index if len(pipei_s.findall(i)) > 0]
                if len(pipei_result) > 0:
                    break
                else:
                    continue
            log = '%s is not in abundance profile, fill nan in it! Find most similar sample name:' % s
            if len(pipei_result) > 0:
                log += ','.join(pipei_result)
            else:
                log += 'none'
            print(log)

        return sample_info


def select_sample(sample_info, n=3):
    '''
    按个体中的样本数量筛选样本，默认删除少于3个的个体
    :param sample_info:
    :param n:
    :return:
    '''
    unit = set(sample_info['name'])
    s_sample = []
    for u in unit:
        if list(sample_info['name']).count(u) >= n:
            s_sample += list(sample_info[sample_info['name'] == u].index)
    return sample_info.loc[s_sample]


def draw_useful(sample_info, useful_species_select):
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
            x_points = [max(y) - i + 1 for i in sample_info[sample_info['name'] == u]['mouths']]
            y_points = sample_info[sample_info['name'] == u][species]
            ax.plot(x_points, y_points, color=color[i])

        ax.set_title('%s' % (useful_species_select[species]), fontproperties=zhfont, fontsize=20)
        ax.set_xlabel('The time before death(mouths)', fontproperties=zhfont, fontsize=15)
        ax.set_ylabel('Percentage(%)', fontproperties=zhfont, fontsize=15)
        ax.legend(labels=unit, loc='best', prop=zhfont)
        ax.set_xticks(range(max(y) - max(y) + 1, max(y) - min(y) + 1 + 1))
        ax.set_xticklabels(xtick_label)
        plt.savefig('有益菌单菌/%s.png' % useful_species_select[species])
        plt.close()


abund = pd.read_csv('otu_table_L7.txt', sep='\t', header=0, index_col=0).T
# print(abund.index)
# print(abund.keys())
death_unit = pd.read_csv('death_unit/death_unit.info', sep=',', header=0, index_col=0)

# 整理成一个dataframe:sample是index;mouth和name作为列名
sample_info = sample_label(death_unit)

# 将特征加入样本的dataframe中
features = list(abund.keys())
sample_info = add_feature(sample_info, abund, features)

# 由于某些sample不存在，因此去除不存在的样本行
sample_info = sample_info.dropna(axis=0, how='any')

# 去除个体样本小于n的个体样本，这里是每个个体不能小于三个样本
sample_info_select = select_sample(sample_info, 3)

# 选择有益单菌，并在丰度表中名字唯一
useful_species_file = 'species.tsv'
useful_species = pd.read_csv(useful_species_file, sep='\t', header=0, index_col=1)
useful_species_select = {}
for i in useful_species.index:
    f = []
    for j in sample_info.keys():
        if i in j:
            f.append(j)
    if len(f) == 1:
        useful_species_select[f[0]] = useful_species['zh_name'].loc[i]
# print(useful_species_select)
draw_useful(sample_info_select, useful_species_select)
