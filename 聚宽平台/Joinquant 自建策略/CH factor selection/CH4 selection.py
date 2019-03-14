#CH4 selection 
#joinquant  2005-01-04开始才有TR数据

import statsmodels.api as sm
from statsmodels import regression         
import numpy as np
import pandas as pd
import time 
from datetime import date
from jqdata import *
from scipy.stats.mstats import winsorize

'''
================================================================================
总体回测前
================================================================================
'''
#总体回测前要做的事情
def initialize(context):
    set_params()        #1设置策参数
    set_variables()     #2设置中间变量
    set_backtest()      #3设置回测条件
    
#1
#设置策参数
def set_params():
    g.tc=10  # 调仓频率
    g.yb=63  # 样本长度
    g.N=15   # 持仓数目
    g.NoF=4  # 三因子模型还是五因子模型
    
#2
#设置中间变量
def set_variables():
    g.t=0               #记录连续回测天数
    g.rf=0.032          #无风险利率
    g.if_trade=False    #当天是否交易
    
    #将2005-01-04至今所有交易日弄成列表输出
    today=date.today()     #取当日时间xxxx-xx-xx
    a=get_all_trade_days() #取所有交易日:[datetime.date(2005, 1, 4)到datetime.date(2016, 12, 30)]
    g.ATD=['']*len(a)      #获得len(a)维的单位向量
    for i in range(0,len(a)):
        g.ATD[i]=a[i].isoformat() #转换所有交易日为iso格式:2005-01-04到2016-12-30
        #列表会取到2016-12-30，现在需要将大于今天的列表全部砍掉
        if today<=a[i]:
            break
    g.ATD=g.ATD[:i]        #iso格式的交易日：2005-01-04至今
    
#3
#设置回测条件
def set_backtest():
    set_option('use_real_price', True) #用真实价格交易
    log.set_level('order', 'error')
    set_slippage(FixedSlippage(0))     #将滑点设置为0


'''
================================================================================
每天开盘前
================================================================================
'''
#每天开盘前要做的事情
def before_trading_start(context):
    if g.t%g.tc==0:
        #每g.tc天，交易一次行
        g.if_trade=True 
        # 设置手续费与手续费
        set_slip_fee(context) 
        # 设置可行股票池：获得当前开盘的沪深300股票池并剔除当前或者计算样本期间停牌的股票
        g.all_stocks = set_feasible_stocks(get_index_stocks('000300.XSHG'),g.yb,context)
    g.t+=1

#4 根据不同的时间段设置滑点与手续费
def set_slip_fee(context):
    # 将滑点设置为0
    set_slippage(FixedSlippage(0)) 
    # 根据不同的时间段设置手续费
    dt=context.current_dt
    log.info(type(context.current_dt))
    
    if dt>datetime.datetime(2013,1, 1):
        set_commission(PerTrade(buy_cost=0.0003, sell_cost=0.0013, min_cost=5)) 
        
    elif dt>datetime.datetime(2011,1, 1):
        set_commission(PerTrade(buy_cost=0.001, sell_cost=0.002, min_cost=5))
            
    elif dt>datetime.datetime(2009,1, 1):
        set_commission(PerTrade(buy_cost=0.002, sell_cost=0.003, min_cost=5))
                
    else:
        set_commission(PerTrade(buy_cost=0.003, sell_cost=0.004, min_cost=5))


#5
# 设置可行股票池：
# 过滤掉当日停牌的股票,且筛选出前days天未停牌股票
# 输入：stock_list-list类型,样本天数days-int类型，context（见API）
# 输出：颗星股票池-list类型
def set_feasible_stocks(stock_list,days,context):
    # 得到是否停牌信息的dataframe，停牌的1，未停牌得0
    suspened_info_df = get_price(list(stock_list), start_date=context.current_dt, end_date=context.current_dt, frequency='daily', fields='paused')['paused'].T
    # 过滤停牌股票 返回dataframe
    unsuspened_index = suspened_info_df.iloc[:,0]<1
    # 得到当日未停牌股票的代码list:
    unsuspened_stocks = suspened_info_df[unsuspened_index].index
    # 进一步，筛选出前days天未曾停牌的股票list:
    feasible_stocks=[]
    current_data=get_current_data()
    for stock in unsuspened_stocks:
        if sum(attribute_history(stock, days, unit='1d',fields=('paused'),skip_paused=False))[0]==0:
            feasible_stocks.append(stock)
   
    return feasible_stocks


'''
================================================================================
每天交易时
================================================================================
'''

