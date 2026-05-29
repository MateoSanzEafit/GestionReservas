import os

import requests
from django.utils.translation import gettext as _


class AlliedTeamService:
    def __init__(self, api_url=None, session=None):
        self.api_url = api_url or os.getenv('ALLIED_TEAM_API_URL', '').strip()
        self.session = session or requests

    def fetch_summary(self):
        if not self.api_url:
            return {
                'available': False,
                'message': _('Configure ALLIED_TEAM_API_URL in your .env file to see allied team information.'),
            }

        try:
            response = self.session.get(self.api_url, timeout=8)
            response.raise_for_status()
            return {
                'available': True,
                'message': _('Information received from the allied API.'),
                'payload': response.json(),
            }
        except Exception as exc:
            return {
                'available': False,
                'message': _('The allied team API is not responding right now.'),
                'error': str(exc),
            }