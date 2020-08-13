# -*- coding: utf-8 -*-

import json

import requests
from django.conf import settings


class Client(object):
    """REST API client for all communication needs."""

    def __init__(self):
        """Initialisation for variables used throughout."""
        self.base_url = settings.INDAHAUS_API_EARL
        self.clients_endpoint = '{0}/{1}/{2}/{3}'.format(
            settings.INDAHAUS_API_EARL,
            settings.INDAHAUS_ENDPOINT_STATS,
            settings.INDAHAUS_ENDPOINT_STATS_WIRELESS,
            settings.INDAHAUS_ENDPOINT_STATS_WIRELESS_CLIENTS,
        )

    def get_token_nac(self):
        """Obtain the authentication token from packetfence API."""
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        auth_params = {
            'username': settings.PACKETFENCE_USERNAME,
            'password': settings.PACKETFENCE_PASSWORD,
        }
        url = settings.PACKETFENCE_API_EARL + settings.PACKETFENCE_LOGIN_ENDPOINT
        resp = requests.post(
            url=url, data=json.dumps(auth_params), headers=headers, verify=False,
        )
        return json.loads(resp.content.decode('utf-8'))['token']


    def get_token(self):
        """Obtain the authentication token from the API."""
        token = None
        response = requests.get(
            '{0}/{1}'.format(self.base_url, settings.INDAHAUS_ENDPOINT_LOGIN),
             auth=(settings.INDAHAUS_USERNAME, settings.INDAHAUS_PASSWORD),
             verify=False,
        )
        jason = response.json()
        if jason.get('data'):
            token = jason['data'].get('auth_token')
        return token

    def destroy_token(self, token):
        """Sign out from the API."""
        response = requests.get(
            '{0}/{1}'.format(self.base_url, settings.INDAHAUS_ENDPOINT_LOGOUT),
            cookies={'auth_token': token},
            verify=False,
        )
        return response.json()

    def get_devices(self, domain, token):
        """Obtain all devices registered on a domain controller."""
        response = requests.post(
            self.clients_endpoint,
            cookies={'auth_token': token},
            data=json.dumps({'rf-domain': domain}),
            verify=False,
        )
        jason = response.json()
        return jason.get('data')
