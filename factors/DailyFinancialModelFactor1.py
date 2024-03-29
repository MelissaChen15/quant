# coding=utf-8
'''
Author: Kangchen Wei
Email:  weixk@cifutures.com.cn
Application : machine learning for investment

date: 2019/5/15  18:18
desc:
'''
# 引用frequency.py文件中相应的频率类
from factors.Frequency import DailyFrequency
# 引用category.py文件中相应的类别类
from factors.Category import FinancialModelFactor
from factors.sql import pl_sql_oracle
from factors.util.FinancialModelFuncProcess import FinancialModelFuncProcess
from factors.util.FinancialModelFunc import FinancialModel_statsFunc
import pandas as pd

"""
日频金融模型_FF3类因子

"""


class DailyFinancialModelFactor1(DailyFrequency,FinancialModelFactor):

    def __init__(self, factor_code= '', name= '', describe= ''):
        super().__init__(factor_code, name, describe)
        self.type = '日频金融模型_FF3类因子'
        self.target_methods,self.nameGroup = FinancialModelFuncProcess()  # 生成因子代码和因子名称，进行初始化
        self.code_sql_file_path_index = r'.\sql\sql_StockIndex.sql'
        self.SMB_HML_file_path_daily = r'.\sql\sql_daily_timeseries_factor.sql'
        self.SMB_HML_file_path_weekly = r'.\sql\sql_weekly_timeseries_factor.sql'
        self.data_sql_file_path = r'.\sql\sql_daily_financialmodel_factor.sql'  # 读取数据库数据的sql代码文件路径
        self.code_sql_file_path = r'.\sql\sql_get_secucode.sql'  # 查询股票代码的sql文件路径

    def init_factors(self):
        """
        初始化因子的基础特征,包括factor name, factor code和description

        :return: dict, key为因子名,value为因子类的一个实例
        """
        factor_entities = dict()
        count = 0000
        columns_name = ['alpha', 'beta_index', 'beta_HML', 'beta_SMB', '波动率', '上行波动率', '下行波动率', '上下波动率之差', '偏度']
        marketindex = ['IF', 'IC', 'IH']
        window = [3,6]

        for i in columns_name:
            for j in marketindex:
                for w in window:
                    name = i + '_' + j + '_'+ str(w) + '_m'
                    entity = DailyFinancialModelFactor1(factor_code='DFA%04d' % count,
                                            name=name,
                                            describe='')
                    factor_entities[name] = entity
                    count += 1

        return factor_entities

    def find_components(self, file_path,secucode,date):
        """
        在数据库中查询计算本类因子需要的数据

        :return: pandas.DataFrame, sql语句执行后返回的数据
        """
        sql = pl_sql_oracle.dbData_import()
        components = sql.InputDataPreprocess(self.data_sql_file_path, ['QT_Performance'], secucode, date)

        components['QT_Performance'] = components['QT_Performance'].sort_values(by='TRADINGDAY')
        # print(components)
        return components

    def get_factor_values(self, components):
        """
        计算本类所有的因子

        :param components: pandas.DataFrame,计算需要的数据
        :return:
            factor_values： pandas.DataFrame, 因子值
        """
        # factor_values['SECUCODE'] = pd.DataFrame(components['QT_Performance']['SECUCODE']) # 'secucode'因子的长度与后面的数据要保持一致

        TO_cal = FinancialModel_statsFunc(components['QT_Performance']['TRADINGDAY'],components['QT_Performance']['CHANGEPCT'],
                                          flag=1,code_sql_file_path1=self.code_sql_file_path_index)

        # columns_name1 = ['alpha','beta','波动率', '上行波动率', '下行波动率', '上下波动率之差', '偏度','上行beta','下行beta','上下行beta差']
        columns_name2 = ['alpha','beta_index','beta_HML','beta_SMB','波动率', '上行波动率', '下行波动率', '上下波动率之差', '偏度']
        marketindex = ['IF','IC','IH']

        datagroup_FF3 = pd.DataFrame()
        for i in marketindex:
            # print(i)
            # print(self.SMB_HML_file_path_daily)
            # print(self.SMB_HML_file_path_weekly)
            alpha1_all, beta_all, residuals_stats = TO_cal.FF3_model_stats(i,self.SMB_HML_file_path_daily,self.SMB_HML_file_path_weekly)
            index_datagroup = pd.DataFrame()
            for j in alpha1_all.keys():
                temp_datagroup = pd.concat([alpha1_all[j],beta_all[j],residuals_stats[j]],axis=1)
                columns_name_temp = [k+'_'+i+'_'+j[-1]+'m' for k in columns_name2 ]
                temp_datagroup.columns = columns_name_temp
                index_datagroup = pd.concat([index_datagroup,temp_datagroup],axis=1)
            datagroup_FF3 = pd.concat([datagroup_FF3,index_datagroup],axis=1)

        # print(len(datagroup_FF3))
        factor_values = pd.DataFrame()
        factor_values[list(datagroup_FF3.columns)] = datagroup_FF3
        factor_values['TRADINGDAY'] = datagroup_FF3.index
        factor_values['SECUCODE'] = components['QT_Performance']['SECUCODE'].values[:len(datagroup_FF3)]

        # factor_values.to_excel(r'C:\Users\Kww\Desktop\temp.xlsx')

        return factor_values
