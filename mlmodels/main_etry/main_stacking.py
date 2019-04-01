# __author__ = Chen Meiying
# -*- coding: utf-8 -*-
# 2019/4/1 13:36
import numpy as np
import os
import pandas as pd
from sklearn import metrics,preprocessing
from sklearn.model_selection import train_test_split
import h5py
from mlmodels.main_etry import PCA_algorithm
from mlmodels.main_etry import load_sample_data,train, predict, build_strategy,evaluate_strategy
from mlmodels.main_etry.Para import Para
para = Para()
from mlmodels.regressors import Ridge_init, RFR_init, SVR_init,Lasso_init

def average_stack_predict(models): # 写成这样子是因为数据的格式
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
            y_curr_day = data_curr_day.loc[:, 'pct_chg'] * 0.01 # y的实际值

            scalar = preprocessing.StandardScaler().fit(X_curr_day) # 标准化
            X_curr_day = scalar.transform(X_curr_day)

            X_curr_day = PCA_algorithm.pca(X_curr_day) # pca

            # 预测
            y_score_curr_day = models[0].predict(X_curr_day)
            for model in models:
                y_score_a_model = model.predict(X_curr_day)
                y_score_curr_day += y_score_a_model
            y_score_curr_day /= len(models)

            # 保存结果到csv文件
            result_curr_day = pd.DataFrame(y_curr_day).rename(columns={'pct_chg': 'return_pred'}) # 复制y_curr_day是为了获取股票代码
            result_curr_day['return_pred'] = y_score_curr_day # 用预测值覆盖掉前面复制的y_curr_day值
            result_curr_day = result_curr_day.sort_values(by='return_pred', ascending=False)
            result_curr_day.loc["predict data from:"] = [key]
            # print(result_curr_day)
            if os.path.exists(para.path_results + "ave_stack") == False:
                os.mkdir(para.path_results + "ave_stack")
            store_path = para.path_results + "ave_stack\\"+str(n_days_in_test) + ".csv"
            result_curr_day.to_csv(store_path, sep=',', header=True, index=True)

            # 计算accuracy，roc
            r2_curr_day =  metrics.r2_score(y_curr_day, y_score_curr_day)
            mse_curr_day = metrics.mean_squared_error(y_curr_day, y_score_curr_day)
            r2_all_tests.append(r2_curr_day)
            mse_all_tests.append(mse_curr_day)
            print("day #%d, r2 = %6f, MSE = %6f" %(n_days_in_test,r2_curr_day, mse_curr_day))
    print("average r2 on all test days = %6f" % np.mean(r2_all_tests))
    print("average MSE on all test days = %6f" % np.mean(mse_all_tests))

    return n_days_in_test # #


if __name__ == '__main__':

    # 1. 加载train/cv set数据
    X_in_sample, y_in_sample = load_sample_data.load2_regress()
    X_train, X_cv, y_train, y_cv, *args = load_sample_data.preprocess(X_in_sample, y_in_sample)
    print("X_train shape, y_train shape:", X_train.shape, y_train.shape)
    print("X_cv shape, y_cv shape:", X_cv.shape,y_cv.shape)

    ## ---------- 训练基模型 ------------
    # # 2. 初始化模型
    # inits = [Ridge_init.init(), RFR_init.init()]
    #
    # # 3. 训练模型,保存模型
    # models = []
    # for init in inits:
    #     model_name = init[1]
    #     models.append(train.train_regress(clone(init[0]), model_name, X_train, X_cv, y_train, y_cv))
    #
    # # ---------- Averaging stacking ------------
    # # 4. 模型预测,保存预测结果
    # # from sklearn.externals import joblib
    # # models = []
    # # models.append(joblib.load(r"D:\Meiying\data\result\RFR\RFR_model.m"))
    # # models.append(joblib.load(r"D:\Meiying\data\result\Ridge\Ridge_model.m"))
    # n_days_in_test = average_stack_predict(models)


    # ---------- Meta-model Stacking --------------
    # 4. 将第一层的预测值作为第二层的输入
    from sklearn.externals import joblib
    models_1st_layer = []
    models_1st_layer.append(joblib.load(r"D:\Meiying\data\result\RFR\RFR_model.m"))  # 加载第一层的模型
    models_1st_layer.append(joblib.load(r"D:\Meiying\data\result\Ridge\Ridge_model.m"))
    X_all_meta = pd.DataFrame(y_in_sample.index)# 复制y的代码
    y_all_meta = y_in_sample
    t = 0 # 单纯用来计数，添加列
    for model in models_1st_layer:
        X_all_meta[t]= (model.predict(X_in_sample))
        t += 1
    X_all_meta = X_all_meta.iloc[:,1:]
    X_train_meta, X_cv_meta, y_train_meta, y_cv_meta = train_test_split(X_all_meta, y_all_meta, test_size=para.percent_cv,
                                                    random_state=para.seed)
    y_train_meta, y_cv_meta  =  y_train_meta.values.ravel(), y_cv_meta.values.ravel() # 转换为sklearn部分模型需要的格式
    # 5. 训练第二层模型
    model_2nd_layer, *arg= Lasso_init.init()
    model_name = 'meta_stack'
    model = train.train_regress(model_2nd_layer, model_name, X_train_meta, X_cv_meta, y_train_meta, y_cv_meta)

    # 6. 第二层模型预测,保存预测结果
    n_days_in_test = predict.predict_regress(model, model_name) ### 预测也要改，也得是两层

    # ------------ staking结束 ------------


    # 7. 策略构建
    build_strategy.add_next_day_return(model_name)
    strategy = build_strategy.build(n_days_in_test, model_name)

    # 8. 策略评价
    evaluate_strategy.evaluate(strategy, n_days_in_test)


    # 其他
    # print(svm.SVC().get_params().keys()) # 查看模型需要的参数
    # model = joblib.load( para.path_results  + "model.m") # 模型加载