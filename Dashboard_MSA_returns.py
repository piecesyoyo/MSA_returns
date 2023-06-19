# -*- coding: utf-8 -*-
"""
Created on Sat May 27 18:39:56 2023

@author: tai
"""
#%%: streamlit run C:\Tai\RE_project\Github\dashboards\MSA_returns\Dashboard_MSA_returns.py 

import pandas as pd
import os
import streamlit as st
import plotly.express as px
import numpy as np
import numpy_financial as npf #DOWNLOAD: pip3 install numpy-financial

#%% page setup
st.set_page_config(layout="wide")  # this needs to be the first Streamlit command

#add title
st.header("Returns Comparison: Investment Property vs. Stock Market")
st.markdown("by Major Metropolitan Statistical Areas (MSAs). Data from Realtor.com.")

st.sidebar.title("Control panel")

col1,col2 = st.columns([6, 5])

#%% import 'df_MSA_price.csv' and 'df_SPY' from here
#setup path to export csv 
# os.chdir("C:\\Tai\\RE_project\\Github\\dashboards\\MSA_returns\\csv")
# path = os.getcwd()
# path_csv = path + "\\"

# df_MSA_price = pd.read_csv(path_csv + "df_MSA_price.csv")
# df_SPY = pd.read_csv(path_csv + "df_SPY.csv")
# df_SPY = df_SPY.drop('Unnamed: 0', axis=1)
# df_SPY = df_SPY.rename({'index': 'Date', 'Close': 'Price'}, axis=1)  

#%% to import csv files 'df_MSA_price.csv' and 'df_SPY.csv' from Github.

url_MSA_price = 'https://raw.githubusercontent.com/liu3388/RE_input/main/df_MSA_price.csv'
df_MSA_price = pd.read_csv(url_MSA_price)

url_SPY = 'https://raw.githubusercontent.com/liu3388/RE_input/main/df_SPY.csv'
df_SPY = pd.read_csv(url_SPY)
df_SPY = df_SPY.drop('Unnamed: 0', axis=1)
df_SPY = df_SPY.rename({'index': 'Date', 'Close': 'Price'}, axis=1)

#%% create list for top 100 MSAs
list_MSA = df_MSA_price.MSA.unique()

list_MSA = list_MSA.tolist()
list_MSA = sorted(list_MSA)

#%% set up side-bar inputs
selected_msa = st.sidebar.selectbox("Select MSA below", list_MSA, key="selected_msa")

# user input side-bar for Downpayment
if "Downpayment" not in st.session_state:
    Downpayment = 0.20

DOWNPAYMENT = st.sidebar.number_input(
    'Input downpayment, in %',
    value=float(20),
    step=1.0,
    help="Downpayment for property, in %",
    key='Downpayment', 
    )


# user input side-bar for interest rates
if "INT_RATE" not in st.session_state:
    INT_RATE = 5.00

INTEREST = st.sidebar.number_input(
    'Input mortgage interest rate, in %',
    value=float(5.00),
    step=0.1,
    help="The interest rate on your mortgage",
    key='INT_RATE', 
    )


# user input side-bar for mortgage terms
if "MORTGAGE_TERMS" not in st.session_state:
    MORTGAGE_TERMS = 30
    # set the initial default value of the slider widget
    # st.session_state.MORTGAGE_TERMS = 30

LOAN_LIFE = st.sidebar.number_input(
    'Mortgage terms, in years (usually 15 or 30)',
    min_value=0,
    value=30,
    max_value=50,
    step=1,
    help="The life of the mortgage terms, usually 15, 20 or 30 years.",
    key='MORTGAGE_TERMS', 
    )


# user input side-bar for rental yields
if "RENT_YIELD" not in st.session_state:
    RENT_YIELD = 4.0
    
RENTAL_YIELD = st.sidebar.number_input(
    'Input estimated net rental yield, in %',
    value=float(4.0),
    step=0.1,
    help="The estimated net rental yield on your property.",
    key='RENT_YIELD', 
      )


#%% create table to calculate returns here

# #covnert string column to datetime
# df_MSA_price['Date'] = pd.to_datetime(df_MSA_price['Date'], format='%Y%m', errors='coerce').dropna()

df_MSA_select = df_MSA_price.loc[df_MSA_price['MSA'] == selected_msa]
df_MSA_select = df_MSA_select.sort_values('Date')
df_MSA_select.reset_index()
df_MSA_select = df_MSA_select[['Date','MSA','median_listing_price']]

Purchase_price = df_MSA_select.iloc[0]['median_listing_price']
Purchase_date = df_MSA_select.iloc[0]['Date']
# Purchase_date = Purchase_date.date()

df_MSA_select['Downpayment_%'] = DOWNPAYMENT/100
Down_payment = str(DOWNPAYMENT) + "%"

