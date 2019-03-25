# __author__ = Chen Meiying
# -*- coding: utf-8 -*-
# 2019/3/20 16:37


from sklearn import linear_model, tree
from sklearn.model_selection import StratifiedShuffleSplit,GridSearchCV, ShuffleSplit
import os
from mlmodels.classifiers.Para import Para
para = Para()

def init():
    # Decision Tree 参数
    #['class_weight', 'criterion', 'max_depth', 'max_features', 'max_leaf_nodes', 'min_impurity_decrease', 'min_impurity_split', 'min_samples_leaf', 'min_samples_split',
    # 'min_weight_fraction_leaf', 'presort', 'random_state', 'splitter']
    # 初始化模型
    model = tree.DecisionTreeClassifier(criterion="gini", min_samples_leaf=150, random_state=para.seed)
    # 建立新的文件夹用于存储模型和预测结果
    if os.path.exists(para.path_results + "DTC") == False:
        os.mkdir(para.path_results + "DTC")

    return model, "DTC"