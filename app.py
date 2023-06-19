import streamlit as st
import pandas as pd
import time
import yfinance as yf
import time
import datetime
from datetime import datetime
from datetime import date
from datetime import timedelta
import warnings
import requests


st.set_page_config(layout='wide')

st.title("Invest like the Bulls of our time")

page=st.sidebar.radio(
    "Choose from the following options:",
    ("Top Investor's holdings","Investing Basics: Work in Progress"))

###
if page=="Top Investor's holdings":

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
    @st.cache(allow_output_mutation=True)

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

               # df=df[["Stock","Ticker","% ofPortfolio","RecentActivity","Shares","ReportedPrice*","Value","CurrentPrice","+/-ReportedPrice","52WeekLow","52WeekHigh"]]
              #  df['Ticker'] = df['Ticker'].str.replace('.','-')

                return df.columns


            st.write(fetching_stock_data(investor=investors))

            visual_data=fetching_stock_data(investor=investors)

###
            # def generating_visuals(visual_data):
            #     viz=[]
            #     for index,row in visual_data.iterrows():

            #         data=(yf.download(
            #         tickers = row['Ticker'],

            #         # What period of time are we interested in?
            #         # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            #         # In our case we will choose 10y
            #         period = "5y",

            #         # Next we need to define our interval.
            #         interval = "1d",

            #         # Ensure our data is grouped properly.
            #         group_by = 'ticker'
            #         ))
            #         columns = ["Date","Close"]
            #         data=data[['Close']]
            #         data.rename(index={1: 'a'},inplace=True)
            #         data['SMA_50'] = data['Close'].rolling(5).mean().shift()
            #         data['SMA_200'] = data['Close'].rolling(10).mean().shift()

                    

            #         prev_close=data['Close'].max()

            #     #    st.write(f"{row['Ticker']}")
            #         st.write(f"{row['Stock']}")
                    
            #         new=data.reset_index()

            #      #   st.write(data)

            #         new['Date'] = pd.to_datetime(new['Date']).dt.date
            #         new["Date"] = pd.to_datetime(new["Date"])

            #         minimum,maximum,YTD,five_year_RTD,five_year_p1,five_year_p2=insights(new)
            #         difference=maximum-minimum
            #         five_year_difference=five_year_p2-five_year_p1

            #         col1,col2,col3 = st.columns([1,1,1]) 

            #         with col1:
            #             st.metric("Previous Day Close", "$" + str(prev_close.round(2)))
            #         with col2:
            #             st.metric("YTD return and difference", str(YTD),difference.round(2))
            #         with col3:
            #             st.metric("Five year Return-Rate and difference", five_year_RTD,five_year_difference.round(2))


            # st.write(generating_visuals(visual_data))
