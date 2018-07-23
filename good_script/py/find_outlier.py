import pandas as pd
import regex as re
import math
import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import kstest
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot as plt


def find_outlier_quantile(df, quantile=0.95):
    '''
    根据分位数来判断是否是离群点
    '''
    outlier = {}
    for sp in df.keys():
        up = df[sp].quantile(0.95)
        
        outlier[sp] = list(df[df[sp] > up].index)

    return outlier


def find_outlier_boxplot(df, fold=1.5):
    '''
    根据box图来判断是否为离群点
    Q1为25%分位数，Q3为75%分位数
    IQR=Q3-Q1
    上界=Q3+1.5IQR
    下界=Q1-1.5IQR
    超出上下界则为离群点
    '''
    outlier = {}
    for sp in df.keys():
        Q1, Q3 = df[sp].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        up = Q3 + fold * IQR
        bottom = Q1 - fold * IQR
        
        has_outlier = list(df[df[sp] > up].index) + list(df[df[sp] < bottom].index)
        if has_outlier:
            outlier[sp] = has_outlier

    return outlier


def find_outlier_nonnormal(df, fold=1/3):
    '''
    对于非正太分布样本，若（Xn-Xn-1）/（Xn-X1）> 1/3，则视Xn为离群值，式中，Xn为最大值，Xn-1为次最大值，X1为最小值
    '''
    outlier = {}
    for sp in df.keys():
        values = sorted(list(df[sp]))
        if values[-1] == 0 or values[-2] == 0:
            # print(sp)
            continue
        while True:
            xn = values[-1]
            xn_1 = values[-2]
            diff = values[-1] - values[0]
            if diff == 0:
                # print('in', sp, xn)
                break
            if (xn - xn_1) / diff > fold:
                values = values[:-1]
            else:
                break
        threshold = max(values)
        has_outlier = list(df[df[sp] > threshold].index)
        if has_outlier:
            outlier[sp] = has_outlier
    return outlier
   

def find_outlier_distance(df, dis='euclidean'):
    '''
    根据欧式距离求离群点：不考虑特征间的相关性
    根据马氏距离求离群点：要求样品数大于维数，考虑特征间相关性
    '''
    if dis == 'euclidean':
        euclidean_dis = pdist(df, 'euclidean')
        df_dis = pd.DataFrame(index=df.index[:-1], columns=df.index[1:])
        n = 0
        for i in range(df_dis.shape[0]):
            for j in range(i, df_dis.shape[1]):
                df_dis.iloc[i, j] = euclidean_dis[n]
                n += 1

        samples_dis = {}
        for sample in df.index:
            if sample in df_dis.index and sample in df_dis.keys():
                samples_dis[sample] = [i for i in list(df_dis[sample]) + list(df_dis.loc[sample]) if not math.isnan(i)]        

        samples_dis_mean = {}
        for sample in samples_dis.keys():
            samples_dis_mean[sample] = np.array(samples_dis[sample]).mean()

        # fig, ax = plt.subplots()

        # ax.hist(list(samples_dis_mean.values()), 100)
        # plt.savefig('dis_mean.png')
        # plt.close()
        # 检验是否为正态分布
        # ks_p = kstest(list(samples_dis_mean.values()), 'norm').pvalue
        # print(ks_p)
        
        sigma = np.std(list(samples_dis_mean.values()))
        avg = np.array(list(samples_dis_mean.values())).mean()

        min_threshold = avg - 1 * sigma
        max_threshold = avg + 1 * sigma
        print(avg, sigma, min_threshold, max_threshold)
        outlier_samples = []
        for sample in samples_dis_mean.keys():
            if samples_dis_mean[sample] > max_threshold or samples_dis_mean[sample] < min_threshold:
                outlier_samples.append(sample)
        return outlier_samples


    elif dis == 'mahalanobis':
        if len(df.keys()) < len(df.index):
            print('数据框的列数（特征）大于行数（样本量），马氏距离不适用。')
            raise ValueError
        else:
            mahalanobis_dis = pdist(df, 'mahalanobis')
            df_dis = pd.DataFrame(index=df.index[:-1], columns=df.index[1:])
            n = 0
            for i in range(df_dis.shape[0]):
                for j in range(i, df_dis.shape[1]):
                    df_dis.iloc[i, j] = mahalanobis_dis[n]
                    n += 1
    
            samples_dis = {}
            for sample in df.index:
                if sample in df_dis.index and sample in df_dis.keys():
                    samples_dis[sample] = [i for i in list(df_dis[sample]) + list(df_dis.loc[sample]) if not math.isnan(i)]
    
            samples_dis_mean = {}
            for sample in samples_dis.keys():
                samples_dis_mean[sample] = np.array(samples_dis[sample]).mean()
    
            sigma = np.std(list(samples_dis_mean.values()))
            avg = np.array(list(samples_dis_mean.values())).mean()
    
            min_threshold = avg - 3 * sigma
            max_threshold = avg + 3 * sigma
            outlier_samples = []
            for sample in samples_dis_mean.keys():
                if samples_dis_mean[sample] > max_threshold or samples_dis_mean[sample] < min_threshold:
                    outlier_samples.append(sample)
            return outlier_samples

    else:
        print('param dis should be one of euclidean or mahalanobis ')
        raise ValueError


