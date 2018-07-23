from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
from sklearn import datasets, tree
from sklearn.externals.six import StringIO
import pydotplus
from matplotlib import pyplot as plt

iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['is_train'] = np.random.uniform(0, 1, len(df)) <= .75
df['species'] = pd.Categorical.from_codes(iris.target, iris.target_names)

df.head()
train, test = df[df['is_train'] == True], df[df['is_train'] == False]
features = df.columns[:4]
clf = RandomForestClassifier(n_jobs=2)
y, _ = pd.factorize(train['species'])
clf = clf.fit(train[features], y)
tree_in_forest = clf.estimators_[0]
dot_data = StringIO()
tree.export_graphviz(tree_in_forest, out_file=dot_data)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
# plt.show()
graph.write_pdf("irisacc.pdf")
