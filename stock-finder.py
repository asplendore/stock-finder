import streamlit as st
from streamlit import caching
import alpaca_trade_api as tradeapi
import numpy as np
import statistics as stats
import pandas as pd
import pandas_ta as pta
import base64

APCA_API_BASE_URL="https://paper-api.alpaca.markets"

st.title('Stock Finder')

st.markdown("""
Developed by A.Splendore - Version 0.1 - 25 August 2021

""")

password = st.text_input("Enter a password", type="password")

DOW= set(["MMM","AXP","AMGN","AAPL","BA","CAT","CVX","CSCO","KO","DOW","GS","HD","HON","IBM","INTC",
        "JNJ","JPM","MCD","MRK","MSFT","NKE","PG","CRM","TRV","UNH","VZ","V","WMT","WBA","DIS"])

NASDAQ=set(["AAPL","MSFT","AMZN","FB","GOOG","INTC","CMCSA","CSCO","PEP","COST","ADBE","AMGN","TXN","NFLX",
        "PYPL","NVDA","AVGO","SBUX","CHTR","QCOM","BKNG","GILD","MDLZ","CELG","FISV","ADP","TMUS","INTU",
        "ISRG","CSX","WBA","MU","AMAT","TSLA","ILMN","VRTX","ATVI","ROST","BIIB","ADI","MAR","NXPI","LRCX",
        "KHC","AMD","CTSH","XEL","EBAY","REGN","ORLY","ADSK","MNST","PAYX","BIDU","SIRI","EA","JD","DLTR",
        "CTAS","MELI","KLAC","LULU","WDAY","VRSK","PCAR","IDXX","WLTW","XLNX","UAL","MCHP","ALXN","VRSN",
        "CERN","NTES","FAST","SNPS","EXPE","ASML","CDNS","WDC","ALGN","INCY","CHKP","MXIM","HAS","SWKS",
        "ULTA","TTWO","CTXS","NTAP","AAL","LBTYK","BMRN","JBHT","WYNN","MYL","HSIC","FOX","LBTYA"])

SP500=set (["MMM","ABT","ABBV","ABMD","ACN","ATVI","ADBE","AMD","AAP","AES","AFL","A","APD",
            "AKAM","ALK","ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN","AMCR",
            "AEE","AAL","AEP","AXP","AIG","AMT","AWK","AMP","ABC","AME","AMGN","APH","ADI","ANSS",
            "ANTM","AON","AOS","APA","AAPL","AMAT","APTV","ADM","ANET","AJG","AIZ","T","ATO","ADSK",
            "ADP","AZO","AVB","AVY","BKR","BLL","BAC","BK","BAX","BDX","BBY","BIO","BIIB",
            "BLK","BA","BKNG","BWA","BXP","BSX","BMY","AVGO","BR","BF.B","CHRW","COG","CDNS","CZR",
            "CPB","COF","CAH","KMX","CCL","CARR","CTLT","CAT","CBOE","CBRE","CDW","CE","CNC","CNP",
            "CERN","CF","CRL","SCHW","CHTR","CVX","CMG","CB","CHD","CI","CINF","CTAS","CSCO","C",
            "CFG","CTXS","CLX","CME","CMS","KO","CTSH","CL","CMCSA","CMA","CAG","COP","ED","STZ",
            "COO","CPRT","GLW","CTVA","COST","CCI","CSX","CMI","CVS","DHI","DHR","DRI","DVA","DE",
            "DAL","XRAY","DVN","DXCM","FANG","DLR","DFS","DISCA","DISCK","DISH","DG","DLTR","D",
            "DPZ","DOV","DOW","DTE","DUK","DRE","DD","DXC","EMN","ETN","EBAY","ECL","EIX","EW",
            "EA","EMR","ENPH","ETR","EOG","EFX","EQIX","EQR","ESS","EL","ETSY","EVRG","ES","RE",
            "EXC","EXPE","EXPD","EXR","XOM","FFIV","FB","FAST","FRT","FDX","FIS","FITB","FE","FRC",
            "FISV","FLT","FMC","F","FTNT","FTV","FBHS","FOXA","FOX","BEN","FCX","GPS","GRMN","IT",
            "GNRC","GD","GE","GIS","GM","GPC","GILD","GL","GPN","GS","GWW","HAL","HBI","HIG","HAS",
            "HCA","PEAK","HSIC","HSY","HES","HPE","HLT","HOLX","HD","HON","HRL","HST","HWM","HPQ",
            "HUM","HBAN","HII","IEX","IDXX","INFO","ITW","ILMN","INCY","IR","INTC","ICE","IBM","IP",
            "IPG","IFF","INTU","ISRG","IVZ","IPGP","IQV","IRM","JKHY","J","JBHT","SJM","JNJ","JCI",
            "JPM","JNPR","KSU","K","KEY","KEYS","KMB","KIM","KMI","KLAC","KHC","KR","LHX","LH",
            "LRCX","LW","LVS","LEG","LDOS","LEN","LLY","LNC","LIN","LYV","LKQ","LMT","L","LOW","LUMN",
            "LYB","MTB","MRO","MPC","MKTX","MAR","MMC","MLM","MAS","MA","MKC","MXIM","MCD","MCK","MDT",
            "MRK","MET","MTD","MGM","MCHP","MU","MSFT","MAA","MRNA","MHK","TAP","MDLZ","MPWR","MNST",
            "MCO","MS","MOS","MSI","MSCI","NDAQ","NTAP","NFLX","NWL","NEM","NWSA","NWS","NEE","NLSN",
            "NKE","NI","NSC","NTRS","NOC","NLOK","NCLH","NOV","NRG","NUE","NVDA","NVR","NXPI","ORLY",
            "OXY","ODFL","OMC","OKE","ORCL","OGN","OTIS","PCAR","PKG","PH","PAYX","PAYC","PYPL","PENN",
            "PNR","PBCT","PEP","PKI","PRGO","PFE","PM","PSX","PNW","PXD","PNC","POOL","PPG","PPL","PFG",
            "PG","PGR","PLD","PRU","PTC","PEG","PSA","PHM","PVH","QRVO","PWR","QCOM","DGX","RL","RJF",
            "RTX","O","REG","REGN","RF","RSG","RMD","RHI","ROK","ROL","ROP","ROST","RCL","SPGI","CRM",
            "SBAC","SLB","STX","SEE","SRE","NOW","SHW","SPG","SWKS","SNA","SO","LUV","SWK","SBUX","STT",
            "STE","SYK","SIVB","SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TGT","TEL","TDY","TFX","TER",
            "TSLA","TXN","TXT","TMO","TJX","TSCO","TT","TDG","TRV","TRMB","TFC","TWTR","TYL","TSN","UDR",
            "ULTA","USB","UAA","UA","UNP","UAL","UNH","UPS","URI","UHS","UNM","VLO","VTR","VRSN","VRSK",
            "VZ","VRTX","VFC","VIAC","VTRS","V","VNO","VMC","WRB","WAB","WMT","WBA","DIS","WM","WAT",
            "WEC","WFC","WELL","WST","WDC","WU","WRK","WY","WHR","WMB","WLTW","WYNN","XEL","XLNX",
            "XYL","YUM","ZBRA","ZBH","ZION","ZTS"])

