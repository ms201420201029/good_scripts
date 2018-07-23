import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

import numpy as np

fig, ax = plt.subplots(figsize=[5, 4])
y = x = range(-20,20)
ax.plot(x,y)
# extent = [-3, 4, -4, 3]

# 在ax右上角（loc设置）中插入放大两倍的矩形框
axins = zoomed_inset_axes(ax, 2, loc=1)  # zoom = 6
axins.plot(x,y)

# sub region of the original image
# 放大原始图像的哪一块
x1, x2, y1, y2 = 1, 2, 1, 2
axins.set_xlim(x1, x2)
axins.set_ylim(y1, y2)
# fix the number of ticks on the inset axes
# 设置插入图片x，y轴的坐标轴数值个数
axins.yaxis.get_major_locator().set_params(nbins=2)
axins.xaxis.get_major_locator().set_params(nbins=2)

# 设置x，y轴是否有坐标
plt.xticks(visible=False)
plt.yticks(visible=True)

# draw a bbox of the region of the inset axes in the parent axes and
# connecting lines between the bbox and the inset axes area
# mark放大的区域是哪块
mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

plt.draw()
plt.savefig('b.png')