df_MSA_select['Downpayment_Amt'] = df_MSA_select['Downpayment_%'] * Purchase_price 
df_MSA_select['Price_change'] = df_MSA_select['median_listing_price'] - Purchase_price 

#add interest costs column
df_MSA_select['Interest_costs'] = (Purchase_price - df_MSA_select.iloc[0]['Downpayment_Amt']) * (INTEREST/100)

#add rental returns column
df_MSA_select['Rental_yield'] = RENTAL_YIELD / 100
df_MSA_select['Monthly_rental_income'] = (df_MSA_select['Rental_yield'] * df_MSA_select['median_listing_price']) / 12

df_MSA_select['Cum_rent'] = df_MSA_select['Monthly_rental_income'].cumsum()

#columns for returns as %
df_MSA_select['Price_returns'] = df_MSA_select['Price_change'] / df_MSA_select['Downpayment_Amt']

df_MSA_select['Rent_returns'] =  df_MSA_select['Cum_rent'] / df_MSA_select['Downpayment_Amt']


#%%
df_returns = df_MSA_select[['Date', 'median_listing_price', 'Price_change', 'Cum_rent']]
df_returns = df_returns.round(0) # remove all decimals

df_returns = df_returns.rename({'Price_change': 'Price appreciation', 
                                'median_listing_price': 'Price',
                                'Cum_rent': 'Total rental income',
                                }, axis=1)

df_returns = df_returns.reset_index()

PROPERTY_PRICE = df_returns.iloc[0]['Price']

#drop columns
df_returns.drop(['index', 'Price'], axis=1, inplace=True)

#%%
# ##### PARAMETERS #####
# # CONVERT MORTGAGE AMOUNT TO NEGATIVE BECAUSE MONEY IS GOING OUT
# mortgage_amount = -(Purchase_price * (1-(DOWNPAYMENT/100)))
# interest_rate = (INTEREST / 100) / 12
# periods = LOAN_LIFE*12
# # CREATE ARRAY
# n_periods = np.arange(LOAN_LIFE * 12) + 1

# ##### BUILD AMORTIZATION SCHEDULE #####
# # INTEREST PAYMENT
# interest_monthly = npf.ipmt(interest_rate, n_periods, periods, mortgage_amount)

# # PRINCIPAL PAYMENT
# principal_monthly = npf.ppmt(interest_rate, n_periods, periods, mortgage_amount)

# # JOIN DATA
# df_initialize = list(zip(n_periods, interest_monthly, principal_monthly))
# df = pd.DataFrame(df_initialize, columns=['period','interest','principal'])

# st.write(df)

#%%

with col1:
    
    ##### PARAMETERS #####
    # CONVERT MORTGAGE AMOUNT TO NEGATIVE BECAUSE MONEY IS GOING OUT
    mortgage_amount = -(Purchase_price * (1-(DOWNPAYMENT/100)))
    interest_rate = (INTEREST / 100) / 12
    periods = LOAN_LIFE*12
    # CREATE ARRAY
    n_periods = np.arange(LOAN_LIFE * 12) + 1
    
    ##### BUILD AMORTIZATION SCHEDULE #####
    # INTEREST PAYMENT
    interest_monthly = npf.ipmt(interest_rate, n_periods, periods, mortgage_amount)
    
    # PRINCIPAL PAYMENT
    principal_monthly = npf.ppmt(interest_rate, n_periods, periods, mortgage_amount)
    
    # JOIN DATA
    df_initialize = list(zip(n_periods, interest_monthly, principal_monthly))
    df = pd.DataFrame(df_initialize, columns=['period','interest','principal'])
    
    # SET UP CUMULATIVE INTERST AND PRINCIPAL COLUMNS
    df['Total interest costs'] = df['interest'].cumsum()
    df['Total loan repayment'] = df['principal'].cumsum()
    df = df.round(0) #round numbers to nearest integer
    
    df2 = df[['Total interest costs','Total loan repayment']]
        
    # st.write(df2)
    
    ################## Amortization calculator ends here######
    
    
    #merge dfs: df_returns and df2
    df_returns = df_returns.merge(df2,how='left', left_index=True, right_index=True)
    df_returns['Cumulative rental income - interests costs'] = df_returns['Total rental income'] - df_returns['Total interest costs']
    
    df_returns2 = df_returns[['Date', 'Price appreciation', 'Cumulative rental income - interests costs', 
                              'Total loan repayment']]
        
    colors = {'Price appreciation':'blue',
              'Cumulative rental income - interests costs': 'magenta',
              'Total loan repayment': 'orange',
              }
    
    #convert data to line chart
    fig_returns = px.bar(df_returns2, 
                          x='Date', 
                          y=[c for c in df_returns2.columns],
                          color_discrete_map=colors
                          )
        
    fig_returns.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=16,
        title_font_family="Arial",
        title_font_color="black",
        title = (f'<b>Property Investment: $ Returns Since {Purchase_date}, {Down_payment} Downpayment</b> <br> {selected_msa}'),
        title_font_size=18,
        legend_title_font_color="black",
        legend_font_size=16,
        legend_title=None,
        yaxis_title=None,
        xaxis_title=None,
        yaxis_tickprefix = '$',
        yaxis_tickformat = ',',
        # yaxis_range=[-5, 5],
        showlegend=True,
        title_x=0.08,
        title_y=0.93,
        width=850,
        height=500, 
        bargap=0.05,
        
        margin=dict(t=80),
                
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.75,
            xanchor="center",
            x=0.3)
        )
    
        
    #add note to chart
    fig_returns.add_annotation(
    showarrow=False,
    text='Note: Total return = (Price appreciation + Total rental income – interests costs + Total loan repayment) / Downpayment.',
    font=dict(size=13), 
    xref='x domain',
    x=0.005,
    yref='y domain',
    y=-0.15
    )
    
    df_returns2['Total returns'] = df_returns2['Price appreciation'] + df_returns2['Cumulative rental income - interests costs'] + df_returns2['Total loan repayment']
    
    #add text box on returns
    #calculate returns and %-tage returns
    total_return = df_returns2['Total returns'].iloc[-1]
    Downpayment_Amt = df_MSA_select['Downpayment_Amt'].iloc[0]
    total_percent_return = total_return / Downpayment_Amt
    
    #format numbers
    total_return = '${:,.0f}'.format(total_return)
    total_percent_return = round(total_percent_return*100)
    total_percent_return = str(total_percent_return) + "%"
    
    fig_returns.add_annotation(text=(f'<b>Total return = {total_percent_return}</b>'),
                  xref="x domain", yref="y domain",
                  x=0.05, y=0.725, showarrow=False, font_size = 20)
    
    
    
    config = {'displayModeBar': True} #turn off mode bar on top:
        
    st.plotly_chart(fig_returns)

