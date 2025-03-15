import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# OpenWeatherMap API Key
API_KEY = "e0100edeedd99f5ae298581c486626a4"

# Function to get coordinates from city name using OpenWeatherMap
def get_coordinates(city_name):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        location_data = response.json()
        if location_data:
            location = location_data[0]
            return location['lat'], location['lon']
        else:
            st.warning("City not found. Please check the spelling or try adding the country name (e.g., 'San Francisco, USA').")
            return None, None
    else:
        st.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None, None

# Function to get weather data from OpenWeatherMap
def get_weather_data(lat, lon, hours):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,daily&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Extract hourly data for the next `hours` hours
        hourly_data = data['hourly'][:hours]
        return hourly_data
    else:
        st.error("Failed to retrieve data")
        return None

# Streamlit UI for downloading dataset
def download_dataset():
    st.title("Download Weather Dataset")
    city_name = st.text_input("Enter City Name")
    forecast_duration = st.slider("Select Forecast Duration (Hours)", min_value=12, max_value=48, value=24, step=12)

    if st.button("Get Weather Data"):
        lat, lon = get_coordinates(city_name)
        if lat and lon:
            data = get_weather_data(lat, lon, forecast_duration)
            if data:
                times = [datetime.now() + timedelta(hours=i) for i in range(forecast_duration)]
                df = pd.DataFrame({
                    "Time": times,
                    "temperature": [hour['temp'] for hour in data],
                    "humidity": [hour['humidity'] for hour in data],
                    "pressure": [hour['pressure'] for hour in data],
                    "precipitation": [hour.get('rain', {}).get('1h', 0) for hour in data],  # Precipitation (rain)
                    "cloud_cover": [hour['clouds'] for hour in data],
                    "wind_speed": [hour['wind_speed'] for hour in data],
                    "wind_direction": [hour['wind_deg'] for hour in data]
                })
                st.write(df)
                st.download_button(
                    label="Download Dataset as CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name="weather_data.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    download_dataset()
