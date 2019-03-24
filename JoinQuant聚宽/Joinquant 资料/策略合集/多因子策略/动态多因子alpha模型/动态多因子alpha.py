
import jqdata
import pandas
from jqfactor import Factor, calc_factors
import datetime
import numpy as np 
# from statsmodels.api import OLS
import statsmodels.api as sm
import math


# 策略初始化
def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    log.set_level('order', 'error')
    set_order_cost(OrderCost(close_tax=0, open_commission=0, close_commission=0, min_commission=0), type='stock')
    # 按月调仓
    run_monthly(market_open,1, time='open', reference_security='000300.XSHG')
    g.all_stocks = []


#过滤停牌的股票
def set_feasible_stocks(stock_list):
    current_data = get_current_data()
    stock_list = [stock for stock in stock_list if not current_data[stock].paused] # 不考虑停盘的股票
    return stock_list
    

'''
######################策略的交易逻辑######################
每周计算因子值， 并买入前 20 支股票
'''

   
# 每周开盘运行一次， 按照上一交易日的因子值进行调仓
def market_open(context):
    # 1. 定义计算因子的 universe，
    #    建议使用与 benchmark 相同的指数，方便判断选股带来的 alpha
    universe0 = get_index_stocks('000300.XSHG', context.previous_date)
    g.all_stocks = set_feasible_stocks(get_index_stocks('000300.XSHG', context.previous_date))
    universe = g.all_stocks
    #过滤上市时间小于60天的股票
    for stock in universe:
        days_public = (context.current_dt.date() - get_security_info(stock).start_date).days
        if days_public<60:
            universe.remove(stock)
    g.lenth = len(universe)
    
    # 2. 获取因子值
    #    get_factor_values 有三个参数，context、因子列表、股票池， 
    #    返回值是一个 dict，key 是因子类的 name 属性，value 是 pandas.Series
    #    Series 的 index 是股票代码，value 是当前日期能看到的最新因子值
    factor_values = get_factor_values(context, [ep(),bp(),sp(),turnover(),ivff(),profitgrowthrate(),equitygrowthrate()], universe)
    
    EP_TTM = factor_values['EP_TTM']
    BP = factor_values['BP']
    SP_TTM = factor_values['SP_TTM']
    Turnover = factor_values['Turnover']
    ProfitGrowthRate = factor_values['ProfitGrowthRate']
    EquityGrowthRate = factor_values['EquityGrowthRate']
    IVFF = factor_values['IVFF']
    
    # 3. 对因子做线性加权处理， 并将结果进行排序。
    #    对因子做 rank 是因为不同的因子间由于量纲等原因无法直接相加，这是一种去量纲的方法。
    #这里的系数是根据规模因子MV将股票分为高规模、低规模，和不分层一起共三种情况，各有一套系数。
    #高规模分层权重
    final_factor = .381536*EP_TTM.rank(ascending=True) + .210049*BP.rank(ascending=True) + .156827*SP_TTM.rank(ascending=True)+.195742*Turnover.rank(ascending=False)+.609915*IVFF.rank(ascending=False) +.245025*ProfitGrowthRate.rank(ascending=True) + .016939*EquityGrowthRate.rank(ascending=True)
    #不规模分层权重
    # final_factor = .50766*EP_TTM.rank(ascending=True) + .361407*BP.rank(ascending=True) + .194835*SP_TTM.rank(ascending=True)+.266527*Turnover.rank(ascending=False)+ .81163*IVFF.rank(ascending=False)+.601718*ProfitGrowthRate.rank(ascending=True) + .235565*EquityGrowthRate.rank(ascending=True)
    #低规模分层权重
    # final_factor = .43503*EP_TTM.rank(ascending=True) + .535049*BP.rank(ascending=True) + .250863*SP_TTM.rank(ascending=True)+.31487*Turnover.rank(ascending=False)+ .975986*IVFF.rank(ascending=False) +.649754*ProfitGrowthRate.rank(ascending=True) + .28018*EquityGrowthRate.rank(ascending=True)
    
    # 4. 由因子确定每日持仓的股票列表：
    #    采用因子值由大到小排名前 10 只股票作为目标持仓

    stocks_list = list(final_factor.order(ascending=False)[:10].index)
    
    
    # 5. 根据股票列表进行调仓：
    #    这里采取所有股票等额买入的方式，您可以使用自己的风险模型自由发挥个股的权重搭配
    rebalance_position(context, stocks_list)

    
'''
######################下面是策略中使用的三个因子######################
可以先使用因子分析功能生产出理想的因子， 再加入到策略中
因子分析：https://www.joinquant.com/algorithm/factor/list
'''

