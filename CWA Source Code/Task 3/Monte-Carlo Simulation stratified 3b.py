import numpy as np  
import pandas as pd  
from scipy.stats import norm 
import matplotlib.pyplot as plt

S0 = 30
r = 0.01
sigma = 0.3
T = 2.0
I = 10
interval = 504
K =35

dt = T/interval
S = np.zeros((interval + 1,I))
F = np.zeros((interval+1,I))
S[0] = S0
N = 50400 
L = N/interval

for t,m in zip(range(1,interval+1),range(1,interval+1)):
    for i in range(1,I):
                U = (m - 1 + np.random.uniform(1,int(L),1))/interval
                Y = norm.ppf(U)
                if S[t-1][i-1]<28:
                      S[t][i-1]=0
                      #F[t][i-1]=0
                elif S[t-1][i-1]>=28:
                    S[t][i-1]=S[t-1][i-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*Y)
                    #F[t][i-1] = (K - S[t][i-1])*np.exp(-r*dt*t)
        
        
pic = plt.figure(figsize = (1,3))
plt.plot(F[:,:],lw = 0, marker = '.',markersize= '2')
plt.title('Option price 3b stratified')
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.dpi']=300
plt.show(pic)
          
      
#plt.hist(ST1,bins = 50)
#plt.xlabel('price')
#plt.ylabel('ferquency')np.random.standard_normal(size = None)