#%% create df for proportional square chart
df_square_chart = df_MSA_select[['Date','Downpayment_Amt', 'Cum_rent', 'Price_change']].reset_index(drop=True)
df_merged = df_square_chart.merge(df, how='inner', left_index=True, right_index=True)
df_merged['Total interest paid'] = df_merged ['Total interest costs'] * -1
df_merged = df_merged[['Downpayment_Amt','Cum_rent','Total interest costs', 'Price_change',
                        'Total loan repayment']]

df_merged = df_merged.rename({'Downpayment_Amt': 'Down payment', 
                              'Cum_rent': 'Total rent collected',
                              'Price_change': 'Price appreciation',
                                }, axis=1).transpose()

df_merged = df_merged.iloc[:,-1].reset_index()

df_merged = df_merged.rename({'index': 'Category'}, axis=1)
df_merged.columns = [*df_merged.columns[:-1], 'Dollar']

Total_gains = df_merged['Dollar'].iloc[3] + df_merged['Dollar'].iloc[1] + df_merged['Dollar'].iloc[4] - df_merged['Dollar'].iloc[2]
Total_gains = '${:,.0f}'.format(Total_gains)


#%%
with col2:
    
    fig = px.treemap(df_merged, path=[px.Constant('<b>Where does the money come from?</b>'), 'Category'],
                 values=df_merged.Dollar,
                 color=df_merged.Category,
                 # color_discrete_map=color_country,
                 # hover_name=Label_per,
                )
    
    fig.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=16,
        title_font_family="Arial",
        title_font_color="black",
        title = (f'<b>Total Financial Gains: {Total_gains} </b> <br> Price Appreciation + Rent Collected + Loan Repayment – Interest Costs'),
        title_font_size=18,
        legend_title_font_color="black",
        legend_font_size=16,
        legend_title=None,
        yaxis_title=None,
        xaxis_title=None,
        yaxis_tickprefix = '$',
        yaxis_tickformat = ',',
        # yaxis_range=[-5, 5],
        showlegend=True,
        title_x=0.08,
        title_y=0.93,
        width=700,
        height=500, 
        bargap=0.05,
        
        margin=dict(t=80, l=50),
                
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.75,
            xanchor="center",
            x=0.2)
        )
    
    fig.update_traces(hovertemplate='%{label: labels } <br> $%{value:,.0f}')
    
    config = {'displayModeBar': False} #turn off mode bar on top:
              
    st.plotly_chart(fig)
    
#%%

