"""
Created on Fri Apr 14 11:38:40 2023

@author: SEB
"""
from matplotlib import pyplot
from statsmodels.tsa.stattools import adfuller 
import pandas as pd 

def subplots_byserie(df,series,name):
    
    print("el numero de plots sera de "+str(len(series)))
    
    if len(series)>1:    
        fig, ax = pyplot.subplots(nrows=len(series), figsize=(12,len(series)*3.5))    
        for x in series:
            ind = series.index(x)
            print(x)
            filt = df['serieID'] == x  
            ax[ind].plot(df.loc[filt]['Date'],df.loc[filt]['obsValue'])
            ax[ind].set_title(x, size=25) 
            ax[ind].set_ylabel('Obs Value', size=15) 
            
            pyplot.tight_layout()
            
        pyplot.savefig(name+'.png')
        
    else:
        filt = df['serieID'] == series[0]  
        print (series[0] )
        fig = pyplot.figure(1)
        pyplot.plot(df.loc[filt]['Date'],df.loc[filt]['obsValue'])
        pyplot.title(series[0] , fontsize='25') 
        pyplot.ylabel('Obs Value', fontsize='15') 
        pyplot.tight_layout()
        pyplot.savefig(name+'.png')
        
        

def adfuller_test(series, signif=0.05):
        """
        Perform Augmented Dickey-Fuller to test for Stationarity of the given series
        and print report. Null Hypothesis: Data has unit root and is non-stationary.
        
        series: time series in pd.Series format
        signif: significance level for P-value to reject Null Hypothesis
        """
        x = adfuller(series, autolag='AIC')
        
        if (x[1]<signif):
            isStationary = True
        else:
            isStationary = False
        
    
        #using dictionary saves different data types (float, int, boolean)
        output = {'Test Statistic': x[0], 
                  'P-value': x[1], 
                  'Number of lags': x[2], 
                  'Number of observations': x[3],
                  f'Reject (signif. level {signif})': x[1] < signif,
                  'Es estacionaria':isStationary}
    
        for key, val in x[4].items():
             output[f'Critical value {key}'] = val
    
        return pd.Series(output)
            
