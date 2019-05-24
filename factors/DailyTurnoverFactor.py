# coding=utf-8
'''
Author: Kangchen Wei
Email:  weixk@cifutures.com.cn
Application : machine learning for investment

date: 2019/5/13  13:06
desc:
'''

# 引用frequency.py文件中相应的频率类
from Frequency import DailyFrequency

# 引用category.py文件中相应的类别类
from Category import TurnoverFactor
from sql import pl_sql_oracle
from util.TurnoverFuncProcess import TurnoverFuncProcess
from util.TurnoverFunc import TurnoverFunc
import pandas as pd

"""
!xx类因子

!代码表：

"""


class DailyTurnoverFactor(DailyFrequency,TurnoverFactor):

    def __init__(self, factor_code= '', name= '', describe= ''):
        super().__init__(factor_code, name, describe)
        self.type = '日频换手率类因子'
        self.target_methods,self.nameGroup = TurnoverFuncProcess()  # 生成因子代码和因子名称，进行初始化

    def init_factors(self):
        """
        初始化因子的基础特征,包括factor name, factor code和description

        :return: dict, key为因子名,value为因子类的一个实例
        """
        factor_entities = dict()
        for i in  range(len(self.target_methods)):
            factor_entities[self.target_methods[i]] = DailyTurnoverFactor(factor_code=self.nameGroup[i],name=self.target_methods[i],describe='')

        return factor_entities  # 不止一个因子

    def find_components(self, file_path, table_name,secucode = ''):
        """
        在数据库中查询计算本类因子需要的数据

        :return: pandas.DataFrame, sql语句执行后返回的数据
        """
        sql = pl_sql_oracle.dbData_import()
        components = sql.InputDataPreprocess(file_path, table_name, secucode )

        # TODO: 读取时需要按时间排序
        components['QT_Performance'] = components['QT_Performance'].sort_values(by='TRADINGDAY')

        return components

    def get_factor_values(self, components):
        """
        计算本类所有的因子

        :param components: pandas.DataFrame,计算需要的数据
        :return:
            factor_values： pandas.DataFrame, 因子值
        """

        factor_values = pd.DataFrame(components['QT_Performance'][['SECUCODE','TRADINGDAY']]) # 存储因子值
        TO_cal = TurnoverFunc(components['QT_Performance']['TURNOVERRATE'],components['QT_Performance']['CHANGEPCT'],
                              periodcoef=20,window=[1,3,6])

        for i in self.target_methods:
            temp_str = 'TO_cal.'+i+'()'
            # 注意.values的操作并不多余，生成的dataframe的列名均为0，重新设置成pd.DF后列名会重置成1,2,3..
            factor_values[[i+'_'+str(TO_cal.window[0])+'_'+str(self.frequency),i+'_'+str(TO_cal.window[1])+'_'+str(self.frequency),i+'_'+str(TO_cal.window[2])+'_'+str(self.frequency)]] = pd.DataFrame(eval(temp_str).values)
            # print(factor_values)

        return factor_values



    def write_values_to_DB(self,  code_sql_file_path, data_sql_file_path):
        """
        计算因子值并写入数据库中相应的数据表
        :param code_sql_file_path: str, 查询股票代码的sql文件路径
        :param data_sql_file_path: str, 读取数据库数据的sql代码文件路径
        :return: none
        """
        sql = pl_sql_oracle.dbData_import()
        s = sql.InputDataPreprocess(code_sql_file_path,['secucodes'])
        for row in s['secucodes'].itertuples(index=True, name='Pandas'):
            try:
                data = self.find_components(file_path= data_sql_file_path,
                                           table_name=['QT_Performance'],
                                           secucode=  'and t2.Secucode = \'' + getattr(row, 'SECUCODE') + '\'')
                factor_values = self.get_factor_values(data)

                from sqlalchemy import String, Integer
                print(factor_values)
                # TODO: 表名必须是小写
                # pl_sql_oracle.df_to_DB(factor_values, '!存入数据库的表名, 必须是连续的小写字符',if_exists='append',data_type={'SECUCODE': String(20)})

                print(self.type, getattr(row, 'SECUCODE'),' done')


            except Exception as e:
                print("write to database failed, error: ", getattr(row, 'SECUCODE'), e)



if __name__ == '__main__':
    TO = DailyTurnoverFactor(DailyFrequency, TurnoverFactor)
    data_sql_file_path = r'D:\项目\FOF相关资料\wind研报\工具性代码\Chen\industrial\factors_ver4\StockFactorsCreating\factors\sql\sql_daily_turnover_factor.sql' # 读取数据库数据的sql代码文件路径
    code_sql_file_path = r'D:\项目\FOF相关资料\wind研报\工具性代码\Chen\industrial\factors_ver4\StockFactorsCreating\factors\sql\sql_get_secucode.sql'  # 查询股票代码的sql文件路径
    TO.write_values_to_DB(data_sql_file_path=data_sql_file_path, code_sql_file_path = code_sql_file_path)

