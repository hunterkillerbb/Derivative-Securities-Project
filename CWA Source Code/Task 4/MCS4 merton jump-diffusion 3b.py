import numpy as np  
import pandas as pd  
from scipy.stats import norm 
import matplotlib.pyplot as plt

S0 = 30
r = 0.01
sigma = 0.3
T = 2.0
I = 1000
interval = 504
Lambda= 0.4 
a,b= 0.2,0.2
dt = T/interval
K = 35

Z_1 = np.random.normal(size=[interval + 1,I])
Z_2 = np.random.normal(size=[interval + 1,I])
Poisson = np.random.poisson(Lambda*dt, [interval + 1,I])
F = np.zeros((interval +1,I))
S = np.zeros((interval +1,I))
S[0] = S0
F[0] = K - S0

for t in range(1,interval+1):
    for i in range(1,I+1):
         if S[t-1][i-1]<28:
                S[t][i-1]=0
                F[t][i-1]=0
         elif S[t-1][i-1]>=28:
            
            S[t][i-1]= S[t-1][i-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*Z_1[t-1][i-1]+a*Poisson[t-1][i-1]+ np.sqrt(b**2)*np.sqrt(Poisson[t-1][i-1]*Z_2[t-1][i-1]))
            F[t][i-1] = np.maximum(K - S[t][i-1],0)*np.exp(-r*dt*t) 
            
            
 

#plt.hist(ST1,bins = 50)
#plt.xlabel('price')
#plt.ylabel('ferquency')
        
plt.subplot(2,1,1)
plt.plot(S[:,:],lw = 1.1)
plt.title('Stock price')

plt.subplot(2,1,2)
plt.title('Option price')
plt.plot(F[interval],lw = 0,alpha=1,marker='.',markersize='2')

plt.subplots_adjust(hspace = 0.5)
plt.rcParams['savefig.dpi'] =300
plt.rcParams['figure.dpi'] =300
plt.show()

#F = F.tolist()
#F_df = pd.DataFrame(F)
#writer = pd.ExcelWriter('MC simulation4A.xlsx')
#F_df.to_excel(writer,'simulation4A') # 
#writer.save()





