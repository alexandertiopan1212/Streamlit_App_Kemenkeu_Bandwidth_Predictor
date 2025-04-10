#library
import pandas as pd
import numpy as np 
import streamlit as st

import plotly.express as px
from matplotlib import pyplot as plt
from PIL import Image

from statsmodels.tsa.stattools import acf, pacf, adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import statsmodels.api as sm
import pmdarima as pmd
from pmdarima.arima.utils import ndiffs

import math
import warnings



def main():
    # Session Handling
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame()
    
    if 'location' not in st.session_state:
         st.session_state.location = []

    if 'layanan' not in st.session_state:
         st.session_state.layanan = []

    if 'link' not in st.session_state:
         st.session_state.link = []

    if 'bandwidth' not in st.session_state:
         st.session_state.bandwidth = []

    if 'cols' not in st.session_state:
         st.session_state.cols = []

    if 'col_name' not in st.session_state:
         st.session_state.col_name = []

    if 'x' not in st.session_state:
         st.session_state.x = []

    if 'y' not in st.session_state:
         st.session_state.y = []
    
    if 'title' not in st.session_state:
        st.session_state.title = ''

    if 'df_latih' not in st.session_state:
         st.session_state.df_latih = pd.DataFrame()

    if 'df_transform1' not in st.session_state:
         st.session_state.df_transform1 = pd.DataFrame()

    if 'df_decompose' not in st.session_state:
         st.session_state.df_decompose = pd.DataFrame()

    if 'indexedDataset_logScale' not in st.session_state:
         st.session_state.indexedDataset_logScale = pd.DataFrame()

    # Main Interface
    img = Image.open('Seal_of_the_Ministry_of_Finance_of_the_Republic_of_Indonesia.svg.png')
    st.image(img, width=200)
    st.markdown(f'<h1 style="color:#E32236;font-size:56px;">{"WINTERIMA"}</h1>', unsafe_allow_html=True)
    st.header(':alpine[Aplikasi Peramalan Kebutuhan Kapasitas Bandwidth Kantor Daerah Menggunakan Metode Arima Dan Hold-Winters]')
    
    # Sidebar Initiation
    st.sidebar.title("Pilih Menu")
    menu0 = st.sidebar.selectbox("Data:", ["Choose", "Unggah Dataset", "Analisis Timeseries"])
    menu1 = st.sidebar.selectbox("Latih Data:", ["Choose", "ARIMA", "HOLT-WINTERS"])
    menu2 = st.sidebar.selectbox("Peramalan", ["Choose", "FORECASTING"])


    if menu0 == "Unggah Dataset" and menu1 == "Choose" and menu2 == "Choose":
        uploaded_file = st.file_uploader("Pilih Data Excel")
        if uploaded_file is not None:
            if st.button("Unggah"):
                #read excel
                xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
                df = pd.read_excel(xls, 'Sheet1', header = None)
                st.success("Unggah Berhasil! Mohon Tunggu...")

                st.session_state.location = df[0].unique()
                st.session_state.layanan = df[1].unique()
                st.session_state.link = df[2].unique()
                st.session_state.bandwidth = df[3].unique()

                for i in range(len(df)):
                    st.session_state.cols.append(df[0][i] + '__' + df[1][i] + '__' + df[2][i] + '__' + str(df[3][i]))

                df2 = pd.read_excel(xls, 'Sheet2', header = None)
                df2 = df2[4:]
                df3 = df2
                df3.columns = st.session_state.cols
                df3 = df3.reset_index().drop(['index'], axis=1)
                st.session_state.data = df3.copy(deep=True)

                st.success("Proses Selesai")

        else:
            st.warning("Unggah Data Terlebih Dahulu atau Ulangi Unggah Data")

    if menu0 == "Analisis Timeseries" and menu1 == "Choose" and menu2 == "Choose":
            
            loc = st.selectbox("Pilih Lokasi", sorted(st.session_state.location))
            split_cols = [item.split('__') for item in st.session_state.cols]

            lay_ = [item[1] for item in split_cols if item[0] == loc]
            lay_ = np.array(lay_)
            lay_ = np.unique(lay_)
            lay = lay_[0]
          #   lay = st.selectbox("Pilih Layanan", sorted(lay_))

            lin_ = [item[2] for item in split_cols if (item[0] == loc and item[1] == lay)]
            lin_ = np.array(lin_)
            lin_ = np.unique(lin_)
            lin = lin_[0]
          #   lin = st.selectbox("Pilih Link", lin_)

            ban_ = [item[3] for item in split_cols if (item[0] == loc and item[1] == lay and item[2] == lin)]
            ban_ = np.array(ban_)
            ban_ = np.unique(ban_)
            ban_ = sorted(ban_)
            ban = ban_[0]
          #   ban = st.selectbox("Pilih Bandwidth", ban_)

            col_ = loc + '__' + lay + '__' + lin + '__' + str(ban)

          #   type_ = st.selectbox("Pilih Transmiter atau Receiver", ["Transmiter", "Receiver"])
            type_ = "Receiver"
            type_n = "Peak"
          #   type_n = st.selectbox("Pilih Peak atau Average", ["Peak", "Average"])
            num = 0
            if st.button("Import Timeseries"):
                if type_ + ' ' + type_n == 'Peak Transmit':
                     num = 0
                if type_ + ' ' + type_n == 'Average Transmit':
                     num = 1
                if type_ + ' ' + type_n == 'Peak Receive':
                     num = 2
                if type_ + ' ' + type_n == 'Average Receive':
                     num = 3

                df = st.session_state.data[st.session_state.data.index.isin(list(range(num,len(st.session_state.data), 4)))]
                df = df.reset_index()
                df = df.drop(['index'], axis=1)
                df.index = pd.date_range(start="2023-05-01",end="2023-11-30")
                df = df.fillna(method='bfill')
                df = df[col_]

                bn = 1000*int(ban)
                df_plot = pd.DataFrame({
                     'Bandwidth (Kbps)': df.values,
                     'Max (Kbps)': [bn] * len(df),
                     'Day': [item.strftime('%a') for item in df.index],
                     'Week of Month': [(item.day - 1) // 7 + 1 for item in df.index],
                     'Quarter': [(item.month-1)//3+1 for item in df.index],
                     'Month': [item.strftime('%b') for item in df.index]
                })
                df_plot.index = [item.date() for item in df.index]
                st.dataframe(df_plot['Bandwidth (Kbps)'])


                # timeseries plot
                fig = px.line(df_plot,
                x=df_plot.index,
                y=df_plot['Bandwidth (Kbps)'],
                title = type_ + ' ' + type_n + ', ' + 'Lokasi: ' + loc + ', ' + 'Link: ' + lin + ', ' + 'Bandwidth: ' + str(ban) + ' Mbps',
                template = 'plotly_dark').update_layout(
                    xaxis_title="Date",
                    yaxis_title="Kbps",
                    showlegend = False
                )

                fig.add_scatter(x=df_plot.index, y=df_plot['Max (Kbps)'], mode='lines')

                fig.update_xaxes(
                    rangeslider_visible=True,
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    )
                )

                st.plotly_chart(fig, use_container_width=True)


                # boxplot daily
                fig = px.box(df_plot, x='Day', y='Bandwidth (Kbps)')
                st.plotly_chart(fig, use_container_width=True)

                # boxplot weekly
                fig = px.box(df_plot, x='Week of Month', y='Bandwidth (Kbps)')
                st.plotly_chart(fig, use_container_width=True)

                # boxplot monthly
                fig = px.box(df_plot, x='Month', y='Bandwidth (Kbps)')
                st.plotly_chart(fig, use_container_width=True)

                # boxplot quarterly
                fig = px.box(df_plot, x='Quarter', y='Bandwidth (Kbps)')
                st.plotly_chart(fig, use_container_width=True)
    
    if menu0 == "Choose" and menu1 == "ARIMA" and menu2 == "Choose":
            
            loc = st.selectbox("Pilih Lokasi", sorted(st.session_state.location))
            split_cols = [item.split('__') for item in st.session_state.cols]

            lay_ = [item[1] for item in split_cols if item[0] == loc]
            lay_ = np.array(lay_)
            lay_ = np.unique(lay_)
            lay = lay_[0]
          #   lay = st.selectbox("Pilih Layanan", sorted(lay_))

            lin_ = [item[2] for item in split_cols if (item[0] == loc and item[1] == lay)]
            lin_ = np.array(lin_)
            lin_ = np.unique(lin_)
            lin = lin_[0]
          #   lin = st.selectbox("Pilih Link", lin_)

            ban_ = [item[3] for item in split_cols if (item[0] == loc and item[1] == lay and item[2] == lin)]
            ban_ = np.array(ban_)
            ban_ = np.unique(ban_)
            ban_ = sorted(ban_)
            ban = ban_[0]
          #   ban = st.selectbox("Pilih Bandwidth", ban_)

            col_ = loc + '__' + lay + '__' + lin + '__' + str(ban)

          #   type_ = st.selectbox("Pilih Transmiter atau Receiver", ["Transmiter", "Receiver"])
          #   type_n = st.selectbox("Pilih Peak atau Average", ["Peak", "Average"])
            type_ = "Receiver"
            type_n = "Peak"
            num = 0

            if 'pilih_data_latih' not in st.session_state:
                 st.session_state.pilih_data_latih = 0

            if 'lanjut_transform' not in st.session_state:
                 st.session_state.lanjut_transform = 0

            if 'lanjut_pemodelan_arima' not in st.session_state:
                 st.session_state.lanjut_pemodelan_arima = 0

            if 'lanjut_acfpcf' not in st.session_state:
                 st.session_state.lanjut_acfpcf = 0
            
            if 'lanjut_dekomposisi' not in st.session_state:
                 st.session_state.lanjut_dekomposisi = 0

            if 'opt_tr' not in st.session_state:
                 st.session_state.opt_tr = ''

            
            if st.button("Pilih Data Latih"):
                 st.session_state.pilih_data_latih = 1

            if st.session_state.pilih_data_latih == 1:
                if type_ + ' ' + type_n == 'Peak Transmit':
                     num = 0
                if type_ + ' ' + type_n == 'Average Transmit':
                     num = 1
                if type_ + ' ' + type_n == 'Peak Receive':
                     num = 2
                if type_ + ' ' + type_n == 'Average Receive':
                     num = 3

                df = st.session_state.data[st.session_state.data.index.isin(list(range(num,len(st.session_state.data), 4)))]
                df = df.reset_index()
                df = df.drop(['index'], axis=1)
                df.index = pd.date_range(start="2023-05-01",end="2023-11-30")
                df = df.fillna(method='bfill')
                df = df[col_]

                df = df.resample('D').mean()
                df = df.fillna(df.mean())
                st.session_state.df_latih = df.copy(deep=True)

                # adfuller test
                dftest = adfuller(df, autolag='AIC')
                dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
                for key,value in dftest[4].items():
                    dfoutput['Critical Value (%s)'%key] = value
                dfoutput = pd.DataFrame(dfoutput)
                dfoutput.columns = ['Nilai']

                st.subheader("Adfuller Test")
                st.dataframe(dfoutput)
                st.write("""
                         Syarat stasioner uji adfuller:
                         1. p-value harus sekecil mungkin
                         2. critical-values 1%, 5%, 10% harus sedekat mungkin dengan nilai test statistic
                         Jika tidak terpenuhi maka harus dilakukan transformasi data (agar stasioner)
                         """)

                if st.button("Lanjut Transformasi"):
                    st.session_state.lanjut_transform = 1
            
            if st.session_state.lanjut_transform == 1:
               #  st.session_state.opt_tr = st.selectbox("Pilih Metode Transformasi", ["Log Scale"])
                st.session_state.opt_tr = "Log Scale"

                if st.session_state.opt_tr == "Log Scale":
                    st.write("Log Scale")
                    indexedDataset = st.session_state.df_latih.copy(deep=True)
                    indexedDataset_logScale = np.log(indexedDataset)
                    st.session_state.indexedDataset_logScale = indexedDataset_logScale.copy(deep=True)

                    movingAverage = indexedDataset_logScale.rolling(window=12).mean()
                    movingSTD = indexedDataset_logScale.rolling(window=12).std()

                    
                    datasetLogScaleMinusMovingAverage = indexedDataset_logScale - movingAverage
                    datasetLogScaleMinusMovingAverage = datasetLogScaleMinusMovingAverage.replace([np.nan, -np.inf, np.inf], np.nan)
                    mean_value = datasetLogScaleMinusMovingAverage.mean()
                    datasetLogScaleMinusMovingAverage = datasetLogScaleMinusMovingAverage.fillna(value = mean_value)

                    # timeseries plot
                    fig = px.line(datasetLogScaleMinusMovingAverage,
                    x=datasetLogScaleMinusMovingAverage.index,
                    y=datasetLogScaleMinusMovingAverage.values,
                    title = 'Log Scale Plot',
                    template = 'plotly_dark').update_layout(
                        xaxis_title="Date",
                        yaxis_title="Log",
                        showlegend = False
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    movingAverage = datasetLogScaleMinusMovingAverage.rolling(window=12).mean()
                    movingSTD = datasetLogScaleMinusMovingAverage.rolling(window=12).std()

                    # timeseries plot
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                         x=movingAverage.index,
                         y=movingAverage.values,
                         name="Moving AVG",
                    ))

                    fig.add_trace(go.Scatter(
                         x=movingSTD.index,
                         y=movingSTD.values,
                         name="Moving STD",
                    ))

                    fig.update_layout(
                         title="Moving AVG vs Moving STD",
                         xaxis_title="Date",
                         yaxis_title="Log",
                         legend_title="Legend",
                         font=dict(
                              family="Courier New, monospace",
                              size=18,
                              color="RebeccaPurple"
                         )
                         )


                    # fig = px.line(movingAverage,
                    # x=movingAverage.index,
                    # y=movingAverage.values,
                    # title = 'Moving Average vs Moving STD',
                    # template = 'plotly_dark').update_layout(
                    #     xaxis_title="Date",
                    #     yaxis_title="Log",
                    #     showlegend = True
                    # )
                    # fig.add_scatter(x=movingSTD.index, y=movingSTD.values, mode='lines')

                    st.plotly_chart(fig, use_container_width=True)

                    # adfuller test
                    dftest = adfuller(datasetLogScaleMinusMovingAverage, autolag='AIC')
                    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
                    for key,value in dftest[4].items():
                        dfoutput['Critical Value (%s)'%key] = value
                    dfoutput = pd.DataFrame(dfoutput)
                    dfoutput.columns = ['Nilai']

                    st.subheader("Adfuller Test")
                    st.dataframe(dfoutput)
                    st.write("""
                            Syarat stasioner uji adfuller:
                            1. p-value harus sekecil mungkin
                            2. critical-values 1%, 5%, 10% harus sedekat mungkin dengan nilai test statistic
                            Jika tidak terpenuhi maka harus dilakukan transformasi data (agar stasioner)
                            """)
                    
                    st.session_state.df_transform1 = datasetLogScaleMinusMovingAverage.copy(deep=True)

                    if st.button("Lanjut Dekomposisi"):
                        st.session_state.lanjut_dekomposisi = 1


            if st.session_state.lanjut_dekomposisi == 1:
                decomposition = seasonal_decompose(st.session_state.df_transform1) 

                trend = decomposition.trend
                seasonal = decomposition.seasonal
                residual = decomposition.resid

                from plotly.subplots import make_subplots
                import plotly.graph_objects as go

                fig = make_subplots(rows=4, subplot_titles=("Original", "Trend", "Seasonality", "Residuals"))

                fig.add_scatter(y=st.session_state.df_transform1.values, row=1, col=1) 
                fig.add_scatter(y=trend, row=2, col=1)
                fig.add_scatter(y=seasonal, row=3, col=1)
                fig.add_scatter(y=residual, row=4, col=1)

                fig.update_layout(width = 1100, height = 800, title = 'Seasonal Decomposition', showlegend=False)

                st.plotly_chart(fig, use_container_width=True)

                mean_value = residual.mean()
                residual = residual.replace([np.nan, -np.inf, np.inf], np.nan)
                residual = residual.fillna(value = mean_value)

                # adfuller test
                dftest = adfuller(residual, autolag='AIC')
                dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
                for key,value in dftest[4].items():
                    dfoutput['Critical Value (%s)'%key] = value
                dfoutput = pd.DataFrame(dfoutput)
                dfoutput.columns = ['Nilai']

                st.subheader("Adfuller Test")
                st.dataframe(dfoutput)
                st.write("""
                            Syarat stasioner uji adfuller:
                            1. p-value harus sekecil mungkin
                            2. critical-values 1%, 5%, 10% harus sedekat mungkin dengan nilai test statistic
                            Jika tidak terpenuhi maka harus dilakukan transformasi data (agar stasioner)
                            """)            

                if st.button("Lanjut ACF & PCF"):
                     st.session_state.lanjut_acfpcf = 1   

            if st.session_state.lanjut_acfpcf == 1:
                lag_acf = acf(st.session_state.df_transform1, nlags=20)
                lag_pacf = pacf(st.session_state.df_transform1, nlags=20, method='ols')

                from plotly.subplots import make_subplots
                import plotly.graph_objects as go

                fig = make_subplots(rows=2, subplot_titles=("ACF", "PACF"))

                fig.add_scatter(y=lag_acf, row=1, col=1) 
                fig.add_scatter(y=[0] * len(lag_acf), row=1, col=1) 
                fig.add_scatter(y=[-1.96/np.sqrt(len(st.session_state.df_transform1))] * len(lag_acf), row=1, col=1) 
                fig.add_scatter(y=[1.96/np.sqrt(len(st.session_state.df_transform1))] * len(lag_acf), row=1, col=1) 


                fig.add_scatter(y=lag_pacf, row=2, col=1)
                fig.add_scatter(y=[0] * len(lag_pacf), row=2, col=1) 
                fig.add_scatter(y=[-1.96/np.sqrt(len(st.session_state.df_transform1))] * len(lag_pacf), row=2, col=1) 
                fig.add_scatter(y=[1.96/np.sqrt(len(st.session_state.df_transform1))] * len(lag_pacf), row=2, col=1) 

                fig.update_layout(width = 1100, height = 800, title = 'ACF vs PACF', showlegend=False)

                st.plotly_chart(fig, use_container_width=True)

                st.write("""
                            Nilai q (autoregressive:AR --> Number of lagged forecast errors in the prediction equation) ditentukan berdasarkan ACF dimana nilai x ketika nilai y pertama kali melewati titik 0.
                         """)
                
                st.write("""
                            Nilai d (integrated:I --> Number of nonseasonal differences needed for stationarity) ditentukan berdasarkan jumlah diff untuk mencapai nilai stasioner.
                         """)
                

                st.write("""
                            Nilai p (moving average:MA --> Number of autoregressive terms) ditentukan berdasarkan PACF dimana nilai x ketika nilai y pertama kali melewati titik 0.
                         """)
                
                st.write("order = (p,d,q)")

                if st.button("Lanjut Pemodelan Arima"):
                     st.session_state.lanjut_pemodelan_arima = 1
                
            if st.session_state.lanjut_pemodelan_arima == 1:

                persentase_train = st.number_input("Persentase Training", min_value = 0, step=10) / 100

                train, test = st.session_state.df_latih.iloc[:int(persentase_train * len(st.session_state.df_latih))], st.session_state.df_latih.iloc[int(persentase_train * len(st.session_state.df_latih)):,]

                p = st.number_input("Pilih p:", min_value = 0, step=1, key=1)
                d = st.number_input("Pilih d:", min_value = 0, step=1, key=2)
                q = st.number_input("Pilih q:", min_value = 0, step=1, key=3)

                if 'model_arima' not in st.session_state :
                    st.session_state.model_arima = sm.tsa.arima.ARIMA(train, order = (1, 1, 1))

                if st.button("Latih ARIMA"):
                    st.session_state.model_arima = sm.tsa.arima.ARIMA(train, order = (p, d, q))
                    st.session_state.model_arima = st.session_state.model_arima.fit()

                    pred = st.session_state.model_arima.predict(start=test.index[0], end=test.index[-1])
                    df_plot = pd.concat([pd.DataFrame({"train": train}), pd.DataFrame({"test": test}), pd.DataFrame({"pred": pred})])

                    title = type_ + ' ' + type_n + ' ' + col_

                    fig = px.line(df_plot,
                                        x=df_plot.index,
                                        y=df_plot.columns,
                                        title = title,
                                        template = 'plotly_dark').update_layout(
                                            xaxis_title="Date",
                                            yaxis_title="Kbps",
                                        )
                    st.plotly_chart(fig, use_container_width=True)

                    test_ = pd.read_html(st.session_state.model_arima.summary().tables[2].as_html(),header=None,index_col=0)[0]

                    st.write(test_[1])

                    def rmse(predictions, targets):
                        return np.sqrt(((predictions - targets) ** 2).mean())
                    
                    model_rmse = rmse(pred, test.values)
                    st.write('RMSE ARIMA: ', model_rmse)

                                        # Define the function to return the MAPE values 
                    def calculate_mape(actual, predicted) -> float: 
                    
                        # Convert actual and predicted 
                        # to numpy array data type if not already 
                        if not all([isinstance(actual, np.ndarray), 
                                    isinstance(predicted, np.ndarray)]): 
                            actual, predicted = np.array(actual),  
                            np.array(predicted) 
                    
                        # Calculate the MAPE value and return 
                        return round(np.mean(np.abs(( 
                        actual - predicted) / actual)) * 100, 2)
                    
                    st.write('MAPE ARIMA: ', calculate_mape(test.values, pred.values), "%")

    if menu0 == "Choose" and menu1 == "HOLT-WINTERS" and menu2 == "Choose":
            
            loc = st.selectbox("Pilih Lokasi", sorted(st.session_state.location))
            split_cols = [item.split('__') for item in st.session_state.cols]

            lay_ = [item[1] for item in split_cols if item[0] == loc]
            lay_ = np.array(lay_)
            lay_ = np.unique(lay_)
            lay = lay_[0]
          #   lay = st.selectbox("Pilih Layanan", sorted(lay_))

            lin_ = [item[2] for item in split_cols if (item[0] == loc and item[1] == lay)]
            lin_ = np.array(lin_)
            lin_ = np.unique(lin_)
            lin = lin_[0]
          #   lin = st.selectbox("Pilih Link", lin_)

            ban_ = [item[3] for item in split_cols if (item[0] == loc and item[1] == lay and item[2] == lin)]
            ban_ = np.array(ban_)
            ban_ = np.unique(ban_)
            ban_ = sorted(ban_)
            ban = ban_[0]
          #   ban = st.selectbox("Pilih Bandwidth", ban_)

            col_ = loc + '__' + lay + '__' + lin + '__' + str(ban)

          #   type_ = st.selectbox("Pilih Transmiter atau Receiver", ["Transmiter", "Receiver"])
          #   type_n = st.selectbox("Pilih Peak atau Average", ["Peak", "Average"])
            type_ = "Receiver"
            type_n = "Peak"
            num = 0

            if 'pilih_data_latih' not in st.session_state:
                 st.session_state.pilih_data_latih = 0

            
            if st.button("Pilih Data Latih"):
                 st.session_state.pilih_data_latih = 1

            if st.session_state.pilih_data_latih == 1:
                if type_ + ' ' + type_n == 'Peak Transmit':
                     num = 0
                if type_ + ' ' + type_n == 'Average Transmit':
                     num = 1
                if type_ + ' ' + type_n == 'Peak Receive':
                     num = 2
                if type_ + ' ' + type_n == 'Average Receive':
                     num = 3

                df = st.session_state.data[st.session_state.data.index.isin(list(range(num,len(st.session_state.data), 4)))]
                df = df.reset_index()
                df = df.drop(['index'], axis=1)
                df.index = pd.date_range(start="2023-05-01",end="2023-11-30")
                df = df.fillna(method='bfill')
                df = df[col_]

                df = df.resample('D').mean()
                df = df.fillna(df.mean())
                st.session_state.df_latih = df.copy(deep=True)

                persentase_train = st.number_input("Persentase Training", min_value = 0, step=10) / 100

                train, test = st.session_state.df_latih.iloc[:int(persentase_train * len(st.session_state.df_latih))], df.iloc[int(persentase_train * len(st.session_state.df_latih)):,]

                if 'model_holt_winter' not in st.session_state:
                    model_holt_winter = ExponentialSmoothing(train,trend='additive', seasonal_periods = 12)
                    st.session_state.model_holt_winter = model_holt_winter.fit(smoothing_level=0.5, smoothing_slope=0.01, optimized=False)
                
                if st.button("Latih HOLT-WINTERS"):
                    smoothing_l = st.number_input("Masukkan Smoothing Level:", min_value = 0.1, step=0.1)
                    smoothing_s = st.number_input("Masukkan Smoothing Slope:", min_value = 0.01, step=0.01)
                                    
                    model_holt_winter = ExponentialSmoothing(train, trend='additive', seasonal_periods = 12)
                    st.session_state.model_holt_winter = model_holt_winter.fit(smoothing_level=smoothing_l, smoothing_slope=smoothing_s, optimized=True, remove_bias = True)


                    pred = st.session_state.model_holt_winter.predict(start=test.index[0], end=test.index[-1])
                    df_plot = pd.concat([pd.DataFrame({"train": train}), pd.DataFrame({"test": test}), pd.DataFrame({"pred": pred})])

                    title = type_ + ' ' + type_n + ' ' + col_

                    fig = px.line(df_plot,
                                        x=df_plot.index,
                                        y=df_plot.columns,
                                        title = title,
                                        template = 'plotly_dark').update_layout(
                                            xaxis_title="Date",
                                            yaxis_title="Kbps",
                                        )
                    st.plotly_chart(fig, use_container_width=True)

                    def rmse(predictions, targets):
                        return np.sqrt(((predictions - targets) ** 2).mean())
                        
                    model_rmse = rmse(pred, test)
                    st.write('RMSE HOLT-WINTERS: ', model_rmse)

                    # Define the function to return the MAPE values 
                    def calculate_mape(actual, predicted) -> float: 
                    
                        # Convert actual and predicted 
                        # to numpy array data type if not already 
                        if not all([isinstance(actual, np.ndarray), 
                                    isinstance(predicted, np.ndarray)]): 
                            actual, predicted = np.array(actual),  
                            np.array(predicted) 
                    
                        # Calculate the MAPE value and return 
                        return round(np.mean(np.abs(( 
                        actual - predicted) / actual)) * 100, 2)
                    
                    st.write('MAPE HOLT-WINTERS: ', calculate_mape(test.values, pred.values), "%")


    if menu0 == "Choose" and menu1 == "Choose" and menu2 == "FORECASTING":

        metode = st.selectbox("Pilih Metode", ["ARIMA", "HOLT-WINTERS"])
        if metode == "ARIMA":
            duration = st.number_input("Masukkan Jumlah Hari ke Depan", min_value = 1, step = 1)
            start = 214
            end = start + int(duration)

            pred = st.session_state.model_arima.forecast(duration)

            df_plot = pd.DataFrame({"future prediction": pred})

            st.dataframe(df_plot)

            fig = px.line(df_plot,
                        x=df_plot.index,
                        y=df_plot.columns,
                        title = st.session_state.title,
                        template = 'plotly_dark').update_layout(
                            xaxis_title="Date",
                            yaxis_title="Kbps",
                        )

            st.plotly_chart(fig, use_container_width=True)
        if metode == "HOLT-WINTERS":
            duration = st.number_input("Masukkan Jumlah Hari ke Depan", min_value = 1, step = 1)

            pred = st.session_state.model_holt_winter.forecast(duration)

            df_plot = pd.DataFrame({"future prediction": pred})

            st.dataframe(df_plot)

            fig = px.line(df_plot,
                        x=df_plot.index,
                        y=df_plot.columns,
                        title = st.session_state.title,
                        template = 'plotly_dark').update_layout(
                            xaxis_title="Date",
                            yaxis_title="Kbps",
                        )

            st.plotly_chart(fig, use_container_width=True)


# Running program
if __name__ == "__main__":
    main()