with col1:
    
    #call in df_SPY
    df_SPY['Investment'] = Downpayment_Amt
    df_SPY['Shares'] = df_SPY['Investment'].iloc[0] / df_SPY['Price'].iloc[0]
    df_SPY['Investment value'] = df_SPY['Shares'] * df_SPY['Price']
    df_SPY['Price appreciation'] = df_SPY['Investment value'] - df_SPY['Investment']
    df_SPY['Cumulative dividend'] = df_SPY['Cumulative dividends'] * df_SPY['Shares'] 
    
    df_SPY_chart = df_SPY[['Date', 'Price appreciation', 'Cumulative dividend']]
    df_SPY_chart = df_SPY_chart.round(0)
        
    colors = {'Price appreciation':'blue',
               'Cumulative dividend': 'magenta',
               }
    
    # convert data to chart
    fig_SPY = px.bar(df_SPY_chart, 
                          x='Date', 
                          y=[c for c in df_SPY_chart.columns],
                          color_discrete_map=colors
                          )
        
    fig_SPY.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=16,
        title_font_family="Arial",
        title_font_color="black",
        title = (f'<b>Stock Market Investment: Cumulative $ Returns Since {Purchase_date}</b> <br> Use the {Down_payment} downpayment to invest in S&P 500 Index fund'),
        title_font_size=18,
        legend_title_font_color="black",
        legend_font_size=16,
        legend_title=None,
        yaxis_title=None,
        xaxis_title=None,
        yaxis_tickprefix = '$',
        yaxis_tickformat = ',',
        # yaxis_range=[-5, 5],
        showlegend=True,
        title_x=0.08,
        title_y=0.93,
        width=850,
        height=500, 
        bargap=0.05,
        
        margin=dict(t=80),
                
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.75,
            xanchor="center",
            x=0.25)
        )
    
        
    #add note to chart
    fig_SPY.add_annotation(
    showarrow=False,
    text='Source: Realtor.com, Yahoo Finance, ApexaVisoin.com, ',
    font=dict(size=13), 
    xref='x domain',
    x=0.005,
    yref='y domain',
    y=-0.15
    )
    
    df_SPY['Total returns'] = df_SPY['Price appreciation'] + df_SPY['Cumulative dividend']
    
    #add text box on returns
    #calculate returns and %-tage returns
    total_SPY_return = df_SPY['Total returns'].iloc[-1]
    SPY_investment = df_SPY['Investment'].iloc[0]
    total_percent_return = total_SPY_return / SPY_investment
    
    #format numbers
    total_return = '${:,.0f}'.format(total_percent_return)
    total_percent_return = round(total_percent_return*100)
    total_percent_return = str(total_percent_return) + "%"
    
    fig_SPY.add_annotation(text=(f'<b>Total return = {total_percent_return}</b>'),
                   xref="x domain", yref="y domain",
                   x=0.04, y=0.725, showarrow=False, font_size = 20)
       
    config = {'displayModeBar': True} #turn off mode bar on top:
        
    st.plotly_chart(fig_SPY)

#%% create SPY df for proportional square chart
df_square_SPY= df_SPY_chart
df_square_SPY['Original investment']=df_SPY['Investment']
df_square_SPY = df_square_SPY.transpose()

df_merged_SPY = df_square_SPY.iloc[:,-1].reset_index()

df_merged_SPY = df_merged_SPY.rename({'index': 'Category'}, axis=1)
df_merged_SPY.columns = [*df_merged_SPY.columns[:-1], 'Dollar']
df_merged_SPY = df_merged_SPY.iloc[1:]


Total_SPY_gains = df_merged_SPY['Dollar'].iloc[0] + df_merged_SPY['Dollar'].iloc[1]
Total_SPY_gains = '${:,.0f}'.format(Total_SPY_gains)

#%%
with col2:
    
    fig = px.treemap(df_merged_SPY, path=[px.Constant('<b>Where does the money come from?</b>'), 'Category'],
                 values=df_merged_SPY.Dollar,
                 color=df_merged_SPY.Category,
                 # color_discrete_map=color_country,
                 # hover_name=Label_per,
                )
    
    fig.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=16,
        title_font_family="Arial",
        title_font_color="black",
        title = (f'<b>Total Financial Gains: {Total_SPY_gains} </b> <br> Price Appreciation + Cumulative Dividend Payment'),
        title_font_size=18,
        legend_title_font_color="black",
        legend_font_size=16,
        legend_title=None,
        yaxis_title=None,
        xaxis_title=None,
        yaxis_tickprefix = '$',
        yaxis_tickformat = ',',
        # yaxis_range=[-5, 5],
        showlegend=True,
        title_x=0.08,
        title_y=0.93,
        width=700,
        height=500, 
        bargap=0.05,
        
        margin=dict(t=80, l=50),
                
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.75,
            xanchor="center",
            x=0.2)
        )
    
    fig.update_traces(hovertemplate='%{label: labels } <br> $%{value:,.0f}')
    
    config = {'displayModeBar': False} #turn off mode bar on top:
              
    st.plotly_chart(fig)