def find_outlier_variance(df, variance=3):
    '''
    假设数据是正态分布，根据3方差来判断是否是离群点
    '''
    
    return


def statistic_outlier(data, samples):
    '''
    统计每个样本离群点的个数
    统计每个个体平均离群点的个数（因为一个个体会存在多个样本，各个个体样本量不一致）
    data是一个每个菌包含离群样本的dict：如：{'species1':['sample1', 'sample2'], 'species2':['sample2', 'sample3']}
    samples是一个要统计离群情况的样本的list
    '''
    sample_outlier = {}
    for sp in data.keys():
        for sample in data[sp]:
            if sample in sample_outlier.keys():
                sample_outlier[sample] += 1
            else:
                sample_outlier[sample] = 1


    units_nsample = {}
    units = [sample.split('-')[0] for sample in samples]
    for i in set(units):
        units_nsample[i] = units.count(i)
    unit_outlier = {}
    for sp in data.keys():
        for sample in data[sp]:
            if sample in samples:
                unit = sample.split('-')[0]
                if unit in unit_outlier.keys():
                    unit_outlier[unit] += 1
                else:
                    unit_outlier[unit] = 1

    for unit in unit_outlier.keys():
        unit_outlier[unit] = unit_outlier[unit] / units_nsample[unit]

    return sample_outlier, unit_outlier


abund = pd.read_csv('otu_table_L7.txt', sep='\t', header=0, index_col=0).T

death = pd.read_csv('death_unit/death_unit.info', sep=',', header=0, index_col=0)
death_samples = []
for i in death:
    death_samples += [s for s in death[i] if isinstance(s, str)]

alive = pd.read_csv('alive_unit/alive_unit.info', sep=',', header=0, index_col=0)
alive_samples = []
for i in alive:
    alive_samples += [s for s in alive[i] if isinstance(s, str)]

# 各种方法得到的离群样本
outlier_quantile = find_outlier_quantile(abund, quantile=0.95)
outlier_boxplot = find_outlier_boxplot(abund, fold=3)
outlier_nonnormal = find_outlier_nonnormal(abund)

# 根据离群样本得到样本中离群数值的格式及各个个体离群次数
quantile_sample_outlier, quantile_unit_outlier = statistic_outlier(outlier_quantile, death_samples + alive_samples)
boxplot_sample_outlier, boxplot_unit_outlier = statistic_outlier(outlier_boxplot, death_samples + alive_samples)
nonnormal_sample_outlier, nonnormal_unit_outlier = statistic_outlier(outlier_nonnormal, death_samples + alive_samples)

print('由95%分位数结果可以得到')
print('\t样本离群结果')
quantile_sample_outlier_sorted = sorted(quantile_sample_outlier.items(), key=lambda x:x[1], reverse=True)
for i in quantile_sample_outlier_sorted:
    print('\t%s 样本的离群个数为： %d' % (i[0], i[1]))

print('\n')
print('\t个体离群结果')
quantile_unit_outlier_sort = sorted(quantile_unit_outlier.items(), key=lambda x:x[1], reverse=True)
for i in quantile_unit_outlier_sort:
    print('\t%s号个体 的平均离群个数为： %.2f' % (i[0], i[1]))

print('\n****************\n')
print('由箱形图的上下界比较结果可以得到')
print('\t样本离群结果')
boxplot_sample_outlier_sorted = sorted(boxplot_sample_outlier.items(), key=lambda x:x[1], reverse=True)
for i in boxplot_sample_outlier_sorted:
    print('\t%s 样本的离群个数为： %d' % (i[0], i[1]))

print('\n')
print('\t个体离群结果')
boxplot_unit_outlier_sorted = sorted(boxplot_unit_outlier.items(), key=lambda x:x[1], reverse=True)
for i in boxplot_unit_outlier_sorted:
    print('\t%s号个体 的平均离群个数为： %.2f' % (i[0], i[1]))

print('\n****************\n')
print('由非正态分布离群判断标准可以得到')
print('\t样本离群结果')
nonnormal_sample_outlier_sorted = sorted(nonnormal_sample_outlier.items(), key=lambda x:x[1], reverse=True)
for i in nonnormal_sample_outlier_sorted:
    print('\t%s 样本的离群个数为： %d' % (i[0], i[1]))

print('\n')
print('\t个体离群结果')
nonnormal_unit_outlier_sorted = sorted(nonnormal_unit_outlier.items(), key=lambda x:x[1], reverse=True)
for i in nonnormal_unit_outlier_sorted:
    print('\t%s号个体 的平均离群个数为： %.2f' % (i[0], i[1]))


print('\n****************\n')
outlier_euclidean_dis = find_outlier_distance(abund,  dis='euclidean')
print('由各个样本间的欧式距离可以得到')
print('\t离群的样本为\n\t%s' % '\n\t'.join(outlier_euclidean_dis))







