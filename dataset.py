import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# OpenWeatherMap API Key
API_KEY = "e0100edeedd99f5ae298581c486626a4"

# List of cities (you can expand this list or load from a CSV file)
CITIES = [
    "New York, US", "London, GB", "Tokyo, JP", "Paris, FR", "Berlin, DE",
    "Mumbai, IN", "Sydney, AU", "Beijing, CN", "Moscow, RU", "Cairo, EG",
    "São Paulo, BR", "Toronto, CA", "Dubai, AE", "Singapore, SG", "Mexico City, MX",
    "Los Angeles, US", "Chicago, US", "Houston, US", "Phoenix, US", "Philadelphia, US",
    "San Francisco, US", "Miami, US", "Shanghai, CN", "Delhi, IN", "Bangkok, TH",
    "Istanbul, TR", "Karachi, PK", "Dhaka, BD", "Rio de Janeiro, BR", "Jakarta, ID",
    "Lagos, NG", "Kolkata, IN", "Manila, PH", "Seoul, KR", "Kinshasa, CD",
    "Lima, PE", "Bogotá, CO", "Hong Kong, HK", "Madrid, ES", "Barcelona, ES",
    "Rome, IT", "Milan, IT", "Amsterdam, NL", "Brussels, BE", "Vienna, AT",
    "Prague, CZ", "Warsaw, PL", "Budapest, HU", "Athens, GR", "Lisbon, PT",
    "Stockholm, SE", "Copenhagen, DK", "Helsinki, FI", "Oslo, NO", "Zurich, CH",
    "Geneva, CH", "Dublin, IE", "Edinburgh, GB", "Manchester, GB", "Birmingham, GB",
    "Glasgow, GB", "Melbourne, AU", "Brisbane, AU", "Perth, AU", "Auckland, NZ",
    "Wellington, NZ", "Johannesburg, ZA", "Cape Town, ZA", "Nairobi, KE", "Casablanca, MA",
    "Riyadh, SA", "Doha, QA", "Kuwait City, KW", "Muscat, OM", "Abu Dhabi, AE",
    "Tel Aviv, IL", "Jerusalem, IL", "Baghdad, IQ", "Tehran, IR", "Kabul, AF",
    "Islamabad, PK", "Colombo, LK", "Kathmandu, NP", "Dhaka, BD", "Yangon, MM",
    "Hanoi, VN", "Ho Chi Minh City, VN", "Bangkok, TH", "Kuala Lumpur, MY",
    "Manila, PH", "Phnom Penh, KH", "Vientiane, LA", "Ulaanbaatar, MN", "Seoul, KR",
    "Pyongyang, KP", "Tokyo, JP", "Osaka, JP", "Kyoto, JP", "Nagoya, JP",
    "Sapporo, JP", "Fukuoka, JP", "Hiroshima, JP", "Sendai, JP", "Yokohama, JP",
    "Beijing, CN", "Shanghai, CN", "Guangzhou, CN", "Shenzhen, CN", "Chengdu, CN",
    "Chongqing, CN", "Tianjin, CN", "Wuhan, CN", "Nanjing, CN", "Hangzhou, CN",
    "Xi'an, CN", "Shenyang, CN", "Harbin, CN", "Hong Kong, HK", "Macau, MO",
    "Taipei, TW", "Kaohsiung, TW", "Taichung, TW", "Tainan, TW", "New Taipei, TW",
    "Seoul, KR", "Busan, KR", "Incheon, KR", "Daegu, KR", "Daejeon, KR",
    "Gwangju, KR", "Ulsan, KR", "Suwon, KR", "Changwon, KR", "Seongnam, KR",
    "Tokyo, JP", "Osaka, JP", "Nagoya, JP", "Sapporo, JP", "Fukuoka, JP",
    "Kobe, JP", "Kyoto, JP", "Yokohama, JP", "Kawasaki, JP", "Saitama, JP"
]


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
            st.warning(f"City not found: {city_name}. Please check the spelling or try adding the country name.")
            return None, None
    else:
        st.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None, None

# Function to get weather data from OpenWeatherMap
def get_weather_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['list']  # Returns 5-day forecast in 3-hour intervals
    else:
        st.error(f"Failed to retrieve data for lat={lat}, lon={lon}: {response.status_code} - {response.text}")
        return None

# Function to save data to a CSV file incrementally
def save_data_to_csv(data, filename="large_weather_dataset.csv"):
    if not os.path.exists(filename):
        # Create a new CSV file with headers
        pd.DataFrame(data).to_csv(filename, index=False)
    else:
        # Append data to the existing CSV file
        pd.DataFrame(data).to_csv(filename, mode='a', header=False, index=False)

# Streamlit UI for downloading dataset
def download_large_dataset():
    st.title("Build Large Weather Dataset")
    st.write("This tool fetches weather data for multiple cities to build a large dataset for machine learning.")

    if st.button("Start Building Dataset"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_cities = len(CITIES)
        all_data = []

        for i, city in enumerate(CITIES):
            status_text.text(f"Fetching data for {city} ({i + 1}/{total_cities})...")
            lat, lon = get_coordinates(city)
            if lat and lon:
                weather_data = get_weather_data(lat, lon)
                if weather_data:
                    for hour in weather_data:
                        all_data.append({
                            "city": city,
                            "time": datetime.fromtimestamp(hour['dt']),
                            "temperature": hour['main']['temp'],
                            "humidity": hour['main']['humidity'],
                            "pressure": hour['main']['pressure'],
                            "precipitation": hour.get('rain', {}).get('3h', 0),
                            "cloud_cover": hour['clouds']['all'],
                            "wind_speed": hour['wind']['speed'],
                            "wind_direction": hour['wind']['deg']
                        })
            progress_bar.progress((i + 1) / total_cities)
            time.sleep(1)  # Add delay to avoid hitting API rate limits

        # Save data to CSV
        save_data_to_csv(all_data)
        st.success(f"Dataset created successfully! Total records: {len(all_data)}")
        st.download_button(
            label="Download Dataset as CSV",
            data=pd.DataFrame(all_data).to_csv(index=False).encode('utf-8'),
            file_name="large_weather_dataset.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    download_large_dataset()
