# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-05 11:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='type',
            field=models.CharField(choices=[('1', 'Renter Ad'), ('0', 'Owner Ad')], default='0', max_length=1, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='flat',
            name='type',
            field=models.CharField(choices=[('2', 'Bed'), ('1', 'Room'), ('0', 'Flat')], default='0', max_length=1, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='image',
            name='type',
            field=models.CharField(choices=[('1', 'Remote image'), ('0', 'Local image')], default='0', max_length=1, verbose_name='type'),
        ),
    ]