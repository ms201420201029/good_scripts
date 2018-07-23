import pandas as pd
import regex as re
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
import random
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from scipy import stats


def sample_label(unit, change=True):
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


def classify(sample_info, species):
    '''
    判断输入的菌在80%个体中的趋势是不是一致的，如果是一致的，那么就接受该菌
    1、菌的变化曲线是否是可以接受的：假设以各条变化线为斜边构成的三角形面积为A,B,C……，面积最大的三角形X是否大于其他三角形的面积之和的1.5倍，
    若上述条件成立，则以最大三角形斜边斜率作为增大或者减小的判断依据或者以第一个点到最后一个点连线的斜率作为增大或者减少的判断依据
    若上述条件不成立，那么判断最大面积三角形的高是否小于整个图形的15%以下或者初始值与最终值的差是否大于整个图形的30%，
    若是，则判断增大或者减少，若不是，则不接受这条变化线
    2、在接受的变化线中，是否80%个体的变化趋势都是一致的，若是，则返回True；接受的变化线太少或者各个变化趋势不一致，都返回False
    :param sample_info:
    :param species:
    :return:True/False
    '''
    unit = list(set(sample_info['name']))
    line_type = []
    for u in unit:
        u_abund = sample_info.loc[sample_info['name'] == u][['mouths', species]]
        u_abund = u_abund.sort_values('mouths', ascending=True)  # True是增序排列，False是降序排列
        s_values = u_abund[species].values
        m_values = u_abund['mouths'].values

        if len(set(s_values)) == 1 and 0 in set(s_values):
            continue

        area = []
        for i in range(len(s_values)-1):
            area.append(abs(s_values[i+1]-s_values[i])*(m_values[i]-m_values[i+1]))
        marea_index = area.index(max(area))
        if max(area) >= 1.5*(sum(area)-max(area)) \
                or abs(s_values[marea_index+1]-s_values[marea_index])/abs(max(sample_info[species])-min(sample_info[species]))/abs(m_values[marea_index+1]-m_values[marea_index]) <= 0.05 \
                or abs(s_values[0]-s_values[-1])/abs(max(sample_info[species])-min(sample_info[species])) > 0.3:
            if s_values[0] > s_values[-1]:
                line_type.append('reduce')
            elif s_values[0] < s_values[-1]:
                line_type.append('increase')

    has_type = None
    for i in set(line_type):
        if line_type.count(i) >= len(unit) * 0.8:
            # print(species, line_type)
            has_type = i

    return has_type


