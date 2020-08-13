#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import requests
import urllib3
from django.conf import settings
from djindahaus.core.manager import Client
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    """Display the number of nodes."""
    client = Client()
    # obtain all devices connected to an RF Domain
    domains = settings.INDAHAUS_RF_DOMAINS
    devices = None
    token = client.get_token()
    for idx, domain in enumerate(domains):
        # auth token from NAC
        headers = {
            'accept': 'application/json', 'Authorization': client.get_token_nac(),
        }
        if settings.DEBUG:
            print(headers)
        devices = client.get_devices(domain['id'], token)
        # if we have some devices go to the NAC to find out who
        # they are based on MAC
        pids = []
        if devices:
            # iterate over the devices from the NAC to remove any duplicate
            # users who might have more than one device registered in an
            # RF Domain.
            for device_wap in devices:
                ap = device_wap['ap']
                mac = device_wap['mac'].replace('-', ':')
                if settings.DEBUG:
                    print('ap = {0}'.format(ap))
                    print('mac = {0}'.format(mac))
                url = '{0}{1}/{2}'.format(
                    settings.PACKETFENCE_API_EARL,
                    settings.PACKETFENCE_NODE_ENDPOINT,
                    mac,
                )
                response = requests.get(url=url, headers=headers, verify=False)
                device_nac = response.json()
                if response.status_code != 404:
                    for key, _ in device_nac['item'].items():
                        if settings.DEBUG:
                            print(key, device_nac['item'][key])
                        if key == 'pid':
                            pid = device_nac['item'][key].lower()
                            # some folks are registered with both their username
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
                                    if settings.DEBUG:
                                        print(
                                            'domain AP = {0}/{1}'.format(ap, pid),
                                        )
                                # check for areas within a domain
                                if domains[idx]['areas']:
                                    for area in domains[idx]['areas']:
                                        if ap in area['aps']:
                                            if settings.DEBUG:
                                                print('area AP = {0} / {1}'.format(
                                                    ap, pid,
                                                ))
                                            if pid not in area['pids']:
                                                area['pids'].append(pid)
                                else:
                                    domains[idx]['areas'] = None
            print(pids)
            # update RF domain with the total number of pids
            domains[idx]['pids'] = len(pids)
            count = domains[idx]['pids']
            cap = domains[idx]['capacity']
            print('++++++++++++++++++++++++++++')
            print(
                {
                    'id': domains[idx]['id'],
                    'name': domains[idx]['name'],
                    'pids': domains[idx]['pids'],
                    'count': domains[idx]['pids'],
                    'capacity': round(count / cap * 100),
                },
            )
            # update areas with total number of pids
            if domains[idx]['areas']:
                print('areas:')
                for aid, _ in enumerate(domains[idx]['areas']):
                    print(domains[idx]['areas'][aid]['name'])
                    print('pids = {0}'.format(domains[idx]['areas'][aid]['pids']))
                    length = len(domains[idx]['areas'][aid]['pids'])
                    domains[idx]['areas'][aid]['pids'] = length
                    print('count = {0}'.format(domains[idx]['areas'][aid]['pids']))
                    count = domains[idx]['areas'][aid]['pids']
                    cap = domains[idx]['areas'][aid]['capacity']
                    print('capacity = {0}'.format(round(count / cap * 100)))
            print('----------------------------')

    # destory client otherwise we max out the number of connections allowed
    # to the API
    client.destroy_token(token)


if __name__ == "__main__":

    sys.exit(main())
