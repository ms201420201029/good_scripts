import pandas as pd
import regex as re
import math
import numpy as np
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def plot_anosim(anosim):
    # 设置绘图风格
    plt.style.use('ggplot')
    zhfont = matplotlib.font_manager.FontProperties(fname='msyhbd.ttc')

    fig, ax = plt.subplots(figsize=(4, 4.5))
    fig.canvas.set_window_title('anosim result')
    
    x_name = re.compile(r'\d+')
    
    x_points = [int(x_name.findall(i)[0]) for i in anosim.index]
    y_points = anosim[anosim.keys()[0]]

    # 绘制点
    ax.scatter(x_points, y_points, marker='*')

    # 绘制拟合的2次多项式
    z = np.polyfit(x_points, y_points, 3)  # 用3次多项式拟合
    # polynomial = np.poly1d(z)
    # y_match = polynomial(x_points)  #也可以使用y_match = np.polyval(z ,x_points)
    y_match = np.polyval(z ,x_points)
    ax.plot(x_points, y_match)

    ax.set_xlabel('The name of grouping scheme', fontproperties=zhfont, fontsize=8)
    ax.set_ylabel('R value', fontproperties=zhfont, fontsize=8)
    ax.set_xticks(range(x_points[0], x_points[-1]+1))
    xtick_label = []
    for x in range(x_points[0], x_points[-1]+1):
        if x in x_points:
            xtick_label.append(anosim[anosim.keys()[2]].loc['cut%d' % x])
        else:
            xtick_label.append('')
    plt.xticks(rotation=20)
    ax.set_xticklabels(xtick_label, fontsize=6)
    plt.yticks(fontsize=6)
    ax.set_title('anosim result of different groups', fontproperties=zhfont, fontsize=10)
    fig.subplots_adjust(left=0.15, bottom=0.15)
    plt.savefig('anosim_result.png')
    plt.close()

anosim = pd.read_csv('anosim.result', sep='\t', index_col=0, header=None)
plot_anosim(anosim)