# EP_TTM
# 参考链接 https://www.joinquant.com/data/dict/alpha191
class ep(Factor):
    # 设置因子名称
    name = 'EP_TTM'
    # 设置获取数据的时间窗口长度
    max_window = 1
    # 设置依赖的数据
    dependencies = ['pe_ratio','market_cap',
                    'HY001','HY002','HY003',
                    'HY004','HY005','HY006',
                    'HY007','HY008','HY009',
                    'HY010','HY011']
   
    # 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值
    def calc(self, data):
        EP_TTM = 1/data['pe_ratio']
        return neutralization(data, EP_TTM.mean())
        
def neutralization(data, factor):
    industry_exposure = pd.DataFrame(index=data['HY001'].columns)
    industry_list = ['HY001','HY002','HY003','HY004','HY005',
                    'HY006','HY007','HY008','HY009','HY010','HY011']
    for key, value in data.items():
        if key in industry_list:
            industry_exposure[key]=value.iloc[-1]
    market_cap_exposure = data['market_cap'].iloc[-1]
    total_exposure = pd.concat([market_cap_exposure,industry_exposure],axis=1)
    result = sm.OLS(factor, total_exposure, missing='drop').fit().resid
    return result


# BP
# 参考链接 https://www.joinquant.com/data/dict/alpha191
class bp(Factor):
    # 设置因子名称
    name = 'BP'
    # 设置获取数据的时间窗口长度
    max_window = 1
    # 设置依赖的数据
    dependencies = ['pb_ratio','market_cap',
                    'HY001','HY002','HY003',
                    'HY004','HY005','HY006',
                    'HY007','HY008','HY009',
                    'HY010','HY011']
   
    # 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值
    def calc(self, data):
        BP = 1/data['pb_ratio']
        return neutralization(data, BP.mean())

# SP_TTM
# 参考链接：https://www.joinquant.com/post/6585
class sp(Factor):
    # 设置因子名称
    name = 'SP_TTM'
    # 设置获取数据的时间窗口长度
    max_window = 1
    # 设置依赖的数据
    dependencies = ['ps_ratio','market_cap',
                    'HY001','HY002','HY003',
                    'HY004','HY005','HY006',
                    'HY007','HY008','HY009',
                    'HY010','HY011']
    # 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值
    def calc(self, data):
        SP_TTM = 1/data['ps_ratio']
        return  neutralization(data,SP_TTM.mean())
        

# Turnover
class turnover(Factor):
    # 设置因子名称
    name = 'Turnover'
    # 设置获取数据的时间窗口长度
    max_window = 1
    # 设置依赖的数据
    dependencies = ['turnover_ratio','market_cap',
                    'HY001','HY002','HY003',
                    'HY004','HY005','HY006',
                    'HY007','HY008','HY009',
                    'HY010','HY011']
   
    # 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值
    def calc(self, data):
        Turnover = data['turnover_ratio']
        return neutralization(data,Turnover.mean())


