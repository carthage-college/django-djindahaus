# django-djindahaus
Capacity tracking app based on data from wifi access point APIs

#*/5 * * * * DJANGO_SETTINGS_MODULE=djindahaus.settings.shell ; export DJANGO_SETTINGS_MODULE; (cd /data2/python_venv/3.6/djindahaus/ && . bin/activate && bin/python djindahaus/bin/okupa.py 2>&1 | mail -s "[DJ IndaHaus] capacity tracking" larry@carthage.edu) >> /dev/null 2>&1
#*/5 * * * * DJANGO_SETTINGS_MODULE=djindahaus.settings.shell ; export DJANGO_SETTINGS_MODULE ; (cd /data2/python_venv/3.6/djindahaus/ && . bin/activate && bin/python djindahaus/bin/okupa.py) >> /dev/null 2>&1
