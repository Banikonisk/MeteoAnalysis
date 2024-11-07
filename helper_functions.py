import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


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


def get_today_str():
    """Get today's date in string format.
    Returns:
        today's date in string format
    """
    today = datetime.today()
    return today.strftime('%Y-%m-%d')


def get_n_years_from_today_str(n):
    """Get date which is specified amount of years before today.
    Args:
        n (int): amount of years
    Returns:
        date (str): date n years before today
    """
    today = datetime.today()
    date = today.replace(year=today.year - n).strftime('%Y-%m-%d')
    return date


def get_n_last_days(hist_data, n):
    """Get n amount of last days from series with hourly frequency.
    Args:
        hist_data (pd.Series): series from which to take last days
        n (int): amount of days
    Returns:
        pd.Series, with specified amount of last days
    """
    return hist_data.tail(n * 24)


def cut_forecast_start(hist_data, forecast):
    """Make forecast series follow one hour later than historical.
    Args:
        hist_data (pd.Series): historical data
        forecast (pd.Series): forecasted data
    Returns:
        pd.Series, with cut forecast observations from the start 
    """
    difference = hist_data.index[-1].hour - forecast.index[0].hour + 1
    if difference > 0:
        forecast = forecast.tail(-difference)
    return forecast


def plot_ts(ts_historical, ts_forecast):
    """Plot two time series with sequential DateTimeIndex
    Args:
        ts_historical (pd.Series): historical data
        ts_forecast (pd.Series): forecasted data
    """
    plt.figure(figsize=(10, 6))
    ts_historical.plot(label='Historical', color='green')
    ts_forecast.plot(label='Forecasted', color='orange', linestyle='--')
    plt.title('Historical and forecasted temperature plot')
    plt.xlabel('Time')
    plt.ylabel('Temperature')
    plt.legend()
    plt.show()


def resample_ts_to_five_min(ts):
    """Change ts frequency to 5 minutes and use linear interpolation for empty values.
    Args:
        ts (pd.Series): series to change frequency
    Returns:
        data (pd.Series): series with changed frequency
    """
    data = ts.resample('5min').mean()
    data = data.interpolate()
    return data