def draw_features(sample_info, select_name, features_type, features=None):
    '''
    按照各个特征进行绘图，不同的个体不同的线
    :param sample_info: 输入的样本的dataframe
    :param select_name: 前面选择的用来判断菌走势的样本
    :param features_type: 代表菌走势的字典
    :param features: 要绘制图形的菌的list
    :return: None
    '''
    color = ['#00447E', '#F34800', '#64A10E', '#930026', '#464E04', '#049a0b', '#4E0C66', '#D00000', '#FF6C00',
             '#FF00FF', '#c7475b', '#00F5FF', '#BDA500', '#A5CFED', '#f0301c', '#2B8BC3', '#FDA100', '#54adf5',
             '#CDD7E2', '#9295C1']
    unit = list(set(sample_info['name']))
    del_u = []
    for u in unit:
        # print(u, unit.index(u), len(sample_info[sample_info['name'] == u].index))
        if len(sample_info[sample_info['name'] == u].index) <= 1:
            del_u.append(u)
    for u in del_u:
        unit.remove(u)

    # 设置绘图风格
    plt.style.use('fivethirtyeight')
    # 设置绘图legend字体，使其可以绘制中文字体
    zhfont = matplotlib.font_manager.FontProperties(fname='msyhbd.ttc')

    if not features:
        features = list(sample_info.keys())
        for i in ['mouths', 'name', 'mouths_pre']:
            if i in features:
                features.remove(i)

    # 在去世的只有两个样本的个体上验证，保留准确率超过80%的特征
    if not select_name == set(sample_info['name']):
        diff_name = set(unit).difference(select_name)
        del_f = []
        for i in features:
            accept = 0
            name_number = 0
            for name in diff_name:
                name_table = sample_info[sample_info['name'] == name].sort_values('mouths', ascending=False)
                if len(name_table.index) <= 1:
                    print('%s only has one sample or less.'% name)
                else:
                    name_number += 1
                    if name_table[i].iloc[0] > name_table[i].iloc[-1] and features_type[i] == 'reduce':
                        accept += 1
                    elif name_table[i].iloc[0] < name_table[i].iloc[-1] and features_type[i] == 'increase':
                        accept += 1
            # print(i, accept, name_number)
            if accept < 0.5 * name_number:
                del_f.append(i)
        for i in del_f:
            features.remove(i)

    with open(r'species_type.o', 'w') as f:
        f.write('species\ttype\n')
        for i in features:
            f.write('%s\t%s\n' % (i, features_type[i]))

    y = sample_info['mouths']
    xtick = set(y)
    xtick_label = []
    # 统计mouths的集合，将没有样本的月份设为空
    for i in range(1, max(y)+1):
        if i in xtick:
            xtick_label.append(max(y)-i+1)
        elif xtick_label:
            xtick_label.append('')
    # print(sample_info)
    # print(xtick_label)

    for species in features:
        fig, ax = plt.subplots(sharey=True, figsize=(15, 5))
        fig.canvas.set_window_title('%s' % species)

        for i, u in enumerate(unit):
            x_points = [max(y)-i+1 for i in sample_info[sample_info['name'] == u]['mouths']]
            y_points = sample_info[sample_info['name'] == u][species]
            ax.plot(x_points, y_points, color=color[i])

        ax.set_title('%s(%s)' % (species, features_type[species]))
        ax.legend(labels=unit, loc='best', prop=zhfont)
        ax.set_xticks(range(max(y)-max(y)+1, max(y)-min(y)+1+1))
        ax.set_xticklabels(xtick_label)
        plt.savefig('find_singlespecies/%s.png' % species)
        plt.close()


def dataframe_std(df):
    '''
    对特征进行标准化
    :param df:
    :return:
    '''
    df_values = np.array(df)
    df_values_std = StandardScaler().fit_transform(df_values)
    df_std = pd.DataFrame(df_values_std, index=df.index, columns=df.keys())
    return df_std


def dataframe_vt(df, threshold=0):
    '''
    对特征按照方差进行筛选，去除方差小于threshold的特征
    :param df:
    :param threshold:
    :return:
    '''
    vt = VarianceThreshold(threshold=threshold)
    features = list(df.keys())
    for f in df.keys():
        try:
            vt.fit_transform(df[f].values.reshape(df.shape[0], 1))
        except:
            features.remove(f)
    return features


def dataframe_wilcox(df, p_threshold=0.5):
    features = []
    label_class = list(set(df['label']))
    for f in df.keys():
        if stats.ranksums(df.loc[df['label'] == label_class[0]][f], df.loc[df['label'] == label_class[1]][f]).pvalue <= p_threshold:
            features.append(f)
    return features


def get_label(df, max_mouths, min_mouths):
    label = []
    for sample in df.index:
        if df['mouths'].loc[sample] >= max_mouths:
            label.append(1)
        elif df['mouths'].loc[sample] <= min_mouths:
            label.append(0)
        else:
            label.append(float('nan'))
    df['label'] = label
    return df


def label_balance(df):
    label = list(df['label'])
    label_class = set(label)
    label_class_number = {}
    for i in label_class:
        label_class_number[str(i)] = label.count(i)
    less_label = sorted(label_class_number, key=lambda x: label_class_number[x])[0]
    more_label = sorted(label_class_number, key=lambda x: label_class_number[x])[1]
    less_number = label_class_number[more_label] - label_class_number[less_label]
    less_sample = list(df[df['label'] == float(less_label)].index)
    add_sample = []
    random.seed(319)
    for i in range(less_number):
        add_sample.append(random.sample(less_sample, 1)[0])
    df = df.loc[list(df.index) + add_sample]
    return df


