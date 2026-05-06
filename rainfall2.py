import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(page_title="Rainfall Tracker", page_icon="🌧️", layout="wide")
st.title("🌧️ Historical Rainfall Tracker")
st.markdown("Pull daily rainfall data for any location using the free Open-Meteo API.")

# --- Sidebar Controls ---
st.sidebar.header("📍 Location Setup")
st.sidebar.markdown("Enter the coordinates for your target location.")

# Defaulting to Sea Point coordinates as a starting point
lat = st.sidebar.number_input("Latitude", value=-33.9180, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=18.3880, format="%.4f")

st.sidebar.header("📅 Date Range")
# Default to the last 30 days
default_start = datetime.today() - timedelta(days=30)
start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=datetime.today())

# --- Main App Logic ---
if st.sidebar.button("Fetch Rainfall Data", type="primary"):
    
    if start_date > end_date:
        st.error("Error: Start Date must be before End Date.")
    else:
        with st.spinner("Fetching data from Open-Meteo..."):
            # API Setup
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "daily": "precipitation_sum",
                "timezone": "Africa/Johannesburg"
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                daily_data = data.get('daily', {})
                
                # Build DataFrame
                df = pd.DataFrame({
                    'Date': pd.Series(pd.to_datetime(daily_data['time'])).dt.date,
                    'Rainfall (mm)': daily_data['precipitation_sum']
                })
                
                # --- Dashboard Display ---
                total_rain = df['Rainfall (mm)'].sum()
                max_rain = df['Rainfall (mm)'].max()
                
                # Top Level Metrics
                col1, col2 = st.columns(2)
                col1.metric("Total Rainfall", f"{total_rain:.1f} mm")
                col2.metric("Highest Daily Rainfall", f"{max_rain:.1f} mm")
                
                st.divider()
                
                # Chart and Table layout
                col_chart, col_table = st.columns([2, 1])
                
                with col_chart:
                    st.subheader("Daily Rainfall")
                    # Streamlit's native bar chart works great for this
                    st.bar_chart(df.set_index('Date')['Rainfall (mm)'], color="#1f77b4")
                
                with col_table:
                    st.subheader("Raw Data")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download Button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Data as CSV",
                        data=csv,
                        file_name=f"rainfall_{start_date}_to_{end_date}.csv",
                        mime="text/csv",
                    )
            else:
                st.error(f"Failed to fetch data. API returned status code: {response.status_code}")