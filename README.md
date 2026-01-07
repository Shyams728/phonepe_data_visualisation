# PhonePe Pulse Data Visualisation 📈

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=streamlit)](https://shyamsphonepedatavisualisation.streamlit.app/)

A comprehensive Streamlit dashboard for visualizing PhonePe Pulse data, providing insights into transactions, users, and insurance metrics across India.

![Dashboard Preview](https://raw.githubusercontent.com/Shyams728/phonepe_data_visualisation/main/visualization.png))

## 🚀 Features

- **Interactive Maps**: Visualize transaction and user data geographically across Indian states and districts.
- **Top Charts**: Identify leading states, districts, and pincodes for various metrics.
- **Trend Analysis**: Track growth and patterns over years and quarters.
- **Custom KPIs**: High-level metrics for quick insights into total amounts, transaction counts, and user bases.
- **District Drill-down**: Detailed analysis at the district level within states.
- **Phone Brand Insights**: Market share analysis of mobile brands used for transactions.

## 🛠️ Tech Stack

- **Frontend/App**: [Streamlit](https://streamlit.io/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Visualizations**: [Plotly](https://plotly.com/python/)
- **Database**: SQLite (SQLAlchemy)
- **Mapping**: Geopandas

## 📋 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Shyams728/phonepe_data_visualisation.git
   cd phonepe_data_visualisation
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Usage

Run the Streamlit application:
```bash
streamlit run Main.py
```

## 📊 Data Source

The data used in this dashboard is sourced from the [PhonePe Pulse GitHub Repository](https://github.com/PhonePe/pulse).

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
