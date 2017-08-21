# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-21 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proxy', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proxy',
            options={'ordering': ('-rating',), 'verbose_name': 'Proxy', 'verbose_name_plural': 'Proxies'},
        ),
        migrations.AlterField(
            model_name='proxy',
            name='address',
            field=models.CharField(max_length=30, verbose_name='address'),
        ),
    ]