ALLSTOCKS=DOW.union(NASDAQ.union(SP500))

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="stocks.csv">Download CSV File for Stocks Summary</a>'
    return href

def parameters_calc(symbol,api):
    price=api.get_barset(symbol, 'minute', 1).df.iloc[0][symbol]['close']
    # get closeList, hiList, loList
    bars = api.get_barset(symbol, 'day', limit=20)[symbol]
    closeList=[]
    hiList=[]
    loList=[]
    for i in range(20):
        closeList.append(bars[i].c)
        hiList.append(bars[i].h)
        loList.append(bars[i].l)
    price_1=closeList[-1]
    average=stats.mean(closeList)
    sigma=stats.stdev(closeList)
    score=(average-price)/sigma
    drop=100*((average-price)/average)
    cList=pd.DataFrame(closeList,columns=["Close"])
    cList["rsi"]=pta.rsi(close=cList["Close"],lenght=14)
    rsi14=cList["rsi"].iloc[-1]
    willR=100+(max(hiList)-price)/(max(hiList)-min(loList))*(-100)
    return score, average, price, price_1, drop, sigma, rsi14, willR


@st.cache
def finder(password,stocks,minscore,maxrsi,maxwillr):
    column_names=["Symbol","Score","Sigma","RSI14","WillR","AvgPrice","Price","Price-1","Drop_pct"]
    APCA_API_KEY_ID="PKT6HZPXP6ZFZOAABF3M"
    APCA_API_SECRET_KEY="uxfb0pNMqzt4Zrc43EvqaBwvLhdG89wXmtgx4ugB"

    if password=="capala":
        api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY,APCA_API_BASE_URL)
        clock = api.get_clock()
        rows_df=[]
        for stock in stocks:
            score, average, price, price_1, drop, sigma, rsi14, willR = parameters_calc(stock,api)
            if (score>=minscore)and(rsi14<=maxrsi)and(willR<=maxwillr):
                rows_df.append([stock,score,sigma,rsi14,willR,average,price,price_1,drop])
        df=pd.DataFrame(rows_df, columns=column_names)
        if rows_df==[]:
            df_sorted=pd.DataFrame(columns=column_names)
        else:
            df_sorted=df.sort_values(by=["Score"],ascending=False)
    else:
        df_sorted=pd.DataFrame(columns=column_names)
    return clock, df_sorted


if password=="capala":
    MINSCORE=st.number_input("Insert Minimum Score:",step=0.25)
    MAXRSI=st.number_input("Insert Maximum RSI14:", min_value=0.0, max_value=100.0, value=100.0,step=5.0)
    MAXWILLR=st.number_input("Insert Maximum WilliamR:", min_value=0.0, max_value=100.0, value=100.0,step=5.0)
    st.write("Find the best opportunities among Dow30, Nasdaq100 and SP500 stocks:")
    st.write("Click the button below .... (It can take longer than 10 minutes!)")
    startFind=st.button(" Go! ")
    if startFind:
        clock, df_sorted=finder(password,ALLSTOCKS,MINSCORE,MAXRSI,MAXWILLR)
        if clock.is_open:
            market="OPEN"
        else:
            market="CLOSED"
        st.write("The Market is ",market)
        st.balloons()
        st.write("Found the following stoks:")
        st.dataframe(df_sorted)
        st.markdown(filedownload(df_sorted), unsafe_allow_html=True)
    else:
        caching.clear_cache()
elif password!="":
    st.info("*Warning: wrong password !!!*")
    caching.clear_cache()
    
