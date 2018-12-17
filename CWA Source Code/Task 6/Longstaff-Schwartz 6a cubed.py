import numpy as np  
import pandas as pd  
from scipy.stats import norm 
import matplotlib.pyplot as plt
import statsmodels.api as sm

S = np.transpose(np.array(pd.read_csv('longsch.csv')))


S0 = 30
r = 0.01
sigma = 0.3
T = 2.0
I = 200
K = 35
interval = 504
dt = T/interval
intercept, b1, b2,b3= 0,0,0,0

#S = np.zeros((interval + 1,I))
F = np.zeros((interval+ 1 ,I))
temp = np.zeros((interval+1,I)) 


#set = []    
F[0] = 0
S[0] = S0                                            
average = 0 

#for t in range(1,interval+1):
    #for i in range(1,I+1):
        #S[t][i-1]= S[t-1][i-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*np.random.standard_normal(size = None))

for t in range(1,interval+1):
    for i in range(1,I+1):
        F[t][i-1]= np.maximum(K- S[interval][i-1],0)*np.exp(-r*dt*(interval-t)) 
        

             
           
          
for m in range(1,interval+1):
    
    for i in range(1,I+1):

        model = sm.OLS(np.exp(-r*dt*m)*(K-S[interval]), np.insert(np.column_stack((S[-m-1],S[-m-1]**2,S[-m-1]**3)), 0, 1, axis = 1)) 
        
        
        if  S[-m-1][i-1] == 0 or np.maximum(K-S[-m-1][i-1],0) == 0:
            intercept,b1,b2,b3 =0,0,0,0
            
        else: 
            intercept, b1, b2,b3 = model.fit().params 
                
                               
    temp[-m-1][i-1] = intercept * 1 + b1*S[-m-1][i-1] + b2 * S[-m-1][i-1]**2 +b3*  S[-m-1][i-1]**3   
                                                            
    if temp[-m-1][i-1] < K-S[-m-1][i-1]:
        F[-m-1][i-1] = K-S[-m-1][i-1]
            
#for k in range(1,interval+1)
F[0] = F[1]*np.exp(-r*dt)  

average = np.average(F[0])


plt.figure(figsize = (9,6))
plt.plot(F,lw=0,marker = '.',markersize='2',alpha=1 )
#plt.title('Longstaff-Schwartz--cubed' )
#plt.plot(F,lw=0,marker = '.',markersize='2',alpha=1 )

plt.rcParams['savefig.dpi'] =300
plt.rcParams['figure.dpi'] =300
plt.show()

#F = F.tolist()
#F_df = pd.DataFrame(F)
#writer = pd.ExcelWriter('MC lngstaff-schwartz squared.xlsx')
#F_df.to_excel(writer,'Simulation6A') 
#writer.save()  