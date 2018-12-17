import numpy as np  
import pandas as pd  
from scipy.stats import norm 
np.random.seed(12345)
import matplotlib.pyplot as plt

S0 = 30
r = 0.01
sigma = 0.3
T = 2.0
I = 501 
interval = 504 #simulation numbers 
dt = T/interval
N = 50400 
L = N/interval

S = np.zeros((interval + 1,I))
S[0] = S0
for m,t in zip(range(1,interval+1),range(1,interval+1)):
     U = (m - 1 + np.random.rand())/interval
     Y = norm.ppf(U)
     S[t] = S[t-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*Y)


plt.plot(S[:,:],lw = 0.5,Marker ='*',markersize = '3')
plt.title('Stratified 3a')
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.dpi'] =300
plt.show()



     
#F =np.zeros((interval+1,I))  F[t] = (K -S[t])*np.exp(-r*dt*t)

#plt.subplot(2,1,1)
#plt.plot(S[:,:],lw = 1.1)
#plt.xlabel('fig.1')
#plt.title('Stock price')


#plt.subplots_adjust(hspace = 0.7)
#plt.rcParams['savefig.dpi'] =300
#plt.rcParams['figure.dpi'] =300



#plt.hist(S[-1],bins = 50)
#plt.xlabel('price')
#plt.ylabel('frequency')
#plt.show()

#plt.figure(figsize = (10,6))
#plt.plot(S[:,:],lw = 1.5)
#plt.xlabel('time')
#plt.ylabel('price')
#plt.rcParams['savefig.dpi'] = 300
#plt.show()
 
#plt.rcParams['figure.dpi'] = 300 
