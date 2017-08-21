# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-21 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='type',
            field=models.CharField(choices=[('0', 'Owner'), ('1', 'Renter')], default='0', max_length=1, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='image',
            name='type',
            field=models.CharField(choices=[('0', 'Local'), ('1', 'Remote')], default='0', max_length=1, verbose_name='type'),
        ),
    ]