#每天交易时要做的事情
def handle_data(context, data):
    if g.if_trade==True:
        # 获得调仓日的日期字符串
        todayStr=str(context.current_dt)[0:10]#去掉时分秒，保留年月日
        # 计算每个股票的ai
        ais=CH4(g.all_stocks,getDay(todayStr,-g.yb),getDay(todayStr,-1),g.rf)
        # 为每个持仓股票分配资金
        g.everyStock=context.portfolio.portfolio_value/g.N
        # 依打分排序，当前需要持仓的股票
        stock_sort=ais.sort('score')['code']
        
        order_stock_sell(context,data,stock_sort)
                
        order_stock_buy(context,data,stock_sort)       
                
    g.if_trade=False

#6
#获得卖出信号，并执行卖出操作
#输入：context, data，已排序股票列表stock_sort-list类型
#输出：none
def order_stock_sell(context,data,stock_sort):
    # 对于不需要持仓的股票，全仓卖出
    for stock in context.portfolio.positions:
        #除去排名前g.N个股票（选股！）
        if stock not in stock_sort[:g.N]:
            stock_sell = stock
            order_target_value(stock_sell, 0)


#7
#获得买入信号，并执行买入操作
#输入：context, data，已排序股票列表stock_sort-list类型
#输出：none
def order_stock_buy(context,data,stock_sort):
    # 对于需要持仓的股票，按分配到的份额买入
    for stock in stock_sort:
        stock_buy = stock
        order_target_value(stock_buy, g.everyStock)

def list_divide(a,b):
    c = []
    for i in range(len(a)):
        if b[i] == 0:
            c.append(np.nan)
        else:
            c.append(a[i]/b[i])
    for i in range(len(a)):
        if isnan(c[i]) == True:
            c[i] = max(c)
        
    return c


def standardize(x):
    return (x - mean(x))/np.sqrt(var(x))

#8
#按照CH4规则计算k个参数并且回归，计算出股票的alpha并且输出
#输入：stocks-list类型； begin，end为“yyyy-mm-dd”类型字符串,rf为无风险收益率-double类型
#输出：最后的打分-dataframe类型
def CH4(stocks,begin,end,rf):
    #查询因子的语句
    LoS = len(stocks)
    q = query(
        valuation.code,
        valuation.market_cap.label('MC'),
        (1/valuation.pe_ratio).label("EP"),
        valuation.turnover_ratio.label('TR')
        ).filter(
        valuation.code.in_(stocks) 
    )

 
    df_1 = get_fundamentals(q,begin).sort('MC',ascending = False)[:int(LoS*0.7)]
    df_12 = df_1.sort('EP',ascending = False)
    df_13= df_1.sort('TR', ascending = False)
    sel_codes1 = df_1.code
    sel_codes2 = df_12.code
    df_1 = standardize(list(winsorize(list(df_1.MC),limits = [0.05,0.05], inplace = True)))
    df_12 = standardize(list(winsorize(list(df_12.EP),limits = [0.05,0.05], inplace = True)))
    df_1 = pd.DataFrame({'code': sel_codes1, 'MC': df_1},columns =['code', 'MC'])
    df_12 = pd.DataFrame({'code': sel_codes2, 'EP': df_12},columns =['code', 'EP'])

    
    df_14= pd.DataFrame({'code':df_13.code, 'TR':df_13.TR},columns = ['code','TR'])
    sel_codes3 = df_14.code
    df_15= pd.DataFrame({'code':sel_codes3})
    default  = list(ones(int(LoS*0.7)))


    TR_lm_sum = 0
    TR_ly_sum = 0
    
   
    for i in range(-1,-253,-1):
        df_131 = get_fundamentals(q,getDay(begin,i)) 
        if len(df_131) ==0:
            df_131 = pd.DataFrame({'code':sel_codes3, 'TR':default},columns = ['code','TR'] )
        else:
            df_131 = pd.DataFrame({'code':df_131.code, 'TR':df_131.TR},columns = ['code','TR'] )

        df_14 = df_14.merge(df_131, how ='inner', on ='code')
    
    df_16 = pd.merge(df_15,df_14,how ='left',on ='code').fillna(value = 0)
    TR_ly_sum = df_16.iloc[:,1:].apply(lambda x: x.sum(), axis = 1)
    TR_lm_sum = df_16.iloc[:,1:22].apply(lambda x:x.sum(),axis = 1)    
    TR_df = pd.Series(list_divide(list(TR_lm_sum),list(TR_ly_sum))).fillna(0).tolist()
    TR_df = standardize(list(winsorize(TR_df,limits = [0.05,0.05], inplace = True)))
    T_df = pd.DataFrame({'code':sel_codes3, 'TR': TR_df },columns =['code','TR']).fillna(value = 0)
    

    stocks = list(df_1['code'])
    LoS = int(LoS *0.7)
    median = np.median(df_1['MC'].values)

    # 选出特征股票组合
    V=df_12['code'][:int(LoS*0.3)]
    M=df_12['code'][int(LoS*0.3):int(LoS*0.7)] 
    G=df_12['code'][int(LoS*0.7):LoS]
    S=df_1['code'][df_1['MC']<= median]
    B=df_1['code'][df_1['MC']> median]
    T1=T_df['code'][:int(LoS*0.3)]
    T2=T_df['code'][int(LoS*0.3):int(LoS*0.7)]
    T3=T_df['code'][int(LoS*0.7):LoS]
    

    # 获得样本期间的股票价格并计算日收益率
    df_2 = get_price(stocks,begin,end,'1d')
    df_3= df_2['close'][:]
    df_4=np.diff(np.log(df_3),axis=0)+0*df_3[1:]
    #求因子的值
   
    PMO= sum(df_4[T3].T)/len(V) - sum(df_4[T1].T)/len(G)
    
    VMG = sum(df_4[V].T)/len(V)- sum(df_4[G].T)/len(G)

    SMB = sum(df_4[S].T)/len(S) - sum(df_4[B].T)/len(B)

    dp=get_price('000300.XSHG',begin,end,'1d')['close']
    MKT=diff(np.log(dp))-rf/252
      







    #将因子们计算好并且放好
    X=pd.DataFrame({"PMO":PMO,"VMG":VMG,"SMB":SMB,"MKT":MKT}).fillna(value = 0)
    #取前g.NoF个因子为策略因子
    factor_flag=["PMO","VMG","SMB","MKT"][:g.NoF]
    print factor_flag
    X=X[factor_flag]
    
    # 对样本数据进行线性回归并计算ai 
    t_scores=[0.0]*LoS
    for i in range(LoS):
        t_stock=stocks[i]
        sample=pd.DataFrame()
        t_r=linreg(X,df_4[t_stock]-rf/252,len(factor_flag))
        t_scores[i]=t_r[0]
    
    #这个scores就是alpha 
    scores=pd.DataFrame({'code':stocks,'score':t_scores})

    return scores

