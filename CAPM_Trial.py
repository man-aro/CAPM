# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 21:46:08 2024

@author: ManishArora
"""


import streamlit as st
import yfinance as yf
import pandas as pd 
import matplotlib.pyplot as plt 
from datetime import datetime
import statsmodels.api as sm 
from statsmodels.regression.rolling import RollingOLS

st.title('Capital Asset Pricing Model')

st.write('DataSource: Yahoo Finance')
st.write('Default Risk-Free Rate: 3-month Treasury Bills.')

stock = st.selectbox("Select a Stock*: ", (' ', 'MSFT', 'AMZN', 'NVDA', 'AMD', 'META'))

market = st.selectbox("Select a Market*: ", (' ', 'S&P 500', 'NASDAQ 100'))




Date_Period = st.slider("Select Period:", value=(datetime(2018, 1, 1), datetime(2024, 11, 30)))


def CAPM_Data(Ticker, Sdate, Edate):
    tick = yf.Ticker(Ticker)
    hist_data =  tick.history(start = Sdate, end = Edate)
    hist_data['Returns'] = hist_data['Close'].pct_change()
    hist_data = hist_data[hist_data['Returns'].notna()]
    hist_data.reset_index(inplace = True)
    hist_data.rename(columns = {'index':'Date'}, inplace = True)
    hist_data['Date'] = hist_data['Date'].dt.strftime('%Y/%m/%d')
    hist_data['Date'] = pd.to_datetime(hist_data['Date']) 
    hist_data = hist_data[['Date', 'Close', 'Returns']]
    hist_data.rename(columns = {'Close': Ticker + '_Close', 'Returns': Ticker + '_Returns'}, inplace = True)
    return hist_data



SDate = Date_Period[0].strftime('%Y-%m-%d')
EDate = Date_Period[1].strftime('%Y-%m-%d')


if stock == ' ' or market == ' ':
    st.write('Please select required fields *')
else: 
    Stock_Data = CAPM_Data(stock, SDate, EDate)
    Stock_Data.drop('Date', inplace = True, axis = 1)
    
    if market == 'S&P 500':
        market_tick = '^GSPC'
        Market = CAPM_Data(market_tick, SDate, EDate)   #S&P 500 
        Market.drop('Date', inplace = True, axis = 1)
    elif market == 'NASDAQ 100':
        market_tick = '^NDX'
        Market = CAPM_Data(market_tick, SDate, EDate)   #NASDAQ 100
        Market.drop('Date', inplace = True, axis = 1)
     
    TBills = CAPM_Data('^IRX', SDate, EDate)   #3-month t-bills
    TBills['Rate'] = TBills['^IRX_Close']/100
    TBills = TBills[['Date', 'Rate']]
    CAPM = pd.concat([Stock_Data, Market, TBills], axis = 1)
    
    CAPM = pd.concat([Stock_Data, Market, TBills], axis = 1)
    CAPM['Rm-Rf'] = CAPM[market_tick + '_Returns'] - CAPM['Rate']
    CAPM['R_' + stock + '-Rf'] = CAPM[stock + '_Returns'] - CAPM['Rate']
    
    
    
    #CAPM Regression
    
    Y = CAPM['R_' + stock + '-Rf']
    X = CAPM['Rm-Rf']
    
    X = sm.add_constant(X)
    
    regression_model = sm.OLS(Y, X)
    results = regression_model.fit()
    
    Parameters = results.params
    P_values = results.pvalues
    
    if P_values[0] < 0.01:
        sig_alpha = '(*)'
    elif (P_values[0] < 0.05) & (P_values[0] >= 0.01):
        sig_alpha = '(**)'
    elif (P_values[0] < 0.10) & (P_values[0] >= 0.05):
        sig_alpha = '(***)'
    else:
        sig_alpha = '(-)'
    

    if P_values[1] < 0.01:
        sig_beta = '(*)'
    elif (P_values[1] < 0.05) & (P_values[1] >= 0.01):
        sig_beta = '(**)'
    elif (P_values[1] < 0.10) & (P_values[1] >= 0.05):
        sig_beta = '(***)'
    else:
        sig_beta = '(-)'
    
    st.write('CAPM Results over Sample Period')
    st.write('Alpha =  ' + str(round(Parameters[0],3)) + sig_alpha)
    st.write('Beta =  '+ str(round(Parameters[1],3)) + sig_beta)
    
    
    #Rolling Regression
    window_size = st.selectbox("Select a Window Size (days)*: ",(' ', '30', '60'))
    st.write("Window size determines the number of historical observations (days) from which information is considered.")
    
    sig_level = st.selectbox("Select a Level of Significance (%)*: ", (' ', '10%', '5%', '1%'))

    if window_size == ' ' or sig_level == ' ':
        st.write('Please select required fields *')
    else: 
        if sig_level == '10%':
            sig= 0.1
        elif sig_level == '5%':
            sig = 0.05
        elif sig_level == '1%': 
            sig = 0.01
    
        Y = CAPM['R_' + stock + '-Rf']
        X = CAPM['Rm-Rf']    
        X = sm.add_constant(X)
        mod = RollingOLS(Y, X, window = int(window_size)) 
        rolling_reg = mod.fit()
        params  = rolling_reg.params.copy() #Copies parameters to DataFrame
        conf_int = rolling_reg.conf_int(alpha = sig)
        p_values = rolling_reg.p_values(alpha = sig)
    
    
    #Concat: This is possible as all three dataframes (params, conf_int, CAPM) have the same date on the same index.
        Parameters_Rolling = pd.concat([params, conf_int], axis = 1)
        Parameters_Rolling.rename(columns = {'const':'Alpha', 'Rm-Rf':'Beta', ('const', 'lower'):'Alpha_lower',('const', 'upper'): 'Alpha_upper',('Rm-Rf', 'lower'):'Beta_Lower', ('Rm-Rf', 'upper'):'Beta_Upper'}, inplace = True)
        Parameters_Rolling['Date'] = CAPM['Date']
        
        fig, ax = plt.subplots(2, figsize = (15, 6)) #indicate that there are two subplots
        ax[0].plot(Parameters_Rolling['Date'], Parameters_Rolling['Beta_Lower'], label  = 'L_CI', color = 'violet', linestyle = '--')
        ax[0].plot(Parameters_Rolling['Date'], Parameters_Rolling['Beta'], label  = 'Beta', color = 'indigo')
        ax[0].plot(Parameters_Rolling['Date'], Parameters_Rolling['Beta_Upper'], label  = 'U_CI', color = 'violet', linestyle = '--')
        ax[0].legend(loc = 1)
        
        ax[1].set_xlabel('Date', fontsize  = 10)
        ax[0].set_title(stock + ': Rolling Beta and Alpha (' + window_size + ' days)')
        ax[1].plot(Parameters_Rolling['Date'], Parameters_Rolling['Alpha_lower'], label  = 'L_CI', color = 'skyblue', linestyle = '--')
        ax[1].plot(Parameters_Rolling['Date'], Parameters_Rolling['Alpha'], label  = 'Alpha', color = 'navy')
        ax[1].plot(Parameters_Rolling['Date'], Parameters_Rolling['Alpha_upper'], label  = 'U_CI', color = 'skyblue', linestyle = '--')
        ax[1].legend(loc = 1)
        
        st.pyplot(fig)