class ivff(Factor):
    # 设置因子名称
    name = 'IVFF'
    # 设置获取数据的时间窗口长度
    max_window = 21
    # 设置依赖的数据
    dependencies = ['circulating_market_cap','pb_ratio','close','market_cap',
                    'HY001','HY002','HY003',
                    'HY004','HY005','HY006',
                    'HY007','HY008','HY009',
                    'HY010','HY011']
    # 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值
    def calc(self, data):
        circulating_market_cap = data['circulating_market_cap'].iloc[-1,:]
        circulating_market_cap.name = 'circulating_market_cap'
        pb_ratio = data['pb_ratio'].iloc[-1,:]
        pb_ratio.name='pb_ratio'
        close = data['close']
       
        
        df = pd.DataFrame()
        df = pd.concat([circulating_market_cap,pb_ratio],axis=1)
        
    
        
    # 计算个股近30日收益
        stock_return = np.log(data['close'].iloc[-1,:])-np.log(data['close'].iloc[0,:])
        log_returns = pd.DataFrame(stock_return,columns=['log_returns'])
        
        df = pd.concat([log_returns,pb_ratio,circulating_market_cap],axis=1)
        
        market = self._get_extra_data(securities=['000300.XSHG'], fields=['close'])['close']
        market = pd.DataFrame(np.log(market).diff())[1:]
        market.columns={'market'}
        
        
        # sub_returns_df = pd.DataFrame(data=[str(start.year)+str(start.month)]*3, index=range(3),columns={'date'})
        sub_returns_df = pd.DataFrame()
        sub_returns = pd.DataFrame()

        for i in range(3):#log_returns,pb_ratio,circulating_market_cap
            factor = df.iloc[:,i]
            column = factor.name
            new = pd.concat([factor,close.T],axis = 1)
            new1 = new.dropna()
            new1['id'] = pd.qcut(new1[column], 3, labels=[0,1,2])
            
            for j in range(3):
                sub=new1[new1['id']==j]
                log_return_portfolio = np.log(sub.sum()[1:-1]).diff()[1:]
                sub_returns[str(column)+str(j)] = pd.Series(log_return_portfolio) # 0 1 2 代表了123组
        
        sub_returns_df = pd.concat([sub_returns_df,sub_returns],axis=1) 

        
        HMB = pd.DataFrame(sub_returns_df.iloc[:,0]- sub_returns_df.iloc[:,2],columns=['HMB'])
        MOM = pd.DataFrame(sub_returns_df.iloc[:,6] - sub_returns_df.iloc[:,8],columns=['MOM'])
        SMB = pd.DataFrame(sub_returns_df.iloc[:,3] - sub_returns_df.iloc[:,5],columns=['SMB'])
            
        ff = pd.concat([market,SMB,HMB],axis=1).iloc[:20.:]
     
        
        hh = np.log(close).diff()[1:]
        
        resid_df2 = pd.DataFrame()
        for i in range(g.lenth):
            stock=hh.iloc[:,i]
            stock_name = hh.iloc[:,i].name
            new = sm.add_constant(ff) 
            new1 = pd.concat([stock,new],axis = 1)
            new1 = new1.dropna()
            results = sm.OLS(new1[stock_name],new1.ix[:,~new1.columns.isin([stock_name])]).fit()
            resid_df2[stock_name] = pd.Series(results.resid, name=stock_name, index=list(hh.index))
          
        IVFF= pd.Series(resid_df2.std()*math.sqrt(243),name='IVFF')
        return IVFF

# ProfitGrowthRate
class profitgrowthrate(Factor):
    # 设置因子名称
    name = 'ProfitGrowthRate'
    # 设置获取数据的时间窗口长度
    max_window = 1
    # 设置依赖的数据
    dependencies = ['inc_net_profit_year_on_year','market_cap',
                    'HY001','HY002','HY003',
                    'HY004','HY005','HY006',
                    'HY007','HY008','HY009',
                    'HY010','HY011']

    # 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值
    def calc(self, data):
        # 计算增长率
        growth = data['inc_net_profit_year_on_year']
        # 返回一个 series
        return neutralization(data,growth.mean())


# EquityGrowthRate
class equitygrowthrate(Factor):
    # 设置因子名称
    name = 'EquityGrowthRate'
    # 设置获取数据的时间窗口长度
    max_window = 1
    # 设置依赖的数据
    dependencies = ['equities_parent_company_owners','equities_parent_company_owners_y','market_cap',
                    'HY001','HY002','HY003',
                    'HY004','HY005','HY006',
                    'HY007','HY008','HY009',
                    'HY010','HY011']

    # 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值
    def calc(self, data):
        # 个股最新一年度的净利润数据
        equity = data['equities_parent_company_owners']
        # 个股最新一年度的上一年的净利润数据
        equity_y = data['equities_parent_company_owners_y']
        # 计算增长率
        EquityGrowthRate = equity/equity_y - 1
        # 返回一个 series
        return neutralization(data,EquityGrowthRate.mean())

    
"""
###################### 工具 ######################

调仓：
先卖出持仓中不在 stock_list 中的股票
再等价值买入 stock_list 中的股票
"""
def rebalance_position(context, stocks_list):
    current_holding = context.portfolio.positions.keys()
    stocks_to_sell = list(set(current_holding) - set(stocks_list))
    # 卖出
    bulk_orders(stocks_to_sell, 0)
    total_value = context.portfolio.total_value
    
    # 买入  
    bulk_orders(stocks_list, total_value/len(stocks_list))

# 批量买卖股票
def bulk_orders(stocks_list,target_value):
    for i in stocks_list:
        order_target_value(i, target_value)

"""
# 策略中获取因子数据的函数
每日返回上一日的因子数据
详见 帮助-单因子分析
"""
def get_factor_values(context,factor_list, universe):
    """
    输入： 因子、股票池
    返回： 前一日的因子值
    """
    # 取因子名称
    factor_name = list(factor.name for factor in factor_list)

    # 计算因子值
    values = calc_factors(universe, 
                        factor_list,
                        context.previous_date, 
                        context.previous_date)
    # 装入 dict
    factor_dict = {i:values[i].iloc[0] for i in factor_name}
    return factor_dict



