# -*- coding: utf-8 -*-

"""API views."""

import json

import requests
import urllib3
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from djindahaus.core.manager import Client
from djindahaus.core.models import Area
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@portal_auth_required(
    session_var='DJINDAHAUS_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def spa(request):
    """Display all clients for all domain controllers for SPA."""
    client = Client()
    domains = client.domains
    token = client.get_token()
    for idx, domain in enumerate(domains):
        headers = {
            'accept': 'application/json',
            'Authorization': client.get_token_nac(),
        }
        devices = client.get_devices(domain['id'], token)
        pids = []
        if devices:
            # auth token from NAC
            for device_wap in devices:
                ap = device_wap['ap']
                mac = device_wap['mac'].replace('-', ':')
                url = '{0}{1}/{2}'.format(
                    settings.PACKETFENCE_API_EARL,
                    settings.PACKETFENCE_NODE_ENDPOINT,
                    mac,
                )
                response = requests.get(
                    url=url, headers=headers, verify=False,
                )
                device_nac = response.json()

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
                            if domains[idx]['areas']:
                                for area in domains[idx]['areas']:
                                    if ap in area['aps']:
                                        if pid not in area['pids']:
                                            area['pids'].append(pid)
                            else:
                                domains[idx]['areas'] = None
            # update RF domain with the total number of pids
            domains[idx]['pids'] = len(pids)
            domains[idx]['capacity'] = round(
                domains[idx]['pids'] / domains[idx]['capacity'] * 100,
            )
            # update areas with total number of pids
            if domains[idx]['areas']:
                for aid, _ in enumerate(domains[idx]['areas']):
                    count = len(domains[idx]['areas'][aid]['pids'])
                    domains[idx]['areas'][aid]['pids'] = count
                    cap = domains[idx]['areas'][aid]['capacity']
                    domains[idx]['areas'][aid]['capacity'] = round(
                        count / cap * 100,
                    )

    # destroy the authentication token
    client.destroy_token(token)

    return HttpResponse(
        json.dumps(domains), content_type='text/plain; charset=utf-8',
    )


def clients(request, domain):
    """Display all clients given a domain controller identifier."""
    area = get_object_or_404(Area, rf_domain=domain)
    client = Client()
    token = client.get_token()
    okupa = client.get_okupa(area, token)
    capacity = client.get_capacity(area.rf_domain)
    # sign out
    client.destroy_token(token)
    percent = 0
    if okupa:
        percent = round(okupa / capacity * 100)
    jason = json.dumps({'capacity': capacity, 'okupa': okupa, 'percent': percent})
    return HttpResponse(jason, content_type='text/plain; charset=utf-8')
