# /usr/bin/python3
# -*- coding:utf-8 -*-
# description : 动态规划解决钢条的最优切割长度问题，有一根N长度的钢条，当切割成多少段价值是最大的（不同小段加个不同）
# __author__ = mas


def forward_select(p, n):
    '''
    params p : 钢条的价格表
    params n : 钢条的总长度
    采用记忆动态规划方法，得到最优的切割方案
    能保证当计算k长度时，所有的子段的最优价格已经算好了
    下面这个脚本，当两种切割情况价格一样时，只保留其中一种
    '''
    plan = [[]]
    price = [0 for i in range(n+1)]

    for k in range(1, n+1):
        q = float('-Inf')
        for i in range(1, k+1):
            # print(k, i, k-i, p[i] + price[k-i])
            try:
                if q < p[i] + price[k-i]:
                    q = p[i] + price[k-i]
                    best = sorted(plan[k-i] + [i], reverse=True)

            except Exception as e:
                # print(k, i, k-i)
                if q < price[i] + price[k-i]:
                    q = price[i] + price[k-i]
                    best = plan[k-i] + plan[i]

                elif q == price[i] + price[k-i]:
                    if isinstance(best[0], int):
                        best = [best, plan[k-i] + plan[i]]
                    else:
                        best.append(plan[k-i] + plan[i])
        price[k] = q
        plan.append(best)
    return price, plan


if __name__ == '__main__':
    p = [0, 1, 5, 8, 9, 10, 17, 17, 20, 24, 30]
    n = 10
    price, plan = forward_select(p, n)
    print(p)
    for i, r, sub_price in zip(range(n+1), price, plan):
        print('{0} length best price is {1}, cut plan is {2}'.format(i, r, sub_price))

#################### some bak ######################
# # /usr/bin/python3
# # -*- coding:utf-8 -*-
# # description : 动态规划解决钢条的最优切割长度问题，有一根N长度的钢条，当切割成多少段价值是最大的（不同小段加个不同）
# # __author__ = mas
# 
# 
# def forward_select(p, n):
#     '''
#     params p : 钢条的价格表
#     params n : 钢条的总长度
#     采用记忆动态规划方法，得到最优的切割方案
#     能保证当计算k长度时，所有的子段的最优价格已经算好了
#     '''
#     plan = [[]]
#     price = [0 for i in range(n+1)]
# 
#     for k in range(1, n+1):
#         q = float('-Inf')
#         for i in range(1, k+1):
#             # print(k, i, k-i, p[i] + price[k-i])
#             try:
#                 if q < p[i] + price[k-i]:
#                     q = p[i] + price[k-i]
#                     if any(plan[k-i]):
#                         if isinstance(plan[k-i][0], int):
#                             best = sorted(plan[k-i] + [i], reverse=True)
#                         else:
#                             best = [sorted(pl + [i], reverse=True) for pl in plan[k-i]]
#                     else:
#                         best = sorted(plan[k-i] + [i], reverse=True)
# 
#                 elif q == p[i] + price[k-i] and sorted(plan[k-i] + [i], reverse=True) not in best and sorted(plan[k-i] + [i], reverse=True) != best:
#                     if isinstance(best[0], int):
#                         best = [best, plan[k-i] + [i]]
#                     else:
#                         best.append(plan[k-i] + [i])
# 
#             except Exception as e:
#                 # print(k, i, k-i)
#                 if q < price[i] + price[k-i]:
#                     q = price[i] + price[k-i]
#                     best = plan[k-i] + plan[i]
# 
#                 elif q == price[i] + price[k-i]:
#                     if isinstance(best[0], int):
#                         best = [best, plan[k-i] + plan[i]]
#                     else:
#                         best.append(plan[k-i] + plan[i])
#         price[k] = q
#         plan.append(best)
#     return price, plan
# 
# 
# if __name__ == '__main__':
#     p = [0, 1, 5, 8, 9, 10, 17, 17, 20, 24, 30]
#     n = 10
#     price, plan = forward_select(p, n)
#     print(p)
#     for i, r, sub_price in zip(range(n+1), price, plan):
#         print('{0} length best price is {1}, cut plan is {2}'.format(i, r, sub_price))
# 
