import pandas as pd
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.tree import export_graphviz
from sklearn.externals import joblib
import os
from random import random
from sklearn import metrics
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import argparse


def read_params():
    parser = argparse.ArgumentParser(description='''get reference guttype | v1.0 at 2017/9/19 by mas ''')
    parser.add_argument('-i', '--input', dest='input_file', metavar='file(txt)', type=str,
                        help='input abundance file')
    parser.add_argument('-n', '--n_tree', dest='tree_number', metavar='number(int)', type=int,
                        help='create tree number', default=1000)
    parser.add_argument('-s', '--search_number', dest='search_number', metavar='number(int)', type=int,
                        help='circle number in order to find best random state', default=1000)
    parser.add_argument('-g', '--group_file', dest='group_file', metavar='file(txt)', type=str,
                        help='group file')
    parser.add_argument('-a', '--acc_file', dest='avg_Acc_file', metavar='file(txt)', type=str,
                        help='output random state avg Acc file', default='state_avg_acc.tsv')
    parser.add_argument('-p', '--picture_name', dest='picture_name', metavar='file(txt)', type=str,
                        help='output picture file name', default='tree.png')
    parser.add_argument('-r', '--roc_fig', dest='roc_fig', metavar='file(txt)', type=str,
                        help='output roc fig file name', default='roc.png')
    parser.add_argument('-w', '--feature_weight_fig', dest='feature_weight_fig', metavar='file(txt)', type=str,
                        help='output feature weight fig file name', default='feature_weight.png')
    parser.add_argument('-v', '--p_value', dest='p_value', metavar='file(txt)', type=str,
                        help='input p value file, threshold is 0.05', default=None)

    args = parser.parse_args()
    param = vars(args)
    return param


def transform(profile, group):
    '''
    将profile转化成行为样本，列为特征
    :param profile: 丰度表
    :param group: 分组表
    :return: profile, group
    '''
    need_t = any([True for i in group.index if i in profile.keys()])
    if need_t:
        profile = profile.T

    sample_profile = set(profile.index)
    sample_group = set(group.index)
    sample_inter = list(sample_profile.intersection(sample_group))

    profile = profile.loc[sample_inter]
    group = group.loc[sample_inter]
    return profile, group


def select_feature_by_p(profile, p_value):
    '''
    如果有输入的p值的文件，那就按照p值为0.05筛选特征
    :param profile: 丰度表
    :param p_value: p值表
    :return: 筛选后的丰度表
    '''
    if p_value:
        p_value = pd.read_csv(p_value, sep='\t', header=0, index_col=0)
        try:
            p_value = p_value['pvalue']
        except:
            p_value = p_value.iloc[:, 0]
        features = p_value[p_value < 0.05].index
        profile = profile[features]
    return profile


def random_forest(profile, group, n_tree, search_number, avg_acc):
    '''
    对丰度表进行建模
    :param profile:丰度表
    :param group: 分组表
    :param n_tree: 模型中树的颗数
    :param search_number: 搜索随机种子的次数
    :param avg_acc: 随机种子准确率的输出文件
    :return: 加label后的group
    '''
    real_label = set(group.iloc[:, 0])
    label_dict = {}
    for i, j in enumerate(real_label):
        label_dict[j] = i
    label = []
    for sample in group.index:
        label.append(label_dict[group.loc[sample].values[0]])

    group['label'] = label

    # n = 0
    # with open(avg_acc, 'w') as f:
    #     f.write('random_state\tavgAcc\n')
    #     while n < search_number:
    #         print('现在循环次数为{0}'.format(n+1))
    #         # random random_state
    #         random_state = round(random() * 10000)
    #
    #         rf = RandomForestClassifier(n_estimators=n_tree, max_leaf_nodes=6,
    #                                     random_state=818)
    #
    #         sample_train = list(profile.index)
    #         sample_val = list(profile.index)
    #         train = profile.loc[sample_train]
    #         val = profile.loc[sample_val]
    #         label_train = group['label'].loc[sample_train]
    #
    #         rf.fit(train, label_train)
    #         pre = rf.predict(val)
    #
    #         acc = metrics.accuracy_score(y_true=group['label'][sample_val], y_pred=pre)
    #         print(acc)
    #
    #         # print('{0}\t{1}\n'.format(random_state, sum(acc) / 10))
    #         f.write('{0}\t{1}\n'.format(random_state, acc))
    #         n += 1
    return group


def plot_tree(profile, group, avg_acc, n_tree, picutre):
    '''
    选择最优的随机种子并建模
    :param profile: 丰度表
    :param group: 分组表
    :param avg_acc: 随机种子准确率的输出文件
    :param n_tree: 模型中树的颗数
    :param picutre: 输出图形的名称
    :return: None
    '''
    acc = pd.read_csv(avg_acc, sep='\t', header=0, index_col=0)
    best_state = int(acc.sort_values('avgAcc').index[-1])

    # 训练和保存预测模型
    rf = RandomForestClassifier(n_estimators=n_tree, max_leaf_nodes=6,
                                random_state=818)
    rf.fit(profile, group['label'])
    joblib.dump(rf, 'rf.pkl')

    # 绘制分类树结果图形
    dot = picutre.split('.')[0] + '.dot'
    tree_in_forest = rf.estimators_[rf.n_estimators-1]
    export_graphviz(tree_in_forest,
                    out_file=dot,
                    feature_names=profile.columns,
                    filled=True,
                    rounded=False,
                    precision=100)

    os.system('dot -Tpng {0} -o {1}'.format(dot, picutre))


