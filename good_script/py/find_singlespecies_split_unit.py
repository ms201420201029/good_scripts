import pandas as pd
import regex as re
import math
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


def draw_features_together(sample_info, select_name, features_type, features=None):
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
            if accept < 0.5 * name_number:  # 接受的百分比
                del_f.append(i)
        for i in del_f:
            features.remove(i)

    y = sample_info['mouths']
    xtick = set(y)
    xtick_label = []
    # 统计mouths的集合，将没有样本的月份设为空
    for i in range(1, max(y)+1):
        if i in xtick:
            xtick_label.append(max(y)-i+1)
        elif xtick_label:
            xtick_label.append('')

    for species in features:
        fig, ax = plt.subplots(sharey=True, figsize=(15, 8))  
        fig.canvas.set_window_title('%s' % species)

        for i, u in enumerate(unit):
            x_points = [max(y)-i+1 for i in sample_info[sample_info['name'] == u]['mouths']]
            y_points = sample_info[sample_info['name'] == u][species]
            ax.plot(x_points, y_points, color=color[i])

        ax.set_xlabel('The time before death(mouths)', fontproperties=zhfont, fontsize=15)
        ax.set_ylabel('Percentage(%)', fontproperties=zhfont, fontsize=15)
        ax.legend(labels=unit, loc='best', prop=zhfont)
        ax.set_xticks(range(max(y)-max(y)+1, max(y)-min(y)+1+1))
        ax.set_xticklabels(xtick_label)

        if species in features_type.keys():
            ax.set_title('%s(%s)' % (species, features_type[species]), fontproperties=zhfont, fontsize=20)
            plt.savefig('find_singlespecies/select/together/%s_all.png' % species)
        else:
            ax.set_title('%s' % (species), fontproperties=zhfont, fontsize=20)
            plt.savefig('find_singlespecies/normal/together/%s_all.png' % species)
        plt.close()


def optimize_size(x):
    a = math.sqrt(x)
    if a % 1 == 0:
        return (int(a), int(a))
    else:
        min_value = math.floor(a)
        if min_value * (min_value + 1) >= x:
            return (min_value, min_value + 1)
        else:
            return (min_value, min_value + 2)


def draw_features_each(sample_info, select_name, features_type, features=None):
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

#    # 在去世的只有两个样本的个体上验证，保留准确率超过80%的特征
#    if not select_name == set(sample_info['name']):
#        diff_name = set(unit).difference(select_name)
#        del_f = []
#        for i in features:
#            if i in features_type.keys():
#                accept = 0
#                name_number = 0
#                for name in diff_name:
#                    name_table = sample_info[sample_info['name'] == name].sort_values('mouths', ascending=False)
#                    if len(name_table.index) <= 1:
#                        print('%s only has one sample or less.'% name)
#                    else:
#                        name_number += 1
#                        if name_table[i].iloc[0] > name_table[i].iloc[-1] and features_type[i] == 'reduce':
#                            accept += 1
#                        elif name_table[i].iloc[0] < name_table[i].iloc[-1] and features_type[i] == 'increase':
#                            accept += 1
#                # print(i, accept, name_number)
#                if accept < 0.5 * name_number:  # 接受的百分比
#                    del_f.append(i)
#            else:
#                del_f.append(i)
#        for i in del_f:
#            features.remove(i)

    y = sample_info['mouths']
    xtick = set(y)
    xtick_label = []
    # 统计mouths的集合，将没有样本的月份设为空
    for i in range(1, max(y)+1):
        if i in xtick:
            xtick_label.append(max(y)-i+1)
        elif xtick_label:
            xtick_label.append('')

    size = optimize_size(len(unit))
    for species in features:
        fig, ax = plt.subplots(nrows=size[0], ncols=size[1], sharex=False, figsize=(size[1]*5, size[0]*4))
        fig.canvas.set_window_title('%s' % species)

        for i, u in enumerate(unit):
            x_points = [max(y)-i+1 for i in sample_info[sample_info['name'] == u]['mouths']]
            y_points = sample_info[sample_info['name'] == u][species]
            ax[int(i/size[1]), i%size[1]].plot(x_points, y_points, color=color[i])
            if species in features_type.keys():
                if y_points[-1] - y_points[0] >= 0 and features_type[species] == 'reduce':
                    ax[int(i/size[1]), i%size[1]].set_title(u + '(special)', fontproperties=zhfont, fontsize=15)
                elif y_points[-1] - y_points[0] <= 0 and features_type[species] == 'increase':
                    ax[int(i/size[1]), i%size[1]].set_title(u + '(special)', fontproperties=zhfont, fontsize=15)
                else:
                    ax[int(i/size[1]), i%size[1]].set_title(u, fontproperties=zhfont, fontsize=15)
            else:
                ax[int(i/size[1]), i%size[1]].set_title(u, fontproperties=zhfont, fontsize=15)
            ax[int(i/size[1]), i%size[1]].set_xlabel('The time before death(mouths)', fontproperties=zhfont, fontsize=10)
            ax[int(i/size[1]), i%size[1]].set_ylabel('Percentage(%)', fontproperties=zhfont, fontsize=10)
            ax[int(i/size[1]), i%size[1]].set_xticks(range(max(y)-max(y)+1, max(y)-min(y)+1+1))
            ax[int(i/size[1]), i%size[1]].set_xticklabels(xtick_label)

        for i in range(size[0]*size[1]-len(unit)):
            ax[size[0]-1,-i-1].set_axis_off()

        fig.set_tight_layout(True)
        plt.subplots_adjust(top=0.91)
        if species in features_type.keys():
            fig.suptitle('%s(%s)' % (species, features_type[species]), fontproperties=zhfont, fontsize=25)
            plt.savefig('find_singlespecies/select/each/%s_each.png' % species)
            plt.close()
        else:
            plt.savefig('find_singlespecies/normal/each/%s_each.png' % species)
            fig.suptitle('%s' % (species), fontproperties=zhfont, fontsize=25)
            plt.close()


abund = pd.read_csv('otu_table_L7.txt', sep='\t', header=0, index_col=0).T
# print(abund.index)
# print(abund.keys())
death_unit = pd.read_csv('death_unit.info', sep=',', header=0, index_col=0)

# 整理成一个dataframe:sample是index;mouth和name作为列名
sample_info = sample_label(death_unit)

# 将特征加入样本的dataframe中
features = list(abund.keys())
sample_info = add_feature(sample_info, abund, features)

# 由于某些sample不存在，因此去除不存在的样本行
sample_info = sample_info.dropna(axis=0, how='any')

# 去除个体样本小于n的个体样本，这里是每个个体不能小于三个样本
sample_info_select = select_sample(sample_info, 3)

select_features = []
features_type = {}
for species in features:
    type = classify(sample_info_select, species)
    if type:
        select_features.append(species)
        features_type[species] = type

# draw_features_together(sample_info_select, set(sample_info['name']), features_type)
draw_features_each(sample_info, set(sample_info_select['name']), features_type)
# if select_features:
#     draw_features_together(sample_info_select, set(sample_info['name']), features_type, select_features)
#     # draw_features(sample_info_select, set(sample_info_select['name']), features_type, select_features)
# 
#     draw_features_each(sample_info, set(sample_info['name']), features_type, select_features)
# else:
#     print('nothing to draw!!!')

