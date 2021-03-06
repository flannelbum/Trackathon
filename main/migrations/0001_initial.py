# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-17 04:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pledge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=9)),
                ('firstname', models.CharField(default=None, max_length=35)),
                ('lastname', models.CharField(default=None, max_length=35)),
                ('is_first_time_donor', models.BooleanField(default=False)),
                ('is_thanked', models.BooleanField(default=False)),
                ('is_monthly', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('city', models.CharField(default=None, max_length=35)),
                ('phone_number', models.CharField(blank=True, max_length=13)),
                ('comment', models.TextField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('callsign', models.CharField(max_length=4)),
            ],
        ),
        migrations.AddField(
            model_name='pledge',
            name='station',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='main.Station'),
        ),
    ]
