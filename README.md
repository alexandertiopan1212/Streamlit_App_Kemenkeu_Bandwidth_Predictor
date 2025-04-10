
WINTERIMA - Bandwidth Forecasting App for Kemenkeu Regional Offices

WINTERIMA is a Streamlit-based forecasting dashboard developed to help BPPK - Kementerian Keuangan Republik Indonesia predict bandwidth capacity needs across regional offices using ARIMA and Holt-Winters methods. This project enables interactive exploration, time series analysis, and future capacity forecasting from historical utilization data.

==================================================
🚀 Features
==================================================
- 📁 Data Upload Interface
  Upload and parse Excel-based historical bandwidth utilization reports (Mei–November 2023).

- 📈 Interactive Time Series Visualization
  Analyze peak/average usage by location, service, and link across various time granularities (daily, weekly, monthly, quarterly).

- 🔍 Stationarity Test & Decomposition
  Automatically test for stationarity using Augmented Dickey-Fuller (ADF), apply log transformation, and decompose trends, seasonality, and residuals.

- 🧠 Model Training
  Train ARIMA and Holt-Winters models on selected time series, complete with:
    - ACF/PACF analysis
    - RMSE & MAPE evaluation metrics
    - Adjustable model parameters (p, d, q / smoothing level)

- 📊 Forecasting Module
  Predict future bandwidth usage over a specified period using the trained model.

==================================================
📂 File Structure
==================================================
📦 Streamlit_App_Kemenkeu_Bandwidth_Predictor
├── main.py                      # Main Streamlit application
├── requirements.txt             # Python dependencies
├── Utilisasi Harian BPPK...xlsx # Sample input dataset
├── Seal_of_the_Ministry...png   # App logo
└── README.txt                   # Documentation

==================================================
🛠️ Tech Stack
==================================================
- Python
- Streamlit
- pandas, numpy
- statsmodels
- scikit-learn
- plotly, matplotlib

==================================================
📦 Installation
==================================================
1. Clone the repository:
   git clone https://github.com/alexandertiopan1212/Streamlit_App_Kemenkeu_Bandwidth_Predictor.git
   cd Streamlit_App_Kemenkeu_Bandwidth_Predictor

2. Install dependencies:
   pip install -r requirements.txt

3. Run the app:
   streamlit run main.py

==================================================
📊 Sample Dataset Format
==================================================
| Lokasi | Layanan | Link | Bandwidth (Mbps) | 01-May-2023 | ... | 30-Nov-2023 |
|--------|---------|------|------------------|--------------|-----|--------------|
| Kanwil X | Internet | FO-01 | 20 | 1234 | ... | 1823 |

Sheet 1 contains metadata, Sheet 2 contains utilization data.

==================================================
🧪 Example Output
==================================================
- Time series bandwidth usage over time
- Boxplots per day/week/month/quarter
- Forecast plot of future utilization
- Model evaluation: RMSE, MAPE

==================================================
🪪 License
==================================================
This project is open-source and free to use under the MIT License.
Developed for research and internal planning purposes within the Ministry of Finance (BPPK).

==================================================
📬 Contact
==================================================
Developer: Alexander Tiopan
Email: alexandertiopan1212@gmail.com
LinkedIn: linkedin.com/in/alexandertiopan

Built with 💻 and ❤️ for better public sector decision making.
