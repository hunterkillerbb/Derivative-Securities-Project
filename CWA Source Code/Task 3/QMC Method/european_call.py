import numpy as np

from numpy       import pi, sqrt, log, exp
from scipy.stats import norm

#
# Normal cumulative distribution function, with extension
# for complex argument with small imaginary component
#

def norm_cdf(x):
    if not isinstance(x, np.ndarray):
        xr = x.real
        xi = x.imag
        if abs(xi) > 1.0e-10:
            raise ValueError('imag(x) too large in norm_cdf(x)')

        ncf = norm.cdf(xr)
        if abs(xi) > 0:
            ncf = ncf + 1.0j*xi*norm.pdf(xr)
    else:
        xr = np.real(x)
        xi = np.imag(x)
        if any(abs(xi) > 1.0e-10):
            raise ValueError('imag(x) too large in norm_cdf(x)')

        ncf = norm.cdf(xr)
        if any(abs(xi) > 0):
            ncf = ncf + 1.0j*xi*norm.pdf(xr)

    return ncf
# V = european_call(r,sigma,T,S,K,opt)

#
# Black-Scholes European call option solution
# as defined in equation (3.17) on page 48 of 
# The Mathematics of Financial Derivatives
# by Wilmott, Howison and Dewynne
#
# r     - interest rate
# sigma - volatility
# T     - time interval
# S     - asset value(s)  (float or flattened numpy array)
# K     - strike price(s) (float or flattened numpy array)
# opt   - 'value', 'delta', 'gamma' or 'vega'
# V     - option value(s) (float or flattened numpy array)
#

def european_call(r,sigma,T,S,K,opt):

    S  = S + 1.0e-100     # avoids problems with S=0
    K  = K + 1.0e-100     # avoids problems with K=0

    d1 = ( log(S) - log(K) + (r+0.5*sigma**2)*T ) / (sigma*sqrt(T))
    d2 = ( log(S) - log(K) + (r-0.5*sigma**2)*T ) / (sigma*sqrt(T))

    if opt == 'value':
        V = S*norm_cdf(d1) - exp(-r*T)*K*norm_cdf(d2)
    elif opt == 'delta':
        V = norm_cdf(d1)
    elif opt == 'gamma':
        V = exp(-0.5*d1**2) / (sigma*sqrt(2*pi*T)*S)
    elif opt == 'vega':
        V = S*(exp(-0.5*d1**2)/sqrt(2*pi))*( sqrt(T)-d1/sigma) \
            - exp(-r*T)*K*(exp(-0.5*d2**2)/sqrt(2*pi))*(-sqrt(T)-d2/sigma)

    else:
        raise ValueError('invalid value for opt -- must be "value", "delta", "gamma", "vega"')

    return V

def european_put (r,sigma,T,S,K,opt):

     S  = S + 1.0e-100     # avoids problems with S=0
     K  = K + 1.0e-100     # avoids problems with K=0

     d1 = ( log(S) - log(K) + (r+0.5*sigma**2)*T ) / (sigma*sqrt(T))
     d2 = ( log(S) - log(K) + (r-0.5*sigma**2)*T ) / (sigma*sqrt(T))

     if opt == 'value':
        V = - S*norm_cdf(-d1) + exp(-r*T)*K*norm_cdf(-d2)

     else:
        raise ValueError('invalid value for opt -- must be "value", "delta", "gamma", "vega"')
     
     return V