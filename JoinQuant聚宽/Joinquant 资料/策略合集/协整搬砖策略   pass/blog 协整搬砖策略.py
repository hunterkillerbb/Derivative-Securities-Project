
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import statsmodels.api as sm
import seaborn as sns


# In[2]:


# 输入是一DataFrame，每一列是一支股票在每一日的价格
def find_cointegrated_pairs(dataframe):
    # 得到DataFrame长度
    n = dataframe.shape[1]
    # 初始化p值矩阵
    pvalue_matrix = np.ones((n, n))
    # 抽取列的名称
    keys = dataframe.keys()
    # 初始化强协整组
    pairs = []
    # 对于每一个i
    for i in range(n):
        # 对于大于i的j
        for j in range(i+1, n):
            # 获取相应的两只股票的价格Series
            stock1 = dataframe[keys[i]]
            stock2 = dataframe[keys[j]]
            # 分析它们的协整关系
            result = sm.tsa.stattools.coint(stock1, stock2)
            # 取出并记录p值
            pvalue = result[1]
            pvalue_matrix[i, j] = pvalue
            # 如果p值小于0.05
            if pvalue < 0.05:
                # 记录股票对和相应的p值
                pairs.append((keys[i], keys[j], pvalue))
    # 返回结果
    return pvalue_matrix, pairs


# In[3]:


stock_list = ["002142.XSHE", "600000.XSHG", "600015.XSHG", "600016.XSHG", "600036.XSHG", "601009.XSHG",
              "601166.XSHG", "601169.XSHG", "601328.XSHG", "601398.XSHG", "601988.XSHG", "601998.XSHG"]
prices_df = get_price(stock_list, start_date="2014-01-01", end_date="2015-01-01", frequency="daily", fields=["close"])["close"]
pvalues, pairs = find_cointegrated_pairs(prices_df)
sns.heatmap(1-pvalues, xticklabels=stock_list, yticklabels=stock_list, cmap='RdYlGn_r', mask = (pvalues == 1))
print pairs


# In[6]:


stock_df1 = prices_df["601398.XSHG"]
stock_df2 = prices_df["601988.XSHG"]
plot(stock_df1); plot(stock_df2)
plt.xlabel("Time"); plt.ylabel("Price")
plt.legend(["601398.XSHG", "601988.XSHG"],loc='best')


# In[7]:


x = stock_df1
y = stock_df2
X = sm.add_constant(x) 
result = (sm.OLS(y,X)).fit()
print(result.summary())


# In[8]:


fig, ax = plt.subplots(figsize=(8,6))
ax.plot(x, y, 'o', label="data")
ax.plot(x, result.fittedvalues, 'r', label="OLS")
ax.legend(loc='best')


# In[9]:


plot(0.9938*stock_df1-stock_df2);
plt.axhline((0.9938*stock_df1-stock_df2).mean(), color="red", linestyle="--")
plt.xlabel("Time"); plt.ylabel("Stationary Series")
plt.legend(["Stationary Series", "Mean"])


# In[10]:


def zscore(series):
    return (series - series.mean()) / np.std(series)


# In[11]:


plot(zscore(0.9938*stock_df1-stock_df2))
plt.axhline(zscore(0.9938*stock_df1-stock_df2).mean(), color="black")
plt.axhline(1.0, color="red", linestyle="--")
plt.axhline(-1.0, color="green", linestyle="--")
plt.legend(["z-score", "mean", "+1", "-1"])

