#!/bin/bash
python manage.py runserver_plus --print-sql --settings=m13.settings_development 0.0.0.0:55555
