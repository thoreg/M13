# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-05 07:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0002_auto_20160904_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='sale.Category'),
        ),
        migrations.AlterField(
            model_name='product',
            name='subcategory',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='sale.SubCategory'),
        ),
    ]
