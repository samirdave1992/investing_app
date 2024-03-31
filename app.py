import streamlit as st
import pandas as pd
import time
import yfinance as yf
import time
import numpy as np
import datetime
from datetime import datetime
from datetime import date
import re
from datetime import timedelta

import plotly.graph_objects as go
import plotly.express as px



# import warnings
# from mitosheet.streamlit.v1 import spreadsheet
# from mitosheet.streamlit.v1.spreadsheet import _get_mito_backend

import requests

pd.options.display.max_rows = 100


st.set_page_config(layout='wide')


page=st.sidebar.radio(
    "Choose from the following options:",
    ("Top Investor's holdings","Grand Portfolio of Investors:$932 B",'SMA Strategy'))

today=datetime.today().strftime("%Y-%m-%d")


@st.cache_data(experimental_allow_widgets=True)
def insights(df):
    current_date=(datetime.now().year)
    last_5_year=current_date-5
                
    current_year_data=df[df['Date']>=f"{current_date}-01-01"]
    price1=current_year_data['Close'].iloc[0].round(2)
    price2=current_year_data['Close'].iloc[-1].round(2)
    pct=(price2-price1)/price1
    pct="{:.2%}".format(pct)

    #5 year RR
    last_5_year=current_date=(datetime.now().year)-5
    last_5_year_data=df[df['Date']>=f"{last_5_year}-01-01"]
    five_year_price1=last_5_year_data['Close'].iloc[0].round(2)
    five_year_price2=last_5_year_data['Close'].iloc[-1].round(2)

    five_year_pct=(five_year_price2-five_year_price1)/five_year_price1
    five_year_pct="{:.2%}".format(five_year_pct)
    # five_year_pct="{:.2%}".format(pct)

    return price1,price2,pct,five_year_pct,five_year_price1,five_year_price2


###
if page=="Top Investor's holdings":


    st.title("Invest like the Bulls of our time")

    st.markdown("""
    ### By selecting the Investor, you will be able to get details of their holdings.

    1. Michael Burry - Scion Asset Management   [:link:](https://en.wikipedia.org/wiki/Michael_Burry)
    2. Warren Buffet - Berkshire Hathaway  [:link:](https://en.wikipedia.org/wiki/Warren_Buffett)
    3. Bill & Melinda Gates Foundation  [:link:](https://en.wikipedia.org/wiki/Bill_%26_Melinda_Gates_Foundation)
    4. Bill Ackman - Pershing Square Capital Management [:link:]""",unsafe_allow_html=True)



    investor_dict={"Michael Burry":"https://www.dataroma.com/m/holdings.php?m=SAM",
                    "Warren Buffet":"https://www.dataroma.com/m/holdings.php?m=BRK",
                    "Bill & Melinda Gates Foundation":"https://www.dataroma.com/m/holdings.php?m=GFT",
                    "Bill Ackman":"https://www.dataroma.com/m/holdings.php?m=psc"}
#    st.write(investor_dict.get('Michael Burry'))

###

    # def insights(df):
    #     current_date=(datetime.now().year)
    #     last_5_year=current_date-5
                    
    #     current_year_data=df[df['Date']>=f"{current_date}-01-01"]
    #     price1=current_year_data['Close'].iloc[0].round(2)
    #     price2=current_year_data['Close'].iloc[-1].round(2)
    #     pct=(price2-price1)/price1
    #     pct="{:.2%}".format(pct)

    #     #5 year RR
    #     last_5_year=current_date=(datetime.now().year)-5
    #     last_5_year_data=df[df['Date']>=f"{last_5_year}-01-01"]
    #     five_year_price1=last_5_year_data['Close'].iloc[0].round(2)
    #     five_year_price2=last_5_year_data['Close'].iloc[-1].round(2)

    #     five_year_pct=(five_year_price2-five_year_price1)/five_year_price1
    #     five_year_pct="{:.2%}".format(five_year_pct)
    #    # five_year_pct="{:.2%}".format(pct)

    #     return price1,price2,pct,five_year_pct,five_year_price1,five_year_price2

