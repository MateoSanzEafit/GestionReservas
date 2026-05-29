from datetime import datetime
import hashlib
import os

import requests
from django.utils.translation import gettext as _

from .interfaces.weather_provider import WeatherProvider


class WeatherAdapter(WeatherProvider):
    def __init__(self, api_url=None, api_key=None, session=None):
        self.api_url = api_url or os.getenv('WEATHER_API_URL', '')
        self.api_key = api_key or os.getenv('WEATHER_API_KEY', '')
        self.session = session or requests

    def _mock_forecast(self, location, target_date, error_message=None):
        seed = hashlib.sha256(f'{location}:{target_date}'.encode('utf-8')).hexdigest()
        temperature = 18 + (int(seed[:2], 16) % 10)
        rain_probability = int(seed[2:4], 16) % 100
        condition = _('Partly cloudy') if rain_probability < 45 else _('Light rain')
        return {
            'source': 'mock',
            'location': location,
            'date': str(target_date),
            'temperature_c': temperature,
            'rain_probability': rain_probability,
            'condition': condition,
            'recommendation': _('Conditions look favorable for booking') if rain_probability < 55 else _('Check the rain forecast before playing'),
            'error_message': error_message,
        }

    def get_forecast(self, location: str, target_date):
        if not self.api_url or not self.api_key:
            return self._mock_forecast(location, target_date)

        try:
            response = self.session.get(
                self.api_url,
                params={
                    'q': location,
                    'date': str(target_date),
                    'appid': self.api_key,
                },
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
            return {
                'source': 'external-api',
                'location': location,
                'date': str(target_date),
                'temperature_c': payload.get('temperature_c') or payload.get('temp') or payload.get('main', {}).get('temp'),
                'rain_probability': payload.get('rain_probability') or payload.get('rain', {}).get('probability', 0),
                'condition': payload.get('condition') or payload.get('weather', [{}])[0].get('description', _('Unknown')),
                'recommendation': payload.get('recommendation') or _('External weather data received successfully'),
            }
        except Exception as exc:
            return self._mock_forecast(location, target_date, error_message=str(exc))