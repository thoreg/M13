# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-15 20:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0004_salesrankhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesrankhistory',
            old_name='sales_rank',
            new_name='salesrank',
        ),
    ]
