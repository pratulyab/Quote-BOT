# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-27 19:24
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0002_author_is_popular'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='author',
            managers=[
                ('random', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='quote',
            managers=[
                ('random', django.db.models.manager.Manager()),
            ],
        ),
    ]
