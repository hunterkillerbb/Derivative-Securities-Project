import matplotlib.pyplot as plt
import numpy             as np
np.random.seed(12345678)
from numpy.random import randn
from numpy import ones, zeros, sqrt, exp, log2
from scipy.stats import norm
from european_call import european_put 
from bb import bb
from sobol import sobol, scramble 

#
# Test weak convergence of Euler method for 
# European put option using Sobol points
#
# Test problem:   dS   = r*S dt + sig*S dW
#

plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=16)

plt.close("all")
plt.ion()

#
# problem parameters and exact solution
#

r   = 0.01 
sig = 0.3 
T   = 2. 
S0  = 30.
K   = 35.

Ms   = zeros((11,))
err1 = zeros((11,))
err2 = zeros((11,))

Ve  = european_put(r,sig,T,S0,K,'value')

for it in range(1,4):

    #
    # Quasi-Monte Carlo simulation comparing to exact solution
    #

    N  = 128   # number of timesteps
    M2 = 64    # number of scrambles

    h  = T/N

    for p in range(2,13):
        print(p)
        M = 2**p  # number of paths in each "family"
        unscrambled = sobol(m=p, s=N, scramble=False)

        sum1 = 0.
        sum2 = 0.

        for m in range(1,M2+1):
            #
            # Sobol quasi-random number generation with scrambling,
            # and Brownian Bridge construction of Brownian increments
            #
            if it==1:
                U = scramble(unscrambled).T
                Z  = norm.ppf(U)
                dW = bb(Z,T)

            #
            # Sobol quasi-random number generation with scrambling,
            # but no Brownian Bridge construction of Brownian increments
            #
            elif it==2:
                U = scramble(unscrambled).T
                Z  = norm.ppf(U)
                dW = sqrt(h)*Z

            #
            # alternative standard random number generation
            #
            else:
                dW = sqrt(h)*randn(N,M)

            S = S0*ones((M,))                          # M是每个家族中paths的数量，N 是intervals

            for n in range(N):
                S  = S*(1+r*h+sig*dW[n,:])                

            P = exp(-r*T)*np.maximum(K-S,0.)
            P = np.sum(P)/M

            sum1 = sum1 + np.sum(P)
            sum2 = sum2 + np.sum(P**2)

        V  = sum1/M2
        sd = sqrt((sum2/M2 - (sum1/M2)**2)/(M2-1))

        Ms[p-2]   = M
        err1[p-2] = V-Ve
        err2[p-2] = 3*sd

    plt.figure()
    plt.loglog(Ms,abs(err1),'b-*',Ms,err2,'r-*')
    plt.xlabel('N'); plt.ylabel('Error')
    plt.legend((' Error',' MC error bound'), loc='upper right', fontsize=14)
    plt.axis([1, 4096, 0.005, 10])
    if   it==1:
        plt.title('comparison to exact solution')
        
    elif it==2:
        plt.title('comparison to exact solution')
        
    else:
        plt.title('comparison to exact solution')

    #plt.plot(S[:,:])
        

# python2.7 and python3 compatibility
if hasattr(__builtins__, 'raw_input'):
    raw_input("Press Enter to continue...")
else:
    input("Press Enter to continue...")
