import requests
import pandas as pd
import time
import sys


def convert_to_df(data, index_name):
    """Convert JSON data to DataFrame, set index, change time zone.
    Args:
        data (list): retrieved JSON data from API
        index_name (str): Timestamp name in Meteo API (observationTimeUtc|forecastTimeUtc)
    Returns:
        data (pd.DataFrame): converted data to DataFrame format
    """
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df[f"{index_name}"]).dt.tz_localize('UTC')
    df['time'] = df['time'].dt.tz_convert('Etc/GMT-2')
    df.set_index('time', inplace=True)
    df.drop(f"{index_name}", axis=1, inplace=True)
    return df


def validate_dates(start_date, end_date):
    """Validate input for start and end dates.
    Args:
        start_date (str): start of interval for collecting data
        end_date (str): end of interval for collecting data
    Returns:
        True, if dates are valid
        False, if dates are not valid
    """
    try:
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
    except Exception as e:
        print(f"Error: {e}")
        return False
    if start_date >= end_date:
        print("Error: start date must be earlier than end date")
        return False
    today = pd.Timestamp.today().normalize().date()
    if start_date >= today:
        print("Error: start date must be earlier than today")
        return False
    if end_date > today:
        print("Error: end date must not be later than today")
        return False
    return True


class MeteoAPI:
    """Read historical and forecasted data from Meteo API."""

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
        """Get historical data in date range from Meteo API.
        Args:
            start_date (str): start of interval
            end_date (str): end of interval
        Returns:
            df (pd.DataFrame): historical data in specified date range
        """
        if (not validate_dates(start_date, end_date)):
            sys.exit(1)
        data = []
        date_list = [date.strftime('%Y-%m-%d') for date in pd.date_range(
            pd.to_datetime(start_date) - pd.Timedelta(days=1), end_date, freq='D')]
        for date in date_list:
            full_url = f"{self.url}stations/{self.station_code}/observations/{date}"
            single_day_data = self.get_request(full_url, "observations")
            data.extend(single_day_data)
        df = convert_to_df(data, "observationTimeUtc")
        time_zone = int(df.index.tz.utcoffset(df.index).total_seconds() / 3600)
        df = df.iloc[24-time_zone:]
        if df.index[-(time_zone+1)].date() != pd.Timestamp.today().normalize().date():
            df = df.iloc[:time_zone]
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
