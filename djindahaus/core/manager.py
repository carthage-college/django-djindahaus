# -*- coding: utf-8 -*-

import json

import requests
from django.conf import settings
from django.core.cache import cache


class Client(object):
    """REST API client for all communication needs."""

    def __init__(self):
        """Initialisation for variables used throughout."""
        self.base_url = settings.INDAHAUS_API_EARL
        self.domains = settings.INDAHAUS_RF_DOMAINS
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
        devices = cache.get(domain)
        if not devices:
            response = requests.post(
                self.clients_endpoint,
                cookies={'auth_token': token},
                data=json.dumps({'rf-domain': domain}),
                verify=False,
            )
            if response.status_code == 200:
                jason = response.json()
                devices = jason.get('data')
                cache.set(domain, devices, settings.INDAHAUS_CACHE_TIMEOUT)

        return devices

    def get_capacity(self, domain):
        capacity = 0
        for dom in self.domains:
            if dom['id'] == domain:
                capacity = dom['capacity']
                break
            elif dom['areas']:
                for area in dom['areas']:
                    if area['id'] == domain:
                        capacity = area['capacity']
                        break
        return capacity

    def get_okupa(self, area, token):
        okupa = None
        if area.parent:
            devices = self.get_devices(area.parent.rf_domain, token)
            area.pids = []
        else:
            devices = self.get_devices(area.rf_domain, token)

        headers = {
            'accept': 'application/json', 'Authorization': self.get_token_nac(),
        }
        pids = []
        if devices:
            for device_wap in devices:
                ap = device_wap['ap']
                mac = device_wap['mac'].replace('-', ':')
                url = '{0}{1}/{2}'.format(
                    settings.PACKETFENCE_API_EARL,
                    settings.PACKETFENCE_NODE_ENDPOINT,
                    mac,
                )
                response = requests.get(url=url, headers=headers, verify=False)
                device_nac = response.json()
                if response.status_code != 404 and response.status_code != 502:
                    for key, _ in device_nac['item'].items():
                        if key == 'pid':
                            pid = device_nac['item'][key].lower()
                            # some folks are registered with their username
                            # and their email address for some reason.
                            if '@{0}'.format(settings.LDAP_EMAIL_DOMAIN) in pid:
                                pid = pid.split('@')[0]
                            status = (
                                pid not in settings.INDAHAUS_XCLUDE and
                                'host/' not in pid and
                                'carthage\\' not in pid
                            )
                            if status:
                                if pid not in pids:
                                    pids.append(pid)
                                    # check for areas within a domain
                                if area.parent:
                                    if ap in area.access_points:
                                        if pid not in area.pids:
                                            area.pids.append(pid)
        if area.parent:
            okupa = len(area.pids)
        else:
            okupa = len(pids)

        return okupa
