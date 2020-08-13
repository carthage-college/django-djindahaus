#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import requests
from django.conf import settings


def main():
    """Display the number of nodes."""
    url = '{0}/{1}'.format(
        settings.INDAHAUS_API_EARL, settings.INDAHAUS_ENDPOINT_LOGIN,
    )
    resp = requests.get(
        url,
        auth=(settings.INDAHAUS_USERNAME, settings.INDAHAUS_PASSWORD),
        verify=False,
    )
    jason = resp.json()
    return jason['data']['auth_token']


if __name__ == "__main__":

    sys.exit(main())
