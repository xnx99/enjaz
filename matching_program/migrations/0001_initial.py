# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(max_length=255, null=True, verbose_name=b'field')),
                ('supervisor', models.CharField(max_length=100, verbose_name=b"Suggested supervisor's name", blank=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('required_role', models.CharField(max_length=100)),
                ('status', models.CharField(default=b'A', max_length=10, choices=[(b'A', b'applied'), (b'N', b'new'), (b'IP', b'in progress'), (b'P', b'puplished')])),
                ('communication', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(related_name='creator', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='members', verbose_name=b'members', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StudentApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('skills', models.CharField(max_length=255)),
                ('experience', models.TextField()),
                ('advantages', models.TextField(verbose_name=b'Why we should pick you?')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('research', models.ForeignKey(to='matching_program.ResearchProject')),
                ('user', models.ForeignKey(related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
