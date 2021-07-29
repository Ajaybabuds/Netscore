import pandas as pd 
import numpy as np
import streamlit as st
import altair as alt
import time
pd.set_option("display.precision",2)
pd.options.mode.use_inf_as_na = True
st.set_page_config(page_title="File Upload",page_icon=":registered:",layout='wide')
st.title("Understanding the Sales by Automation")
uploaded_file=st.file_uploader('Choose a File')
if uploaded_file is not None:
    df=pd.read_csv(uploaded_file,engine='python',encoding='utf-8')
    sales=df.loc[:,['Internal ID','Date','Amount']]
    def dropout(df1):
        for x in df1.columns:
            if x=='Internal ID':
                if df1[x].nunique()==df1.shape[0]:
                     return df1[x]
                else:
                    df1[x]=df1[x].drop_duplicates(keep='first')
                    return df1[x].dropna().index
    sales=sales.reindex(dropout(sales))
    sales['Date']=pd.to_datetime(sales['Date'])
    sales['month']=sales['Date'].dt.month
    sales['year']=sales['Date'].dt.year.astype('str')
    sales['week']=sales['Date'].dt.isocalendar().week
    sales['Week Day']=sales['Date'].apply(lambda x:x.strftime("%a"))
    sales['Quarter']=sales['Date'].dt.quarter
    col1,col2,col3=st.beta_columns(3)
    with col1:
         yr=st.selectbox("Select a Year",options=list(sales['year'].unique()))
    with col2:
         category=st.selectbox("Select a Category",options=['Week Day','week','month','Quarter'])
    with col3:
        metric=st.selectbox("Select a Metric",options=['Report','Charts','Pivot'])
    for j in list(sales['year'].unique()):
        if j in yr:
            for i in list(sales.columns):
                if i in category:
                    if "Report" in metric:
                        slct=st.sidebar.selectbox("Pick below to Calculate:",options=['Total Sales','Average Sales','Total Transactions','Growth Rate'])
                        if 'Total Sales' in slct:
                            res=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).sum().rename(columns={"Amount":'Total Sales'})
                            st.write(res)
                        elif 'Average Sales' in slct:
                            res1=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).mean().rename(columns={"Amount":'Average Sales'})
                            st.write(res1)
                        elif 'Total Transactions' in slct:
                            res2=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).count().rename(columns={"Amount":'Total Transactions'})
                            st.write(res2)
                        else:
                            res3=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).sum().pct_change().dropna().rename(columns={"Amount":'Growth Rate'})
                            st.write(res3)
                    elif "Charts" in metric:
                        choose=st.sidebar.selectbox("Pick below to Visualize:",options=['Total Sales','Average Sales','Total Transactions','Growth Rate'])
                        if 'Total Sales' in choose:
                            chrt=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).sum().rename(columns={"Amount":'Total Sales'})
                            ret=pd.DataFrame({"A":chrt.index,'B':chrt['Total Sales']})
                            st.altair_chart(alt.Chart(ret).mark_bar(size=20,color='firebrick').encode(
                            alt.X('A',title=i),alt.Y('B',title='Total Sales'),tooltip=['A',"B"]))  
                        elif 'Average Sales' in choose:
                            chrt1=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).mean().rename(columns={"Amount":'Average Sales'})
                            ret1=pd.DataFrame({"A":chrt1.index,'B':chrt1['Average Sales']})
                            st.altair_chart(alt.Chart(ret1).mark_bar(size=20,color='firebrick').encode(
                             alt.X('A',title=i),alt.Y('B',title='Average Sales'),tooltip=['A',"B"]))
                        elif 'Total Transactions' in choose:
                            chrt2=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).count().rename(columns={"Amount":'Total Transactions'})
                            ret2=pd.DataFrame({"A":chrt2.index,'B':chrt2['Total Transactions']})
                            st.altair_chart(alt.Chart(ret2).mark_bar(size=20).encode(
                            alt.X('A',title=i),alt.Y('B',title='Total Transactions'),tooltip=['A',"B"]))
                        else:
                            chrt3=sales.loc[sales['year']==j,[i,'Amount']].groupby([i]).sum().pct_change().dropna().rename(columns={"Amount":'Growth Rate'})
                            ret3=pd.DataFrame({"A":chrt3.index,'B':chrt3['Growth Rate']})
                            st.altair_chart(alt.Chart(ret3).mark_bar(size=20).encode(
                             alt.X('A',title=i),alt.Y('B',title='Growth Rate'),tooltip=['A',"B"],
                            color=alt.condition(
                            alt.datum.B>0,alt.value('green'),alt.value('red'))))
                    else:
                        st.markdown("** Generate Pivot Reports **")
                        col4,col5=st.beta_columns(2)
                        with col4:
                            idx=st.selectbox('Choose Index:',options=[m for m in sales.columns[2:] if m!='Amount'])
                        with col5:
                            col=st.selectbox("Choose Column",options=[m for m in sales.columns[2:] if m!='Amount'])
                        for a in sales.columns:
                            if a in idx:
                                for b in sales.columns[::-1]:
                                    if b in col:
                                        pvt=pd.pivot_table(data=sales,values='Amount',index=a,columns=b,aggfunc=[np.sum]
                                                      ,fill_value='-',margins=True,margins_name='Total').round(2)
                                        st.dataframe(pvt)