###
    with st.form('form'):
        investors=st.selectbox('Pick an Investor/HedgeFund',['Michael Burry','Warren Buffet','Bill & Melinda Gates Foundation','Bill Ackman'])

        submit=st.form_submit_button('submit')

        if submit:
        #    @st.cache(allow_output_mutation=True)
            def fetching_stock_data(investor=investors):
                headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
                }

                url=investor_dict.get(f"{investor}")

                r = requests.get(url, headers=headers)
                c = r.content

                df=pd.read_html(c,match='Stock')
                df=df[0]
                df['Ticker']=df.Stock.str.extract('(.*)- ', expand=False)
                df['Ticker'] = df['Ticker'].str.replace('.','-')
                df = df.rename(columns={"""% of Portfolio""": 'percentage_of_portfolio',"""ReportedPrice*""": 'reported_price'})
                df=df[["Stock","Ticker","percentage_of_portfolio","RecentActivity","Shares","reported_price","Value","Current Price","52Week Low","52Week High"]]

                #df=df[["Stock","Ticker"]]
              #  df['Ticker'] = df['Ticker'].str.replace('.','-')

                return df.head()


            st.write(fetching_stock_data(investor=investors))

            visual_data=fetching_stock_data(investor=investors)

###
            def generating_visuals(visual_data):
                viz=[]
                for index,row in visual_data.iterrows():

                    data=(yf.download(
                    tickers = row['Ticker'],

                    # What period of time are we interested in?
                    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                    # In our case we will choose 10y
                    period = "5y",

                    # Next we need to define our interval.
                    interval = "1d",

                    # Ensure our data is grouped properly.
                    group_by = 'ticker'
                    ))
                    columns = ["Date","Close"]
                    data=data[['Close']]
                    data.rename(index={1: 'a'},inplace=True)
                    data['SMA_50'] = data['Close'].rolling(5).mean().shift()
                    data['SMA_200'] = data['Close'].rolling(10).mean().shift()

                    

                    prev_close=data['Close'].max()

                #    st.write(f"{row['Ticker']}")
                    st.write(f"{row['Stock']}")
                    
                    new=data.reset_index()

                 #   st.write(data)

                    new['Date'] = pd.to_datetime(new['Date']).dt.date
                    new["Date"] = pd.to_datetime(new["Date"])

                    minimum,maximum,YTD,five_year_RTD,five_year_p1,five_year_p2=insights(new)
                    difference=maximum-minimum
                    five_year_difference=five_year_p2-five_year_p1

                    col1,col2,col3 = st.columns([1,1,1]) 

                    with col1:
                        st.metric("Previous Day Close", "$" + str(prev_close.round(2)))
                    with col2:
                        st.metric("YTD return and difference", str(YTD),difference.round(2))
                    with col3:
                        st.metric("Five year Return-Rate and difference", five_year_RTD,five_year_difference.round(2))


            st.write(generating_visuals(visual_data))



elif page=="Grand Portfolio of Investors:$932 B":
   
    top_holdings_url="https://www.dataroma.com/m/g/portfolio.php?o=c"

    st.markdown("## This view shows top 100 stocks owned by most Investors.")
    st.markdown("[Data source Link](https://www.dataroma.com/m/g/portfolio.php)")


    def fetching_top_holdings_stock_data():
        headers = {
                     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
                 }
        
        r = requests.get(top_holdings_url, headers=headers)
        c = r.content

       # pd.set_option('max_rows',500)

        df=pd.read_html(c)
        df=df[0]



        df['Ticker']=df.Stock.str.extract('(.*)- ', expand=False)
        df['Ticker'] = df['Ticker'].str.replace('.','-')
        #df = df.rename(columns={"""% of Portfolio""": 'percentage_of_portfolio',"""ReportedPrice*""": 'reported_price'})
        #df=df[["Stock","Ticker","percentage_of_portfolio","RecentActivity","Shares","reported_price","Value","Current Price","52Week Low","52Week High"]]

        #df=df[["Stock","Ticker"]]
        #  df['Ticker'] = df['Ticker'].str.replace('.','-')

        return df
    

    st.write(fetching_top_holdings_stock_data())

    visuals_data=fetching_top_holdings_stock_data()

    visuals_data['Symbol'] = visuals_data['Symbol'].str.replace('.','-')

    def generating_visuals_main(visuals_data):
        viz=[]
        for index,row in visuals_data.iterrows():

            data=(yf.download(
            tickers = row['Symbol'],

            # What period of time are we interested in?
            # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            # In our case we will choose 10y
            period = "5y",

            # Next we need to define our interval.
            interval = "1d",

            # Ensure our data is grouped properly.
            group_by = 'ticker'
            ))
            columns = ["Date","Close"]
            data=data[['Close']]
            data.rename(index={1: 'a'},inplace=True)
            data['SMA_50'] = data['Close'].rolling(5).mean().shift()
            data['SMA_200'] = data['Close'].rolling(10).mean().shift()

            

            prev_close=data['Close'].max()

        #    st.write(f"{row['Ticker']}")
            st.write(f"{row['Stock']}")
            
            new=data.reset_index()

            #   st.write(data)

            new['Date'] = pd.to_datetime(new['Date']).dt.date
            new["Date"] = pd.to_datetime(new["Date"])

            minimum,maximum,YTD,five_year_RTD,five_year_p1,five_year_p2=insights(new)
            difference=maximum-minimum
            five_year_difference=five_year_p2-five_year_p1

            col1,col2,col3 = st.columns([1,1,1]) 

            with col1:
                st.metric("Previous Day Close", "$" + str(prev_close.round(2)))
            with col2:
                st.metric("YTD return and difference", str(YTD),difference.round(2))
            with col3:
                st.metric("Five year Return-Rate and difference", five_year_RTD,five_year_difference.round(2))


    st.write(generating_visuals_main(visuals_data))

