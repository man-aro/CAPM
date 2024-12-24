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

st.dataframe(CAPM.head())