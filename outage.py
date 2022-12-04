from cgitb import text
from datetime import datetime
from email.policy import default
from enum import unique
from itertools import groupby
from optparse import Option
from re import template
from sqlite3 import Time
from time import strftime, struct_time, time
from tkinter import CENTER, Grid
from typing import Text
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO, BytesIO
import plotly.graph_objects as go
from pyecharts.charts import Liquid, Grid
from pyecharts import options as opts
from streamlit_echarts import st_echarts
from streamlit_echarts import st_pyecharts
from pyecharts.globals import SymbolType
 


def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

def generate_html_download_link(fig):
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)




st.set_page_config(page_title='Outage Dash', layout="wide")
st.title('Outage report  🗼')
st.subheader('Please upload the outage for visual representation')
 

uploaded_file = st.file_uploader('choose an xlsx file',type ='xlsx')

if uploaded_file:
    st.markdown('-----')
    
    
    df=pd.read_excel(uploaded_file, header=[2], engine='openpyxl').astype(str)
     
     
    
     
    df.columns = df.columns.str.replace('-','')\
        .str.replace(' ','_')
    
     
    
     
     

    st.dataframe(df)

     


    groupby_column = st.selectbox(
        'what you would like to view and analays? ',
        ('SC','Team_Leader','WILAYA','Region','Halted','Duration','Pr','Technology')
    )

    output_column = ['TT']
     
    df_grouped=df.groupby(by=[groupby_column],as_index=False)[output_column].count()
    
    
    fig= px.bar(
        df_grouped,
        x=groupby_column,
        y='TT',
        template='plotly_white',
        text_auto=True,
        
        title=f'<b>Number of sites by {groupby_column}<b>'


    )
    st.plotly_chart(fig)

    st.sidebar.header('Please filter here ..!!')
     

    SCt = st.sidebar.multiselect(

     "Select the SC:",
     options=df["SC"].unique(),
     default=df["SC"].unique()

    )
    tech = st.sidebar.multiselect(

     "Select the Technology:",
     options=df["Technology"].unique(),
     default=df["Technology"].unique()

    )

    TLt = st.sidebar.multiselect(

     "Select the Team Leader:",
     options=df["Team_Leader"].unique(),
     default=df["Team_Leader"].unique()

    )

    

    df_selection= df.query(

        "Technology == @tech & Team_Leader == @TLt & SC == @SCt"
        )




    st.title('Filtered Outage report 🗼')
    countif2g= df_selection.query('Technology=="2G"')['TT'].count()
    countif3g= df_selection.query('Technology=="3G"')['TT'].count()
    countif4g= df_selection.query('Technology=="4G"')['TT'].count()

    total=countif2g+countif3g+countif4g

    towG=countif2g/total
    threeG=countif3g/total
    fourG=countif4g/total

    


    tg=(
        Liquid()
        .add("lq",[towG], center=["15%","35%"])
        .set_global_opts(title_opts = opts.TitleOpts(title='2G',pos_left="5%"))
    )

    trg=(
        Liquid()
        .add("lq",[threeG], center=["50%","35%"])
        .set_global_opts(title_opts = opts.TitleOpts(title='3G',pos_left="40%"))
    )

    fg=(
        Liquid()
        .add("lq",[fourG],center=["85%","35%"])
        .set_global_opts(title_opts = opts.TitleOpts(title='4G',pos_left="75%"))
    )

    grid = (

        Grid()
        .add(tg, grid_opts=opts.GridOpts())
        .add(trg, grid_opts=opts.GridOpts())
        .add(fg, grid_opts=opts.GridOpts())
        
    )

    st_pyecharts(grid)

     


     

   
    




    left_column, middel_column, right_column = st.columns(3)
    
    with left_column:
     st.subheader('2G sites down:')      

     st.subheader(countif2g)

    with middel_column:
     st.subheader('3G sites down:')
     st.subheader(countif3g)

    with right_column:
     st.subheader('4G sites down:')
     st.subheader(countif4g)  
           

    st.dataframe(df_selection)


    

    Sites=(

        df_selection.groupby(by=["SC"],as_index=False)[output_column].count()


    )

     
    output_column = ['TT']
     
     
    
    
    fig2= px.bar(
        Sites,
        x='SC',
        y='TT',
        template='plotly_white',
        text_auto=True,
        
        title=f'<b>Number of sites by SC<b>'


    )
     


    Sites2=(

        df_selection.groupby(by=["Duration"],as_index=False)[output_column].count()


    )

     
    output_column = ['TT']
     
     
    
    
    fig3= px.bar(
        Sites2,
        x='Duration',
        y='TT',
        template='plotly_white',
        text_auto=True,
        
        title=f'<b>Number of sites by Duration<b>'


    )
     


    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig2,use_container_width=True)
    right_column.plotly_chart(fig3,use_container_width=True)

    Sites3=(

        df_selection.groupby(by=["Region"],as_index=False)[output_column].count()


    )

     
    output_column = ['TT']
     
     
    
    
    fig4= px.bar(
        Sites3,
        x='Region',
        y='TT',
        template='plotly_white',
        text_auto=True,
        
        title=f'<b>Number of sites by Region<b>'


    )

    Sites4=(

        df_selection.groupby(by=["Technology"],as_index=False)[output_column].count()


    )

     
    output_column = ['TT']
     
     
    
    
    fig5= px.bar(
        Sites4,
        x='Technology',
        y='TT',
        template='plotly_white',
        text_auto=True,
        
        title=f'<b>Number of sites by Technology<b>'


    )

    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig4,use_container_width=True)
    right_column.plotly_chart(fig5,use_container_width=True)


    Sites5=(

        df_selection.groupby(by=["Team_Leader"],as_index=False)[output_column].count()


    )

     
    output_column = ['TT']
     
     
    
    
    fig6= px.bar(
        Sites5,
        x='Team_Leader',
        y='TT',
        template='plotly_white',
        text_auto=True,
        
        title=f'<b>Number of sites by Team_Leader<b>'


    )

    st.plotly_chart(fig6,use_container_width=True)


    
    





   
     

    st.subheader('Download:')
    generate_excel_download_link(df_grouped)
    generate_html_download_link(fig)
    generate_excel_download_link(df_selection)