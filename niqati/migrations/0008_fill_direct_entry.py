# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def fill_direct_entry(apps, schema_editor):
    Category = apps.get_model('niqati', 'Category')
    Category.objects.filter(label__in=['Idea', 'Organizer']).update(direct_entry=True)

def empty_direct_entry(apps, schema_editor):
    Category = apps.get_model('niqati', 'Category')
    Category.objects.filter(label__in=['Idea', 'Organizer']).update(direct_entry=False)    

class Migration(migrations.Migration):

    dependencies = [
        ('niqati', '0007_category_direct_entry'),
    ]

    operations = [
       migrations.RunPython(
           fill_direct_entry,
           reverse_code=empty_direct_entry)
    ]
