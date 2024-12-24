# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 21:46:08 2024

@author: ManishArora
"""

import streamlit as st
import yfinance as yf
import pandas as pd 
import matplotlib.pyplot as plt 

st.title('Capital Asset Pricing Model')

st.write('DataSource: Yahoo Finance')

stock = st.selectbox("Select a Stock*: ", (' ', 'MSFT', 'AMZN', 'NVDA', 'AMD', 'META'))