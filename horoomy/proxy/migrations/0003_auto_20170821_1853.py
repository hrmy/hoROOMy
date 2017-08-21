# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-21 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proxy', '0002_auto_20170821_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proxy',
            name='type',
            field=models.CharField(choices=[('0', 'HTTP'), ('1', 'HTTPS'), ('2', 'HTTP / HTTPS')], max_length=1, verbose_name='type'),
        ),
    ]