elif page=="SMA Strategy":
    st.subheader("Running SMA 50 and 200 strategy on top 10 S&P 500 holdings 📈 ")


    def top_10_SPY():
        table=pd.read_html('https://www.investopedia.com/articles/investing/122215/spy-spdr-sp-500-trust-etf.asp')
        df = table[0]
        df.reset_index(inplace=True)
        df.columns=['id','company','pct']
        df['company']=df['company'].str.replace('.','-')
        ticker=[]
        for data in df['company']:
            ticker.append(re.search('\(([^)]+)', data).group(1))

        return df[['company','pct']],ticker
    
    top_10,tickers=top_10_SPY()

    st.write("Top 10 SPY tickers and holdings:",top_10)



    df=yf.download(tickers,start='2021-01-01',end=today)

    data=pd.DataFrame(df.Close)

    



    @st.cache_data(experimental_allow_widgets=True)
    def SMA(data):

        sma_s=50
        sma_l=200
    
        for i in (data.columns):
            st.write(f"Trends for {i}")
            trends=data[i]
         #   trend_d.append(data[i])
            trends=pd.DataFrame(trends)
            trends.columns=['close']


            trends['sma_s']=trends.close.rolling(sma_s).mean()
            trends['sma_l']=trends.close.rolling(sma_l).mean()
            trends['position']=np.where(trends['sma_s']>trends['sma_l'],1,-1) #position to buy and sell 

            #Buy and Hold
            trends['returns']=np.log(trends.close.div(trends.close.shift(1)))

            #Strategy
            trends['strategy']=trends.position.shift(1)*trends['returns']

            #For  1 $ invested
            buy_hold_retuns1dlr=trends[['returns']].sum().apply(np.exp)  
            strategy_returns=trends[['strategy']].sum().apply(np.exp)   
           
            #Exponential returns
            trends['c_returns']=trends['returns'].cumsum().apply(np.exp)
            trends['c_strategy']=trends['strategy'].cumsum().apply(np.exp)
            #st.write(trends)
          #  st.write(buy_hold_retuns1dlr)  


            st.write(f"for {i}:buy and hold returns(1$):{round(buy_hold_retuns1dlr[0],2)}")
            
            st.write(f"for {i}:Strategy(1$):{round(strategy_returns[0],2)}")                



            data_container = st.container()

            with data_container:
              tab1, tab2 = st.columns(2)

              with tab1:
                  fig1=go.Figure(data=[go.Scatter(x=trends.index, y=trends['close'],),
                  go.Scatter(x=trends.index, y=trends.sma_s, line=dict(color='green', width=3),name = 'sma_50' ),
                   go.Scatter(x=trends.index, y=trends.sma_l, line=dict(color='red', width=3),name = 'sma_200' )])

                  st.plotly_chart(fig1)
              with tab2:
                  
                  fig2=go.Figure(data=[go.Scatter(x=trends.index, y=trends['c_returns'],name = 'buy and hold'),
                  go.Scatter(x=trends.index, y=trends.c_strategy, line=dict(color='green', width=3),name = 'golden cross strategy' )])

                  st.plotly_chart(fig2)

            st.write("****")
                  


            


            
        #    data['sma_s']=data.i.rolling(sma_s).mean()
       #     data['sma_l']=data.i.rolling(sma_l).mean()
         #   st.write(data[i])

          #  return data[i]
    SMA(data)



        
    