def plot_roc(profile, group, roc_fig):
    rf = joblib.load('rf.pkl')
    print(rf.random_state)
    y_pred = rf.predict(profile)
    y_true = group['label']
    # print(list(y_true))
    # print(y_pred)

    fig, ax = plt.subplots()
    fpr_lr, tpr_lr, _ = roc_curve(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, y_pred, average='macro', sample_weight=None)
    print(roc_auc)
    ax.plot(fpr_lr, tpr_lr, label='auc=%s' % round(roc_auc, 2))
    ax.plot([0, 1], [0, 1], 'k--')
    ax.set_xlabel('fpr')
    ax.set_ylabel('tpr')
    ax.set_title('RandomForest ROC')
    ax.legend(loc='best')
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 1.1)
    ax.grid(True)
    plt.savefig(roc_fig)


def plot_feature_weight(profile, feature_weight_fig):
    rf = joblib.load('rf.pkl')
    feature_weight = pd.DataFrame(rf.feature_importances_, index=profile.keys())
    feature_weight = feature_weight.sort_values(0, ascending=False)
    feature_weight = feature_weight[feature_weight > 0]
    feature_weight = feature_weight.dropna(axis=0, how='all')
    feature_weight = feature_weight.sort_values(0, ascending=True)

    if len(feature_weight.index) > 10:
        feature_weight = feature_weight.iloc[:10]

    fig, axes = plt.subplots(figsize=(8, 5))  # 设置图片大小

    max_length = max([len(species) for species in feature_weight.index])
    fig.subplots_adjust(left=max_length*0.0085, right=0.95)  # 调整y轴在图片中的位置，y若y轴名称较长，则可以调整y轴偏右边一些
    fig.canvas.set_window_title('random forest features weight')  # 设置整个图片句柄的名称

    pos = np.arange(len(feature_weight))  # 取名称的长度来为纵坐标取刻度数

    rects = axes.barh(pos, feature_weight.values,  # y轴的刻度个数以及各个值
                      align='center',
                      height=0.5, color='lightblue')  # bar的宽度，填充颜色
    axes.set_yticks(pos)
    axes.set_yticklabels(feature_weight.index, fontsize=8)

    axes.set_title('random forest features weight', fontsize=10)  # 图形名称

    axes.set_xlim([max(float(min(feature_weight.values))-0.05, 0), float(max(feature_weight.values))*1.1])  # 设置x轴的大小
    axes.xaxis.set_major_locator(MaxNLocator(5))  # 设置x轴刻度个数
    axes.xaxis.grid(True, linestyle='--', which='major',
                    color='grey', alpha=.25)  # 设置网格虚线格式，颜色，粗细

    cohort_label = axes.text(.5, -.1, 'weight',
                             horizontalalignment='center', fontsize=10,
                             transform=axes.transAxes)  # 设置x轴的标注

    plt.savefig(feature_weight_fig)


def main_select(abund_file, n_tree, search_number, group, avg_acc, picutre, roc_fig, feature_weight_fig, p_value):
    '''
    主函数
    :param abund_file:
    :param n_tree:
    :param search_number:
    :param group:
    :param avg_acc:
    :param picutre:
    :param p_value:
    :return:None
    '''
    profile = pd.read_csv(abund_file, sep='\t', header=0, index_col=0)
    group = pd.read_csv(group, sep='\t', header=None, index_col=0)
    # 判断profile是否需要转置，并取出group和profile共有的样本
    print('变换丰度表')
    profile, group = transform(profile, group)

    # 根据检验的p值来选取特征
    print('根据p值选择feature')
    profile = select_feature_by_p(profile, p_value)

    # 用随机森林进行预测
    print('选择random state')
    group = random_forest(profile, group, n_tree, search_number, avg_acc)

    # 读取随机各个随机种子的准确率文件，选取最优的随机种子并绘制分类树
    print('绘图')
    plot_tree(profile, group, avg_acc, n_tree, picutre)

    # 绘制对原数据集预测的roc曲线
    plot_roc(profile, group, roc_fig)

    # 绘制特征重要性图
    plot_feature_weight(profile, feature_weight_fig)


if __name__ == '__main__':
    params = read_params()
    abund_file = params['input_file']
    n_tree = params['tree_number']
    search_number = params['search_number']
    group = params['group_file']
    avg_acc = params['avg_Acc_file']
    picutre = params['picture_name']
    p_value = params['p_value']
    roc_fig = params['roc_fig']
    feature_weight_fig = params['feature_weight_fig']
    main_select(abund_file, n_tree, search_number, group, avg_acc, picutre, roc_fig, feature_weight_fig, p_value)
