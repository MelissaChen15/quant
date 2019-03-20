# __author__ = Chen Meiying
# -*- coding: utf-8 -*-
# 2019/3/20 10:57

from sklearn import svm
from sklearn.model_selection import StratifiedShuffleSplit,GridSearchCV,train_test_split
import os
from mlmodels.classificators.Para import Para
para = Para()

def init():
    # SVC 参数
    # ['C', 'cache_size', 'class_weight', 'coef0', 'decision_function_shape', 'degree', 'gamma', 'kernel', 'max_iter',
    #  'probability', 'random_state', 'shrinking', 'tol', 'verbose']
    param_grid = {'C': [1],
                  'gamma':[1]
                  }
    cv_split = StratifiedShuffleSplit(n_splits=5, train_size=0.9, test_size=0.1)

    #初始化模型
    model = GridSearchCV(estimator=svm.SVC(), param_grid=param_grid, cv=cv_split, n_jobs=1,scoring='accuracy')
    # 建立新的文件夹用于存储模型和预测结果
    os.mkdir(para.path_results + "SVC")

    return model, "SVC"