#9
# 辅助线性回归的函数
# 输入:X:回归自变量 Y:回归因变量 完美支持list,array,DataFrame等三种数据类型
#      columns:X有多少列，整数输入，不输入默认是3（）
# 输出:参数估计结果-list类型
def linreg(X,Y,columns=3):
    X=sm.add_constant(array(X))
    Y=array(Y)
    if len(Y)>1:
        results = regression.linear_model.OLS(Y, X).fit()
        return results.params
    else:
        return [float("nan")]*(columns+1)


#10
# 日期计算之获得某个日期之前或者之后dt个交易日的日期
# 输入:precent-当前日期-字符串（如2016-01-01）
#      dt-整数，如果要获得之前的日期，写负数，获得之后的日期，写正数
# 输出:字符串（如2016-01-01）
def getDay(precent,dt):
    for i in range(0,len(g.ATD)):
        if precent<=g.ATD[i]:
            t_temp = i
            if t_temp+dt>=0:
                return g.ATD[t_temp+dt]#present偏移dt天后的日期
            else:
                t= datetime.datetime.strptime(g.ATD[0],'%Y-%m-%d')+datetime.timedelta(days = dt)
                t_str=datetime.datetime.strftime(t,'%Y-%m-%d')
                return t_str

'''
================================================================================
每天收盘后
================================================================================
'''
#每天收盘后要做的事情
def after_trading_end(context):
    return
# 进行长运算（本模型中不需要）


 #PMO= 0.5*(sum(df_4[T3].T)/len(V) + sum(df_4[T1])/len(V)) - 0.5*(sum(df_4[S].T)/len(G)+sum(df_4[].T)/len(G))
    
   #VMG = 0.5* (sum(df_4[S].T)/len(V)+sum(df_4[B].T)/len(V))- 0.5*(sum(df_4[S].T)/len(G)+sum(df_4[B].T)/len(G))

   # SMB1 = 1/3 * (sum(df_4[S].T)/len(V)) + 1/3 * (sum(df_4[S].T)/len(M)) + 1/3 * (sum(df_4[S].T)/len(G))
   # SMB2 = 1/3 * (sum(df_4[B].T)/len(V)) + 1/3 * (sum(df_4[B].T)/len(M)) + 1/3 * (sum(df_4[B].T)/len(G))
   # SMB= SMB1 - SMB2 
                 
   # MKT= 1/3*(sum(df_4[V].T)/len(V) +sum(df_4[M].T)/ len(M) +sum(df_4[G].T)/len(G)) - g.rf/252  