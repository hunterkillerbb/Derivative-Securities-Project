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
dt = T/interval
Lambda= 0.4 
a,b= 0.2,0.2  
K = 35 

Z_1 = np.random.normal(size=[interval + 1,I])
Z_2 = np.random.normal(size=[interval + 1,I])
Poisson = np.random.poisson(Lambda*dt, [interval + 1,I])
S = np.zeros((interval + 1,I))
F = np.zeros((interval+1,I))
S[0] = S0
F[0] = K - S0

for t in range(1,interval+1):

    S[t] = S[t-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*Z_1[t-1]+a*Poisson[t-1]+np.sqrt(b**2)*np.sqrt(Poisson[t-1])*Z_2[t-1])
    F[t] = np.maximum(K - S[t],0)*np.exp(-r*dt*t) 

#plt.hist(S[-1],bins = 50)
#plt.xlabel('price')
#plt.ylabel('frequency')
#plt.show()


#plt.subplot(2,1,1)
#plt.plot(S[:,:],lw = 1.1)
#plt.title('Stock price')

#plt.subplot(2,1,2)
#plt.plot(F[interval],marker='.',markersize= '0.8',alpha=0.6  ,lw = '0')
#plt.title('Option price')
#plt.hlines(30,0,5000,color ='red',linestyle='--')

#plt.subplots_adjust(hspace = 0.5)

#plt.rcParams['figure.dpi'] =300
#plt.rcParams['savefig.dpi'] =300
#plt.show()


F = F.tolist()
F_df = pd.DataFrame(F)
writer = pd.ExcelWriter('MC simulation4A comparison.xlsx')
F_df.to_excel(writer,'simulation4A') # 
writer.save()