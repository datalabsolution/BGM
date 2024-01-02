# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 13:31:54 2022

@author: USER
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import yfinance as yf
import streamlit as st 
import plotly.graph_objects as go

fmp_api_key = "e3e1ef68f4575bca8a430996a4e11ed1"


@st.cache_data
def load_yield():
    # 获取AAA_Effective_Yield
    response = requests.get("https://ycharts.com/indicators/us_coporate_aaa_effective_yield" ,headers=headers)
    soup = BeautifulSoup(response.text,"html.parser")
    AAA_Effective_Yield = float(soup.find_all("td",{"class":"col-6"})[5].text.replace("%", ""))
    
    return(AAA_Effective_Yield)

@st.cache_data  # 使用新的缓存装饰器
def load_stock_data(stock_code):

    # 获取价格
    stock_price = yf.download(stock_code, period="3y")
    price = round(stock_price["Close"][-1], 2)        

    return price, stock_price

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
df_bgm = pd.DataFrame()
sheet_id ="1--_yA87vC8YgxiwgQ_dR_SbWlIDUl9yf"
trickers_eps = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")

# find the positive eps
positive_df = trickers_eps[(trickers_eps['EPS'] > 0) & (trickers_eps['Growth'] > 0)]
tickers = positive_df["Ticker"].to_list()
st.title('Benjamin Graham model (BGM)')


# 使用函数获取数据
AAA_Effective_Yield = load_yield()

# Display on web app
code_Average_Yield_AAA = f"AAA級公司債券的有效收益率 (US Corporate AAA Effective Yield): {AAA_Effective_Yield}"
st.code(code_Average_Yield_AAA, language='python')

# Assuming 'tickers' is your list of ticker symbols
tickers = sorted(tickers)
stock_code = st.selectbox(f'選擇股票: ({len(tickers)})', tickers)


stock_data = load_stock_data(stock_code)
col1, col2= st.columns([2,1])
with col1:
    company_name = positive_df["Company"][positive_df["Ticker"] == stock_code].values[0]
    st.text(f"公司: {company_name}")

with col2:
    
    price = stock_data[0]
    print_price = f"股價: {price}"
    st.code(print_price)
    


stock_data = load_stock_data(stock_code)
Grown = positive_df["Growth"][positive_df["Ticker"] == stock_code].values[0]
eps = positive_df["EPS"][positive_df["Ticker"] == stock_code].values[0]
price = stock_data[0]
stock_price= stock_data[1]
company_name = positive_df["Company"][positive_df["Ticker"] == stock_code].values[0]

col1, col2= st.columns([1,1])
with col1:
    eps = st.number_input("每股盈利 (EPS) - 五年平均", value=eps, step=0.01, format="%.2f")
    Grown = st.number_input(f"後五年增長(Next 5 Years) - 每年", value=Grown, step=0.01, format="%.2f")
with col2:
    grown_mult = st.number_input("增長倍數 (Growth multiplier)", value=1.0, step=0.1, format="%.1f")    
    PE_zone = st.number_input("零增長股票P/E (Zero-growth stock P/E )", value=7.0, step=0.1, format="%.1f")
    

markdown_text = f'<p style="font-size: 10px;">intrinsic value (BGM) = EPS x ({PE_zone} + {round(grown_mult,1)} x g) x 4.4/Y</p>'
st.markdown(markdown_text, unsafe_allow_html=True)
BGM_value = round((eps * (PE_zone + grown_mult *Grown)* 4.4)/AAA_Effective_Yield,2)    
st.code(f"BGM 數值: {BGM_value}", language='python')
Margin_of_safty = st.slider("安全網 (Margin of safty)", min_value=0.5, max_value=1.0, value=0.8, step=0.05)
New_BGM = round(BGM_value *Margin_of_safty,2)
st.code(f"BGM 數值 (安全網): {New_BGM}", language='python')
    
    
stock_price["Date"] = stock_price.index
stock_price.reset_index(inplace=True, drop=True)
# stock_price
# st.dataframe(stock_price)
fig = go.Figure()
fig.add_trace(go.Candlestick(x=stock_price["Date"], open=stock_price["Open"], high=stock_price["High"], low=stock_price["Low"], close=stock_price["Close"]) )
fig.add_hline(y=BGM_value, line_dash="dot" , annotation_text=f"BGM Value: {BGM_value}")
fig.add_hline(y=New_BGM , annotation_text=f"Margin_of_safty: {New_BGM}")
st.plotly_chart(fig)

st.markdown('<p style="font-size: 10px;">數據來源自Financial Modeling Prep 和 Yahoo Finance</p>', unsafe_allow_html=True)


