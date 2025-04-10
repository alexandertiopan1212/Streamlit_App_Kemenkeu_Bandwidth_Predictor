# WINTERIMA: Bandwidth Forecasting App for Regional Offices

**WINTERIMA** (Winter + ARIMA) is a Streamlit-based forecasting tool designed for the Indonesian Ministry of Finance to analyze and predict regional office bandwidth needs using time series techniques (ARIMA and Holt-Winters). The app is tailored for network infrastructure teams to plan bandwidth upgrades based on actual peak usage trends.

## 🚀 Features

- 📁 Upload Excel datasets with multi-dimensional headers (location, service, link, bandwidth)
- 📊 Visualize daily bandwidth usage, including:
  - Line charts
  - Box plots (daily, weekly, monthly, quarterly)
- 🔍 Time Series Analysis Workflow:
  - Augmented Dickey-Fuller Test (ADF)
  - Log transform and smoothing
  - Decomposition (trend, seasonal, residual)
  - ACF & PACF plotting
- 🧠 Forecasting Models:
  - **ARIMA**: Custom (p, d, q) + interactive ADF + decomposition
  - **Holt-Winters**: Additive smoothing (level + slope control)
- 📈 Forecast future bandwidth needs (user-defined period)
- 📦 Built-in RMSE and MAPE error metrics for model evaluation

## 📁 Project Structure

```
📦Streamlit_App_Kemenkeu_Bandwidth_Predictor
 ┣ 📜main.py
 ┣ 📜requirements.txt
 ┣ 📜Utilisasi Harian BPPK Mei - November 2023 (2).xlsx
 ┗ 📜Seal_of_the_Ministry_of_Finance_of_the_Republic_of_Indonesia.svg.png
```

## 📊 Technologies Used

- Python (Pandas, Numpy)
- Streamlit
- Plotly for interactive visualization
- statsmodels (ARIMA, ADF Test, Seasonal Decompose)
- sklearn (MAPE & RMSE)
- ExponentialSmoothing (Holt-Winters)
- pmdarima (auto ARIMA backend)

## 🛠 How to Run

```bash
pip install -r requirements.txt
streamlit run main.py
```

## 📌 Notes

- Excel template must follow two-sheet structure:
  - Sheet1: metadata (location, service, link, bandwidth)
  - Sheet2: actual bandwidth values with 4-row stacked format (Tx Peak, Tx Avg, Rx Peak, Rx Avg)
- Works best for daily-level bandwidth logging from multiple offices.

## 🪪 License

This project is intended for internal use and educational purposes only. All institutional branding belongs to the Indonesian Ministry of Finance.
