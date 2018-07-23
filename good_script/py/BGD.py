import numpy as np
from random import sample


print('test network!')
print('BGD!')
a = 3
b = 4
rate = 0.11
max_error = 0.0001
n = 10000
print('初始化！y=%dx+%d,学习数率为：%f,最大误差不超过：%f,最大迭代次数：%d' % (a, b, rate, max_error, n))

x = np.array([[1], [2], [3]])
y = np.array([[1], [2], [3]])

i = 0
while i <= n:
    i += 1
    for s in range(len(x)):
        diff = (a * x[s][0] + b) - y[s]
        a = a - rate*diff*x[s]

        diff = (a * x[s] + b) - y[s]
        b = b - rate*diff

    error = 0
    for p, q in zip(x, y):
        # print([a,b])
        # print([q[0] , ( a*p[0] + b )])
        error += abs(q[0] - (a*p[0] + b))
        # print(error)
    # print('经过第%d次拟合后函数变为：y = %fx + %f, 错误大小：%f' % (i, a, b, error))
    if abs(error) <= 3*max_error:
        print('end')
        # print(type(error))
        print('拟合%d次后，最终拟合函数为：y = %fx + %f' % (i, a, b))
        break


###################################################################################
print('SGD!')
a = 3
b = 4
rate = 0.11
max_error = 0.0001
n = 10000
print('初始化！y=%dx+%d,学习数率为：%f,最大误差不超过：%f,最大迭代次数：%d' % (a, b, rate, max_error, n))

x = np.array([[1], [2], [3]])
y = np.array([[1], [2], [3]])

i = 0
while i <= n:
    i += 1
    s = sample([0, 1, 2], 1)

    diff = (a * x[s][0] + b) - y[s]
    a = a - rate*diff*x[s]

    diff = (a * x[s] + b) - y[s]
    b = b - rate*diff

    error = 0
    for p, q in zip(x, y):
        error += abs(q[0] - (a*p[0] + b))
    # print('经过第%d次拟合后函数变为：y = %fx + %f, 错误大小：%f' % (i, a, b, error))
    if abs(error) <= 3*max_error:
        print('end')
        print('拟合%d次后，最终拟合函数为：y = %fx + %f' % (i, a, b))
        break

###################################################################################
print('MSGD!')
a = 3
b = 4
rate = 0.11
max_error = 0.0001
n = 10000
print('初始化！y=%dx+%d,学习数率为：%f,最大误差不超过：%f,最大迭代次数：%d' % (a, b, rate, max_error, n))

x = np.array([[1], [2], [3]])
y = np.array([[1], [2], [3]])

i = 0
while i <= n:
    i += 1
    sss = sample([0, 1, 2], 2)

    for s in sss:
        diff = (a*x[s][0] + b) - y[s]
        a = a - rate*diff*x[s]

        diff = (a*x[s] + b) - y[s]
        b = b - rate*diff

    error = 0
    for p, q in zip(x, y):
        # print([a,b])
        # print([q[0] , ( a*p[0] + b )])
        error += abs(q[0] - (a*p[0] + b))
        # print(error)
    # print('经过第%d次拟合后函数变为：y = %fx + %f, 错误大小：%f' % (i, a, b, error))
    if abs(error) <= 3*max_error:
        print('end')
        # print(type(error))
        print('拟合%d次后，最终拟合函数为：y = %fx + %f' % (i, a, b))
        break
