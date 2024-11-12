import sys


class MeteoReceiver:
    """Calculates various metrics with Meteo API data"""

    def __init__(self, meteo_api, start_date, end_date):
        """Initializes MeteoReceiver object and fetches data from API.
        Args:
            meteo_api (MeteoAPI): API to retrieve data from
            start_date (str): start of interval for collecting data
            end_date (str): end of interval for collecting data
        """
        self.meteo_api = meteo_api
        self.start_date = start_date
        self.end_date = end_date
        self._hist_data = None
        self._forecast_data = None

    def fetch_hist_data(self):
        """Fetches historical data from API ranging between set dates."""
        self._hist_data = self.meteo_api.get_historical_data(
            self.start_date, self.end_date)

    def fetch_forecast_data(self):
        """Fetches forecasted data from API."""
        self._forecast_data = self.meteo_api.get_forecast()

    @property
    def hist_data(self):
        if self._hist_data is not None:
            return self._hist_data
        else:
            print("Error: no historical data.")
            sys.exit(3)

    @property
    def forecast_data(self):
        if self._forecast_data is not None:
            return self._forecast_data
        else:
            print("Error: no forecast data.")
            sys.exit(3)

    def get_hist_metric(self, metric):
        """Get specific metric from historical df
        Args:
            metric (str): weather metric, refer to Meteo API
        Returns:
            data (pd.Series): specific metric of historical df
        """
        try:
            data = self.hist_data[f"{metric}"]
            return data
        except KeyError:
            print(f"Error: metric {metric} does not exist in historical data.")
            sys.exit(2)

    def get_forecast_metric(self, metric):
        """Get specific metric from forecast df
        Args:
            metric (str): weather metric, refer to Meteo API
        Returns:
            data (pd.Series): specific metric of forecast df
        """
        try:
            data = self.forecast_data[f"{metric}"]
            return data
        except KeyError:
            print(f"Error: metric {metric} does not exist in forecast data.")
            sys.exit(2)
