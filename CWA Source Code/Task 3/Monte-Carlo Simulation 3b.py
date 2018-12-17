import numpy as np  
import pandas as pd  
from scipy.stats import norm 
import matplotlib.pyplot as plt

S0 = 30
r = 0.01
sigma = 0.3
T = 2.0
I = 5000
K =35

interval = 504
dt = T/interval
S = np.zeros((interval + 1,I))
F= np.zeros((interval + 1,I))
S[0] = S0


for t in range(1,interval+1):
    for i in range(1,I+1):
        if S[t-1][i-1]<28:
            S[t][i-1]=0
            F[:,i-1]=0
            
            
        elif S[t-1][i-1]>=28 :
            
            S[t][i-1]= S[t-1][i-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*np.random.standard_normal(size = None))
            F[t][i-1]= np.maximum(K- S[t][i-1],0)*np.exp(-r*dt*t)
            

plt.subplot(2,1,1)
plt.plot(S[:,:],lw = 0.5)
plt.title('Stock price')


plt.subplot(2,1,2)
plt.plot(F,marker='.',markersize= '0.8',alpha=0.8  ,lw = '0')
plt.title('Option price')
plt.hlines(30,0,5000,color ='red',linestyle='--')

plt.subplots_adjust(hspace = 0.5)

plt.rcParams['savefig.dpi'] =300
plt.rcParams['figure.dpi'] =300

plt.show()
            
       
#F = F.tolist()
#F_df = pd.DataFrame(F)
#writer = pd.ExcelWriter('MC simulation3B comparison.xlsx')
#F_df.to_excel(writer,'Simulation3B') # float_format 
#writer.save()
