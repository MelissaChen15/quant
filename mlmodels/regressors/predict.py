# __author__ = Chen Meiying
# -*- coding: utf-8 -*-
# 2019/3/20 13:10

import numpy as np
import pandas as pd
import h5py
from sklearn import preprocessing, metrics
from mlmodels.utities import PCA_algorithm
from mlmodels.regressors.Para import Para
para = Para()

def predict(model, model_name):
    # 模型预测
    n_days_in_test = 0  # 记录test set包含的天数
    r2_all_tests = []  # 记录每一天的预测准确度
    mse_all_tests = []  # 记录每一天的roc
    for i_month in para.month_test:  # 按月加载
        file_name = para.path_data + str(i_month) + ".h5"
        f = h5py.File(file_name, 'r')
        # print(file_name)
        for key in f.keys():  # 按天加载，按天预处理数据
            n_days_in_test += 1
            # 加载
            h5 = pd.read_hdf(file_name, key=str(key))
            data_curr_day = pd.DataFrame(h5)
            data_curr_day = data_curr_day.mask(data_curr_day['pct_chg'].abs() >= 10.1)  # 去掉收益率绝对值大于10.1的数据点
            data_curr_day = data_curr_day.mask(data_curr_day['pct_chg'] == 0.0)  # 去掉收益率为0的数据点
            data_curr_day = data_curr_day.dropna(axis=0)  # remove nan
            # 预处理
            X_curr_day = data_curr_day.loc[:, 'close':'amount'] # X的实际值
            y_curr_day = data_curr_day.loc[:, 'pct_chg'] # y的实际值

            scalar = preprocessing.StandardScaler().fit(X_curr_day) # 标准化
            X_curr_day = scalar.transform(X_curr_day)

            X_curr_day = PCA_algorithm.pca(X_curr_day) # pca

            # 预测
            y_score_curr_day = model.predict(X_curr_day)

            # 保存结果到csv文件
            result_curr_day = pd.DataFrame(y_curr_day).rename(columns={'pct_chg': 'return_pred'})
            result_curr_day['return_pred'] = y_score_curr_day
            result_curr_day = result_curr_day.sort_values(by='return_pred', ascending=False)
            store_path = para.path_results + model_name+ "\\"+str(n_days_in_test) + ".csv"
            result_curr_day.to_csv(store_path, sep=',', header=True, index=True)

            # 计算accuracy，roc
            r2_curr_day =  metrics.r2_score(y_curr_day, y_score_curr_day)
            mse_curr_day = metrics.mean_squared_error(y_curr_day, y_score_curr_day)
            r2_all_tests.append(r2_curr_day)
            mse_all_tests.append(mse_curr_day)
            print("day #%d, r2 = %6f, MSE = %6f" %(n_days_in_test,r2_curr_day, mse_curr_day))
    print("average r2 on all test days = %6f" % np.mean(r2_all_tests))
    print("average MSE on all test days = %6f" % np.mean(mse_all_tests))

    return n_days_in_test


def add_next_day_return(model_name):
    n_days_in_test = 0
    for i_month in para.month_test:  # 按月加载
        file_name = para.path_data + str(i_month) + ".h5"
        f = h5py.File(file_name, 'r')
        # print(file_name)
        for key in f.keys():  # 按天加载，按天预处理数据
            n_days_in_test += 1
            if n_days_in_test == 1: continue # 第一天的y不要
            ### key!!
            h5 = pd.read_hdf(file_name, key=str(key))
            data_next_day = pd.DataFrame(h5)
            y_next_day = data_next_day.loc[:, 'pct_chg'] # y的实际值
            # print(y_next_day)
            csv_name = para.path_results + model_name + "\\" + str(n_days_in_test-1)
            print("day/csv",n_days_in_test, csv_name)
            csv = pd.read_csv(csv_name + ".csv")
            csv_curr_day = pd.DataFrame(csv).iloc[:100,:]# 取前100支
            csv_curr_day['return_true'] = np.zeros([100])
            # print(csv_curr_day)
            # map对应的股票
            for i in range(100):
                code = csv_curr_day.iloc[i,0]
                try:
                    csv_curr_day.iloc[i,2] = y_next_day[code]
                except:
                    pass
            # print(csv_curr_day)
            csv_curr_day.to_csv(csv_name + '_r.csv', sep=',', header=True, index=True)
            # print(csv_curr_day)
            print(n_days_in_test)




if __name__ == '__main__':
    from sklearn.externals import joblib
    model = joblib.load( r"D:\Meiying\data\result\GBoostR\GBoostR_model.m") # 模型加载
    # predict(model, "GBoostR")
    add_next_day_return("GBoostR")
    # keys_set = list(f.keys())
