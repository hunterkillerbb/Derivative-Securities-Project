#TD组合策略
def initialize(context):
    set_params()        #1设置策参数
    set_variables()     #2设置中间变量
    set_backtest()      #3设置回测条件
    g.stock = '000300.XSHG' #沪深300指数作为交易对象
    set_benchmark('000300.XSHG')
    
def set_params():
    g.buy_init = 0      #买入启动阶段计数，直到满足g.init_len为止
    g.sell_init = 0     #卖出启动阶段计数，直到满足g.init_len为止
    g.buy_count_1 = 0   #买入计数1，直到达到g.count_num为止
    g.buy_count_2 = 0   #买入计数2，直到达到g.count_num为止
    g.sell_count_1 = 0  #卖出计数1，直到达到g.count_num为止
    g.sell_count_2 = 0  #卖出计数2，直到达到g.count_num为止
    g.state = 'empty'   #仓位状态，是满仓还是空仓
    g.save_price = 0    #记录上次保存的价格状态
    g.init_lag = 4      #启动阶段和此前第四天的价格进行比较
    g.init_len = 4      #启动阶段为4
    g.count_lag = 2     #计数阶段和此前第二天的价格进行比较
    g.count_num = 14    #计数阶段临界值为14和28，计数1达到14或者计数2达到28则达到安全买卖点
    g.low=0.0           #用来保存计数阶段K线的最低值，从而判断是否达到止损条件

def set_variables():
    g.t=0              #记录回测运行的天数

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
    # 根据不同的时间段设置滑点与手续费
    set_slip_fee(context) 
    g.t+=1
    
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
def handle_data(context, data):
    #获取交易信号
    signal = get_signal(context)
    #根据交易信号买入卖出
    rebalance(signal, context)

#获取交易信号，并判断是买入还是卖出
def get_signal(context):
    #如果当前仓位为空，则寻找买入启动，找到后进行买入计数
    if g.state == 'empty':
        prices = list(attribute_history(g.stock, g.init_lag+1, '1d', 'close').close)
        prices_low=list(attribute_history(g.stock, g.init_lag+1, '1d', 'low').low)
        if prices[-1]<prices[0]:
            g.buy_init += 1
        else:
            g.buy_init = 0
        if g.buy_init == g.init_len:
            g.state = 'buy_count'
            g.buy_init = 0
            g.save_price = prices[-1]
            g.low=prices_low[-1]
            return 'poop'
    #如果当前仓位已满，则寻找卖出计数，找到后进行卖出计数
    elif g.state == 'full':
        prices = list(attribute_history(g.stock, g.init_lag+1, '1d', 'close').close)
        prices_low=list(attribute_history(g.stock, g.init_lag+1, '1d', 'low').low)
        if(g.low>prices_low[-1]):
            return 'sell'
        if prices[-1]>prices[0]:
            g.sell_init += 1
        else:
            g.sell_init = 0
        if g.sell_init == g.init_len:
            g.state = 'sell_count'
            g.sell_init = 0
            g.save_price = prices[-1]
            return 'poop'  
    #如果是买入计数则判断是否到达安全买点，如到达则买入
    elif g.state == 'buy_count':
        prices = attribute_history(g.stock, g.count_lag+1, '1d', ['close','high','low'])
        closes = list(prices.close)
        highs = list(prices.high)
        lows = list(prices.low)
        if closes[-1]<closes[0] or lows[-1]<lows[-2] or closes[-1]<g.save_price:
            if(g.low>lows[-1]):
                g.low=lows[-1]
            g.buy_count_1 += 1
        elif closes[-1]>closes[0] or highs[-1]>highs[-2] or closes[-1]>g.save_price:
            if(g.low>lows[-1]):
                g.low=lows[-1]
            g.buy_count_2 += 1
        if g.buy_count_1 == g.count_num*2 or g.buy_count_2 == g.count_num:
            g.state = 'full'
            g.buy_count_1 = 0
            g.buy_count_2 = 0
            return 'buy'
    #如果是卖出计数则判断是否到达安全卖点，如到达则卖出
    elif g.state == 'sell_count':
        prices = attribute_history(g.stock, g.count_lag+1, '1d', ['close','high','low'])
        closes = list(prices.close)
        highs = list(prices.high)
        lows = list(prices.low)
        if closes[-1]<closes[0] or lows[-1]<lows[-2] or closes[-1]<g.save_price:
            g.sell_count_2 += 1
        elif closes[-1]>closes[0] or highs[-1]>highs[-2] or closes[-1]>g.save_price:
            g.sell_count_1 += 1
        if g.sell_count_1 == g.count_num*2 or g.sell_count_2 == g.count_num:
            g.state = 'empty'
            g.sell_count_1 = 0
            g.sell_count_2 = 0
            return 'sell'

#根据获得的信号进行买入卖出操作，并将最低点计数归为0
def rebalance(signal, context):
    if signal=='buy':
        order_target_value(g.stock, context.portfolio.total_value)
    if signal=='sell':
        if(g.low!=0):
            order_target(g.stock, 0)
        #每次将仓位平空后，重新将计数期间K线最低点设置为0
        g.low=0.0
    
    
    

