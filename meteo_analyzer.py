import sys
import warnings


class MeteoAnalyzer:
    """Calculates various metrics with Meteo API data"""

    def __init__(self, meteo_api, start_date, end_date):
        """Initializes MeteoAnalyzer object and fetches data from API.
        Args:
            meteo_api (MeteoAPI): API to retrieve data from
            start_date (str): start of interval for collecting data
            end_date (str): end of interval for collecting data
        """
        self.meteo_api = meteo_api
        self.start_date = start_date
        self.end_date = end_date
        self.h_data = None
        self.f_data = None

    def fetch_hist_data(self):
        """Fetches historical data from API ranging between set dates."""
        self.h_data = self.meteo_api.get_historical_data(
            self.start_date, self.end_date)

    def fetch_forecast_data(self):
        """Fetches forecasted data from API."""
        self.f_data = self.meteo_api.get_forecast()

    def get_hist_metric(self, metric):
        """Get specific metric from historical df
        Args:
            metric (str): weather metric, refer to Meteo API
        Returns:
            data (pd.Series): specific metric of historical df
        """
        try:
            data = self.h_data[f"{metric}"]
            return data
        except KeyError:
            print(f"Metric {metric} does not exist in historical data.")
            sys.exit(2)

    def get_forecast_metric(self, metric):
        """Get specific metric from forecast df
        Args:
            metric (str): weather metric, refer to Meteo API
        Returns:
            data (pd.Series): specific metric of forecast df
        """
        try:
            data = self.f_data[f"{metric}"]
            return data
        except KeyError:
            print(f"Metric {metric} does not exist in forecast data.")
            sys.exit(2)

    def calculate_hist_day_mean(self, metric):
        """Calculates mean value of specified metric during day.
        Args:
            metric (str): weather metric, refer to Meteo API
        Returns:
            result (float): mean value of metric during day
        """
        result = self.get_hist_metric(metric)[
            (self.h_data.index.hour >= 8) & (self.h_data.index.hour <= 20)
        ].mean()
        return result

    def calculate_hist_night_mean(self, metric):
        """Calculates mean value of specified metric during night.
        Args:
            metric (str): weather metric, refer to Meteo API
        Returns:
            result (float): mean value of metric during night
        """
        result = self.get_hist_metric(metric)[
            (self.h_data.index.hour < 8) | (self.h_data.index.hour > 20)
        ].mean()
        return result

    def calculate_rainy_weekends(self):
        """Calculates amount of weekends that had rain for atleast an hour.
        Returns:
            result (int): amount of rainy weekends
        """
        with warnings.catch_warnings():  # Ignore timezone being dropped
            warnings.simplefilter("ignore", UserWarning)
            self.h_data.loc[:, "week"] = self.h_data.index.to_period("W")
        weekend_data = self.h_data[self.h_data.index.weekday >= 5]
        result = weekend_data.groupby("week")["conditionCode"].apply(
            lambda x: "rain" in x.values).sum()
        return result
