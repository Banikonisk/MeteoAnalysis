import requests
import pandas as pd
import time
import sys
from helper_functions import convert_to_df, validate_dates


class MeteoAPI:
    """Read historical and forecasted data from Meteo API."""
    TIME_ZONE = 2

    def __init__(self, place_code, station_code, url):
        """Initializes MeteoAPI object.
        Args:
            place_code (str): place code for forecasted data
            station_code (str): station code for historical data
            url (str): address of Meteo API
        """
        self.place_code = place_code
        self.station_code = station_code
        self.url = url

    def get_request(self, full_url, var_name):
        """Retrieve data from API.
        Args:
            full_url (str): url with specific endpoint for Meteo API
            var_name (str): variable name to extract observations (observations|forecastTimestamps)
        Returns:
            data (list): response data from API in JSON format
        Raises:
            requests.RequestException: if exception happens while handling request
        """
        try:
            response = requests.get(full_url)
            time.sleep(0.35)
            response.raise_for_status()
            data = response.json()[f"{var_name}"]
            return data
        except requests.RequestException as e:
            print(f"Error: {e}")
            sys.exit(1)

    def get_historical_data(self, start_date, end_date):
        """Get historical data in specified date range from Meteo API.
        Args:
            start_date (str): start of interval for collecting data
            end_date (str): end of interval for collecting data
        Returns:
            df (pd.DataFrame): historical data in specified date range
        """
        if (not validate_dates(start_date, end_date)):
            sys.exit(1)
        data = []
        date_list = [date.strftime('%Y-%m-%d') for date in pd.date_range(
            pd.to_datetime(start_date) - pd.Timedelta(days=1), end_date, freq='D')]
        for date in date_list:
            full_url = f"{
                self.url}stations/{self.station_code}/observations/{date}"
            single_day_data = self.get_request(full_url, "observations")
            data.extend(single_day_data)
        df = convert_to_df(data, "observationTimeUtc")
        df = df.iloc[24-self.TIME_ZONE:]
        if df.index[-(self.TIME_ZONE+1)].date() != pd.Timestamp.today().normalize().date():
            df = df.iloc[:-self.TIME_ZONE]
        return df

    def get_forecast(self):
        """Get forecasted data from Meteo API.
        Returns:
            df (pd.DataFrame): forecasted data
        """
        full_url = f"{self.url}places/{self.place_code}/forecasts/long-term"
        forecast = self.get_request(full_url, "forecastTimestamps")
        df = convert_to_df(forecast, "forecastTimeUtc")
        return df
