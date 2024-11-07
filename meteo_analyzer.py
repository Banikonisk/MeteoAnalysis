import sys
import pandas as pd


class MeteoAnalyzer:
    """Calculates various metrics with Meteo API data"""

    def __init__(self, meteo_api, start_date, end_date):
        """Initializes MeteoAnalyzer object and collects data from api.
        Args:
            meteo_api (MeteoAPI): api to retrieve data from
            start_date (str): start of interval for collecting data
            end_date (str): end of interval for collecting data
        """
        self.meteo_api = meteo_api
        self.start_date = start_date
        self.end_date = end_date
        self.h_data = meteo_api.get_historical_data(start_date, end_date)
        self.f_data = meteo_api.get_forecast()

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

    def calculate_hist_mean(self, metric):
        """Calculates mean value of specified metric.
        Args:
            metric (str): weather metric, refer to Meteo API
        """
        mean = self.get_hist_metric(metric).mean()
        print(f"Mean {metric}: {mean:.2f}")

    def calculate_hist_day_mean(self, metric):
        """Calculates mean value of specified metric during day.
        Args:
            metric (str): weather metric, refer to Meteo API
        """
        mean_day = self.get_hist_metric(metric)[
            (self.h_data.index.hour >= 8) & (self.h_data.index.hour <= 20)
        ].mean()
        print(f"Mean day {metric} - {mean_day:.2f}")

    def calculate_hist_night_mean(self, metric):
        """Calculates mean value of specified metric during night.
        Args:
            metric (str): weather metric, refer to Meteo API
        """
        mean_night = self.get_hist_metric(metric)[
            (self.h_data.index.hour < 8) | (self.h_data.index.hour > 20)
        ].mean()
        print(f"Mean night {metric} - {mean_night:.2f}")

    def calculate_rainy_weekends(self):
        """Calculates amount of weekends that had rain on both days for atleast an hour."""
        rain_types = ["rain", "heavy-rain", "freezing-rain"]
        self.h_data.loc[:, "rain"] = self.h_data["conditionCode"].isin(
            rain_types)
        weekend_data = self.h_data[self.h_data.index.weekday >= 5]
        data = weekend_data.resample("D")["rain"].max().dropna()
        saturdays = data.index[data.index.weekday == 5]
        rainy_weekend_count = 0
        for saturday in saturdays:
            if data.loc[saturday] == True:
                sunday = saturday + pd.Timedelta(days=1)
                if sunday in data.index and data.loc[sunday] == True:
                    rainy_weekend_count += 1
        print(f"Weekends count which had rain on both days for atleast hour: {
              rainy_weekend_count}")
