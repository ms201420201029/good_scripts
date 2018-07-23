# /usr/bin/python3
# -*- coding:utf-8 -*-
# description : 硬币找零问题，现有某些币值的money，且无限量，请找出能够组成某个数目的找零所使用最少的硬币数。
# __author__ = mas


def coin_change(p, n):
    '''
    params p : 硬币的币值表
    params n : 需要兑换的money的值
    '''
    plan = [[]]
    counts = [0]

    for k in range(1, n+1):
        c = float('Inf')
        for i in range(1, k+1):
            if i in p:
                best = [i] + plan[k-i]
                c = 1 + counts[k-i]
            elif k-i > 0:
                if c > counts[i] + counts[k-i]:
                    best = plan[i] + plan[k-i]
                    c = counts[i] + counts[k-i]
        plan.append(best)
        counts.append(c)

    return plan, counts


if __name__ == '__main__':
    p = [1, 3, 5]
    n = 20
    plan, counts = coin_change(p, n)
    for i, c, pl in zip(range(n+1), counts, plan):
        print('{0} money need {1} coins, the best plan is {2}'.format(i, c, pl))

