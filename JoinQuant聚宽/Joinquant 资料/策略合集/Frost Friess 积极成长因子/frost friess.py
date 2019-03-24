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
    g.tc=30      #调仓频率
    g.pe_ratio=25#市盈率
    g.lar=0.3    #资产负债率
    g.otr=0.8    #主营业务利润占比
    g.prr=0.1    #营业利润率
#2
#设置中间变量
def set_variables():
    g.t=0              #记录回测运行的天数
    g.if_trade=False   #当天是否交易
    g.feasible_stocks=[]#删除建仓日或者重新建仓日停牌的股票后剩余的可选股票
    
#3
#设置回测条件
def set_backtest():
    set_option('use_real_price', True)#用真实价格交易
    log.set_level('order', 'error')

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
        #g.feasible用来记录调仓日重新选择的股票组合
        g.feasible_stocks=set_feasible_stocks(context)
        # 设置手续费与手续费
        set_slip_fee(context) 
    #每次执行完要将交易日加1   
    g.t+=1
    
#4
#每次重新建仓时要重新选择股票，并将停牌的排除
def set_feasible_stocks(context):
    # 得到是否停牌信息的dataframe，停牌的1，未停牌得0
    suspened_info_df = get_price(list(get_all_securities('stock').index),start_date=context.current_dt,end_date=context.current_dt,frequency='daily', fields='paused')['paused'].T
    # 过滤停牌股票 返回dataframe
    unsuspened_index = suspened_info_df.iloc[:,0]<1
    # 得到当日未停牌股票的代码list:
    unsuspened_stocks = suspened_info_df[unsuspened_index].index
    return unsuspened_stocks
    
#5
# 根据不同的时间段设置滑点与手续费
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

'''
================================================================================
每天交易时
================================================================================
'''
#每个交易日需要运行的函数
def handle_data(context, data):
    #如果不需要调仓就不对仓中组合作处理，每日直接跳过即可
    if g.if_trade==True:
        signals = get_signals(context)
        buy_and_sell(signals, context)
    g.if_trade=False    

# 6  
# 产生信号函数
def get_signals(context):
    df = get_fundamentals(query(
         valuation.code, valuation.market_cap, valuation.pe_ratio, income.operating_profit,income.total_profit,income.operating_revenue,
         balance.total_liability,balance.total_assets
    ).filter(
        # 股票应满足策略指定的要求
        balance.total_liability / balance.total_assets < g.lar,
        valuation.pe_ratio < g.pe_ratio,
        income.operating_profit / income.total_profit > g.otr,
        income.operating_profit / income.operating_revenue > g.prr,
        # 并且应该在可行股票池内
        valuation.code.in_(g.feasible_stocks)
    ))
    return(list(df.code))

# 7
# 根据信号执行买卖
def buy_and_sell(signals,context):
    N=len(signals)
    #记录每个股票应该买入的数目
    every_stock= context.portfolio.portfolio_value/N
    holdings = context.portfolio.positions.keys()
    for stock in holdings:
        #判断老的组合中股票是否在新组合中,不在的话则卖出
        if stock not in signals:
            order_target(stock, 0)
    #将新组合中的所有股票的仓位调到everyStock
    for stock in signals:
        order_target_value(stock,every_stock)
    for stock in signals:
        order_target_value(stock,every_stock)

'''
================================================================================
每天收盘后
================================================================================
'''
# 每日收盘后要做的事情（本策略中不需要）
def after_trading_end(context):
    return

