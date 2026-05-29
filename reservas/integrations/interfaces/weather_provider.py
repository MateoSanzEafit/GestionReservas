from abc import ABC, abstractmethod


class WeatherProvider(ABC):
    @abstractmethod
    def get_forecast(self, location: str, target_date):
        raise NotImplementedError