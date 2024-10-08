# -*- coding: utf-8 -*-

"""All views."""

import datetime
import requests
import urllib3
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from djindahaus.core.manager import Client
from djindahaus.core.models import Area
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@login_required
def home(request):
    """Display all clients for all domain controllers."""
    client = Client()
    domains = settings.INDAHAUS_RF_DOMAINS
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

                if response.status_code != 404:
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
            domains[idx]['occupied'] = len(pids)
            domains[idx]['percent'] = round(
                domains[idx]['occupied'] / domains[idx]['capacity'] * 100,
            )
            # update areas with total number of pids
            if domains[idx]['areas']:
                for aid, _ in enumerate(domains[idx]['areas']):
                    count = len(domains[idx]['areas'][aid]['pids'])
                    domains[idx]['areas'][aid]['occupied'] = count
                    cap = domains[idx]['areas'][aid]['capacity']
                    domains[idx]['areas'][aid]['percent'] = round(
                        count / cap * 100,
                    )

    # destroy the authentication token
    client.destroy_token(token)
    context = {'domains': domains}
    domains = None

    return render(request, 'home.html', context)


@login_required
def spa(request):
    """Display all clients for all domain controllers in standard HTML."""
    return render(request, 'spa.html', {})


def dining(request):
    """Display dining areas."""
    client = Client()
    token = client.get_token()
    try:
        caf = Area.objects.get(rf_domain='Cafeteria')
    except Exception:
        caf = None
    if caf:
        caf.okupa = client.get_okupa(caf, token)
        if caf.okupa:
            caf.percent = round(caf.okupa / caf.capacity * 100)
        else:
            caf.percent = 0
    try:
        stu = Area.objects.get(rf_domain='Student_Center')
    except Exception:
        stu = None
    if stu:
        stu.okupa = client.get_okupa(stu, token)
        if stu.okupa:
            stu.percent = round(stu.okupa / stu.capacity * 100)
        else:
            stu.percent = 0
    try:
        byt = Area.objects.get(rf_domain='Donna_Bytes')
    except Exception:
        byt = None
    if byt:
        byt.okupa = client.get_okupa(byt, token)
        if byt.okupa:
            byt.percent = round(byt.okupa / byt.capacity * 100)
        else:
            byt.percent = 0
    # sign out
    client.destroy_token(token)
    return render(request, 'dining.html', {'caf': caf, 'stu': stu, 'byt': byt})


@csrf_exempt
@login_required
def clear_cache(request, ctype='blurb'):
    """Clear the cache for API content."""
    if request.is_ajax() and request.method == 'POST':
        cid = request.POST.get('cid')
        key = 'livewhale_{0}_{1}'.format(ctype, cid)
        cache.delete(key)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        earl = '{0}/live/{1}/{2}@JSON?cache={3}'.format(
            settings.LIVEWHALE_API_URL, ctype, cid, timestamp,
        )
        try:
            response = requests.get(earl, headers={'Cache-Control': 'no-cache'})
            text = json.loads(response.text)
            cache.set(key, text)
            body = mark_safe(text['body'])
        except Exception:
            body = ''
    else:
        body = "Requires AJAX POST"

    return HttpResponse(body, content_type='text/plain; charset=utf-8')


def metadata(request):
    # req = prepare_django_request(request)
    # auth = init_saml_auth(req)
    # saml_settings = auth.get_settings()
    saml_settings = OneLogin_Saml2_Settings(settings=None, custom_base_path=settings.SAML_FOLDER, sp_validation_only=True)
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    return HttpResponse(content=metadata, content_type='text/xml')

    #if len(errors) == 0:
    #    resp = HttpResponse(content=metadata, content_type='text/xml')
    #else:
    #    resp = HttpResponseServerError(content=', '.join(errors))
    #return resp
