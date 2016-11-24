#!/bin/bash
#python manage.py runserver_plus 0.0.0.0:55555
python manage.py runserver_plus --print-sql --settings=m13.settings.development 0.0.0.0:55555