def del_repeat_list(l):
    '''
    l是一个list,里面包含的也是list：[['a'],['b']]
    :param l:
    :return: 不重复list
    '''
    l_uniq = []
    l = [sorted(i) for i in l]
    for i in l:
        if i not in l_uniq:
            l_uniq.append(i)

    return l_uniq


def classify(sample_info, species):
    '''
    判断输入的菌在80%个体中的趋势是不是一致的，如果是一致的，那么就接受该菌
    1、# 1、全为正或全为负：符号全相同，接受；不相同，不接受，判断第2条
       # 2、 正/负（取大者）的面积均值是否大于负/正的面积均值的1.5倍：大于，接受；小于，不接受，判断第3条
       # 3、面积最大的三角形月跨度是否小于5%：小于，接受；大于，不接受，判断第4条
       # 4、初始值和最后值的差值是否占据整个图形的30%以上：大于，接受；小于，不接受
    若接受，则判断增大或者减少，若以上四条全部接受，则不接受这条变化线
    2、在接受的变化线中，是否80%个体的变化趋势都是一致的，若是，则返回True；接受的变化线太少或者各个变化趋势不一致，都返回False
    :param sample_info:
    :param species:
    :return:True/False
    '''
    unit = list(set(sample_info['name']))
    line_type = []
    for u in unit:
        u_abund = sample_info.loc[sample_info['name'] == u][['mouths', species]]
        # 这里mouths数值越大越接近死亡
        u_abund = u_abund.sort_values('mouths', ascending=False)  # True是增序排列，False是降序排列
        s_values = u_abund[species].values
        m_values = u_abund['mouths'].values

        if len(set(s_values)) == 1 and 0 in set(s_values):
            continue

        area = []
        for i in range(len(s_values)-1):
            area.append(-(s_values[i+1]-s_values[i])*(m_values[i+1]-m_values[i]))
        area_positive = [abs(i) for i in area]
        marea_index = [abs(i) for i in area].index(max(area_positive))
        # 1、全为正或全为负：符号全相同，接受；不相同，不接受，判断第2条
        # 2、正/负（取大者）的面积均值是否大于负/正的面积均值的1.5倍：大于，接受；小于，不接受，判断第3条
        # 3、面积最大的三角形月跨度是否小于5%：小于，接受；大于，不接受，判断第4条
        # 4、初始值和最后值的差值是否占据整个图形的30%以上：大于，接受；小于，不接受
        if sorted(area)[0] >= 0 or sorted(area)[-1] <= 0:
            if s_values[0] > s_values[-1]:
                line_type.append('reduce')
            elif s_values[0] < s_values[-1]:
                line_type.append('increase')
        else:
            # 小于0的面积的均值，大于0的面积的均值
            large_than_zero = sum([i for i in area if i > 0])/len([i for i in area if i > 0])
            small_than_zero = sum([abs(i) for i in area if i < 0])/len([abs(i) for i in area if i < 0])
            if max(large_than_zero, small_than_zero) >= 1.5*min(large_than_zero, small_than_zero) \
                or abs(s_values[marea_index+1]-s_values[marea_index])/abs(max(sample_info[species])-min(sample_info[species]))/abs(m_values[marea_index+1]-m_values[marea_index]) <= 0.05 \
                or abs(s_values[0]-s_values[-1])/abs(max(sample_info[species])-min(sample_info[species])) > 0.3:
                if s_values[0] > s_values[-1]:
                    line_type.append('reduce')
                elif s_values[0] < s_values[-1]:
                    line_type.append('increase')

    has_type = None
    for i in set(line_type):
        if line_type.count(i) >= len(unit) * 0.8: # 乘以的是多少条线是趋势一致的，1表示100%
            # print(species, line_type)
            has_type = i

    return has_type

