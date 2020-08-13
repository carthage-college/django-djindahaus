# -*- coding: utf-8 -*-

import os
import sys


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djindahaus.settings.shell')

from django.conf import settings


# set up command-line options

def main():
    """Main function that does something."""
    try:
        print("hello world")
    except Exception as e:
        print("does not exist")
        print("Exception: {0}".format(str(e)))
        sys.exit(1)


if __name__ == '__main__':

    sys.exit(main())
