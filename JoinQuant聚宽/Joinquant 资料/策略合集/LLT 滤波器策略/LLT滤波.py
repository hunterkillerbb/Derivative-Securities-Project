
# 克隆自聚宽文章：https://www.joinquant.com/post/11158
# 标题：【量化课堂】LLT-发现股市中的“大浪”
# 作者：JoinQuant量化课堂

import talib
import pandas as pd
import numpy as np
import math
from sklearn.model_selection import learning_curve
import copy

import talib


def initialize(context):
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    # 定义一个全局变量, 保存要操作的证券                                                                                           
    context.stocks = ['399300.XSHE']
    # 设置我们要操作的股票池
    set_universe(context.stocks)
    
    h = attribute_history('399300.XSHE', 60, '1d', ('high','low','close'))
    g.alpha1 = 2./35
    #计算LLT需要带入一天前的LLT和两天前的LLT，设一天前的LLT为LLT1，两天前的LLT为LLT2
    #但是最开始的第一个和第二个LLT由于没有前值无法求出，我们先用EMA得到最开始的LLT1和LLT2
    #在之后的循环中，下一个LLT_1和LLT_2分别会取代LLT_now和LLT_1
    g.LLT2=h['close'].values[-4]
    g.LLT1=(1-g.alpha1)*h['close'].values[-3]+g.alpha1*h['close'].values[-4]
    g.LLT_now=(1-g.alpha1)*h['close'].values[-2]+g.alpha1*g.LLT1

    
# 初始化此策略
def handle_data(context, data):
    # 取得当前的现金
    cash = context.portfolio.cash
    # 循环股票列表
    for stock in context.stocks:
        # 获取股票的数据
        h = attribute_history(stock, 60, '1d', ('high','low','close'))
        g.LLT2=copy.deepcopy(g.LLT1)
        g.LLT1=copy.deepcopy(g.LLT_now)      
        LLT2=g.LLT2
        LLT1=g.LLT1
        a=g.alpha1
        #LLT_now=(a-a**2/4)*h['close'].values[-1]+a**2/2*h['close'].values[-2]-(a-3*a**2/4)*h['close'].values[-3]+2*(1-a)*LLT1-(1-a)**2*LLT2
        LLT_now=(a-(a**2)/4)*h['close'].values[-1]+(a**2)/2*h['close'].values[-2]-(a-(3./4)*(a**2))*h['close'].values[-3]+2*(1-a)*LLT1-(1-a)**2*LLT2
        g.LLT_now=copy.deepcopy(LLT_now)
        print('HS300:     {0}'.format(h['close'].values[-1]))
        print('昨天的LLT:     {0}'.format(LLT1))
        print('今天的HS300:     {0}'.format(LLT_now))

        current_position = context.portfolio.positions[stock].amount
        # 获取当前股票价格
        current_price = data[stock].price
        # 当 LLT_now < LLT1，且拥有的股票数量>=0时，卖出所有股票
        if LLT_now < LLT1 and LLT1 > LLT2 and current_position >= 0:
            order_target(stock, 0)
        # 当 LLT_now > LLT1, 且拥有的股票数量<=0时，则全仓买入
        elif LLT_now > LLT1 and LLT1 < LLT2 and current_position <= 0:
            # 买入股票
            order_value(stock, cash)
            # 记录这次买入
            log.info("Buying %s" % (stock))