# __author__ = Chen Meiying
# -*- coding: utf-8 -*-
# 2019/4/11 13:17


from factors.Frequency import SeasonalFrequency
from factors.Category import FinancialQualityFactor
from factors.sql import pl_sql_oracle

import pandas as pd

"""

季频、财务质量类因子

代码表：
    4001	ROEAvg
    4002	ROA
    4003	GrossIncomeRatio
    4004	TotalProfitCostRatio
    4005	ROIC
    4006	OperatingNIToTP
    4007	DPtoP
    4008	CashRateOfSales
    4009	NOCFToOperatingNITTM
    4010	CurrentLiabilityToTL
    4011	CurrentRatio
    4012	TotalAssetTRate


"""

class SeasonalFinancialQualityFactor(SeasonalFrequency, FinancialQualityFactor):

    def __init__(self, factor_code= '', name= '', describe= ''):
        super().__init__(factor_code, name, describe)
        self.type = '季频财务质量类'
        self.data_sql_file_path = r'.\sql\sql_seasonal_financial_quality_factor.sql'
        self.code_sql_file_path = r'.\sql\sql_get_secucode.sql'
        self.table_name = ['LC_MainIndexNew']

    def init_factors(self):
        factor_entities = dict()  # 存储实例化的因子

        # ROEAvg	净资产收益率_平均,计算值(%)
        ROEAvg = SeasonalFinancialQualityFactor(factor_code='4001',
                                                name='ROEAvg',
                                                describe='净资产收益率_平均,计算值（ROEAvg）==（归属于母公司的净利润*2/（期初归属于母公司的股东权益+期末归属于母公司的股东权益））*100%')
        factor_entities['ROEAvg'] = ROEAvg

        # ROA	总资产净利率(%)
        ROA = SeasonalFinancialQualityFactor(factor_code='4002',
                                             name='ROA',
                                             describe='总资产净利率（ROA）＝含少数股东损益的净利润*2/（期初总资产+期末总资产）*100%')
        factor_entities['ROA'] = ROA

        # GrossIncomeRatio	销售毛利率(%)
        GrossIncomeRatio = SeasonalFinancialQualityFactor(factor_code='4003',
                                                          name='GrossIncomeRatio',
                                                          describe=' 销售毛利率（GrossIncomeRatio）＝（营业收入-营业成本）/营业收入*100%，金融类企业不计算。')
        factor_entities['GrossIncomeRatio'] = GrossIncomeRatio

        # TotalProfitCostRatio	成本费用利润率
        TotalProfitCostRatio = SeasonalFinancialQualityFactor(factor_code='4004',
                                                              name='TotalProfitCostRatio',
                                                              describe='成本费用利润率（TotalProfitCostRatio）＝利润总额/成本费用总额*100%其中，成本费用总额＝营业成本（对金融类公司，用营业支出代替营业成本）+期间费用；期间费用＝财务费用+销售费用+管理费用。金融类企业不计算。')
        factor_entities['TotalProfitCostRatio'] = TotalProfitCostRatio

        # ROIC	投入资本回报率(%)
        ROIC = SeasonalFinancialQualityFactor(factor_code='4005',
                                              name='ROIC',
                                              describe='投入资本回报率ROIC=（息税前利润*（1-所得税/利润总额）*2/（期初全部投入资本+期末全部投入资本））*100%其中，息税前利润=利润总额+(利息支出-利息收入)，若报表附注中未披露利息费用，则用“财务费用”代替；全部投入资本=归属于母公司的股东权益+短期借款+交易性金融负债+一年内到期的非流动负债+长期借款+应付债券，金融类企业不计算。')
        factor_entities['ROIC'] = ROIC

        # OperatingNIToTP	 经营活动净收益/利润总额(%)
        OperatingNIToTP = SeasonalFinancialQualityFactor(factor_code='4006',
                                                         name='OperatingNIToTP',
                                                         describe='经营活动净收益／利润总额（OperatingNIToTP）＝经营活动净收益／利润总额*100%')
        factor_entities['OperatingNIToTP'] = OperatingNIToTP

        # DPtoP	单季度扣非净利润/净利润
        DPtoP = SeasonalFinancialQualityFactor(factor_code='4007',
                                               name='DPtoP',
                                               describe='单季度扣非净利润/净利润')
        factor_entities['DPtoP'] = DPtoP

        # CashRateOfSales	经营活动产生的现金流量净额/营业收入(%)
        CashRateOfSales = SeasonalFinancialQualityFactor(factor_code='4008',
                                                         name='CashRateOfSales',
                                                         describe='经营活动产生的现金流量净额/营业收入')
        factor_entities['CashRateOfSales'] = CashRateOfSales

        # NOCFToOperatingNITTM	经营活动产生的现金流量净额/经营活动净收益_TTM(%)
        NOCFToOperatingNITTM = SeasonalFinancialQualityFactor(factor_code='4009',
                                                              name='NOCFToOperatingNITTM',
                                                              describe='经营活动产生的现金流量净额/经营活动净收益（TTM）=经营活动产生的现金流量净额（TTM）/经营活动净收益（TTM）*100%，“经营活动净收益”的算法见 NOCFToOperatingNI[经营活动产生的现金流量净额/经营活动净收益（%）]。')
        factor_entities['NOCFToOperatingNITTM'] = NOCFToOperatingNITTM

        # CurrentLiabilityToTL	流动负债/负债合计(%)
        CurrentLiabilityToTL = SeasonalFinancialQualityFactor(factor_code='4010',
                                                              name='CurrentLiabilityToTL',
                                                              describe='流动负债／负债合计(%)(CurrentLiabilityToTL):该指标金融类企业不计算。')
        factor_entities['CurrentLiabilityToTL'] = CurrentLiabilityToTL

        # CurrentRatio	流动比率
        CurrentRatio = SeasonalFinancialQualityFactor(factor_code='4011',
                                                      name='CurrentRatio',
                                                      describe='流动比率（CurrentRatio）＝流动资产合计／流动负债合计，金融类企业不计算。')
        factor_entities['CurrentRatio'] = CurrentRatio

        # TotalAssetTRate	总资产周转率(次)
        TotalAssetTRate = SeasonalFinancialQualityFactor(factor_code='4012',
                                                         name='TotalAssetTRate',
                                                         describe='总资产周转率（TotalAssetTRate）＝营业总收入*2/（期初资产合计+期末资产合计）')
        factor_entities['TotalAssetTRate'] = TotalAssetTRate

        return factor_entities

    def find_components(self, file_path, secucode, date):
        """
        在数据库中查询计算本类因子需要的数据

        :return: pandas.DataFrame, sql语句执行后返回的数据
        """
        sql = pl_sql_oracle.dbData_import()
        components = sql.InputDataPreprocess(file_path, self.table_name,secucode, date)
        components['LC_MainIndexNew'] = components['LC_MainIndexNew'].sort_values(by='ENDDATE')
        components['LC_MainIndexNew_monthly'] = self.seasonal_to_monthly(components['LC_MainIndexNew'],['ROEAVG', 'ROA', 'GROSSINCOMERATIO', 'TOTALPROFITCOSTRATIO', 'ROIC', 'OPERATINGNITOTP', 'NETPROFITCUT','NETPROFIT', 'CASHRATEOFSALES', 'NOCFTOOPERATINGNITTM', 'CURRENTLIABILITYTOTL', 'CURRENTRATIO', 'TOTALASSETTRATE'])
        return components

    def get_factor_values(self, components):
        """
        计算本类所有的因子

        :param components: pandas.DataFrame,计算需要的数据
        :return:
            factor_values： pandas.DataFrame, 因子值
        """

        factor_values = pd.DataFrame(components['LC_MainIndexNew_monthly'][['SECUCODE','STARTDAY']]) # 存储因子值

        factor_values['ROEAvg'] = components['LC_MainIndexNew_monthly']['ROEAVG']
        factor_values['ROA'] = components['LC_MainIndexNew_monthly']['ROA']
        factor_values['GrossIncomeRatio'] = components['LC_MainIndexNew_monthly']['GROSSINCOMERATIO']
        factor_values['TotalProfitCostRatio'] = components['LC_MainIndexNew_monthly']['TOTALPROFITCOSTRATIO']
        factor_values['ROIC'] = components['LC_MainIndexNew_monthly']['ROIC']
        factor_values['OperatingNIToTP'] = components['LC_MainIndexNew_monthly']['OPERATINGNITOTP']
        factor_values['DPtoP'] = components['LC_MainIndexNew_monthly']['NETPROFITCUT']/components['LC_MainIndexNew_monthly']['NETPROFIT']
        factor_values['CashRateOfSales'] = components['LC_MainIndexNew_monthly']['CASHRATEOFSALES']
        factor_values['NOCFToOperatingNITTM'] = components['LC_MainIndexNew_monthly']['NOCFTOOPERATINGNITTM']
        factor_values['CurrentLiabilityToTL'] = components['LC_MainIndexNew_monthly']['CURRENTLIABILITYTOTL']
        factor_values['CurrentRatio'] = components['LC_MainIndexNew_monthly']['CURRENTRATIO']
        factor_values['TotalAssetTRate'] = components['LC_MainIndexNew_monthly']['TOTALASSETTRATE']


        return factor_values




if __name__ == '__main__':
    pass
    # sfqf = SeasonalFinancialQualityFactor(factor_code = '0019-0030', name = 'ROEAvg,ROA,GrossIncomeRatio,TotalProfitCostRatio,ROIC,OperatingNIToTP,DPtoP,CashRateOfSales,NOCFToOperatingNITTM,CurrentLiabilityToTL,CurrentRatio,TotalAssetTRate', describe = 'seasonal financial quality factor')
    # data_sql_file_path = r'D:\Meiying\codes\industrial\factors\sql\sql_seasonal_financial_quality_factor.sql'
    # code_sql_file_path = r'D:\Meiying\codes\industrial\factors\sql\sql_get_secucode.sql'
    # sfqf.write_values_to_DB(data_sql_file_path=data_sql_file_path, code_sql_file_path = code_sql_file_path)


