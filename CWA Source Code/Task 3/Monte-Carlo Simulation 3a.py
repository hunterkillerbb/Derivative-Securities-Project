import numpy as np  
import pandas as pd  
from scipy.stats import norm 
import matplotlib.pyplot as plt
import seaborn as sns

S0 = 30
r = 0.01
sigma = 0.3
T = 2.0
I = 5000
interval = 504
dt = T/interval

S = np.zeros((interval + 1,I))
F = np.zeros((I,))
K = 35

S[0] = S0

for t in range(1,interval+1):
    S[t] = S[t-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*np.random.standard_normal(I))

F = np.maximum(K - S[interval],0)*np.exp(-r*T)



plt.subplot(2,1,1)
plt.plot(S[:,:],lw = 0.5)
plt.title('Stock price--Plain vanilla option')


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
#writer = pd.ExcelWriter('MC simulation3A comparison.xlsx')
#F_df.to_excel(writer,'Simulation3A') # float_format 
#writer.save()