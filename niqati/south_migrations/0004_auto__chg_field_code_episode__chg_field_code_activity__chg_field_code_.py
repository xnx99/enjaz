# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Code.episode'
        db.alter_column(u'niqati_code', 'episode_id', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['activities.Episode']))

        # Changing field 'Code.activity'
        db.alter_column(u'niqati_code', 'activity_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'], null=True))

        # Changing field 'Code_Order.episode'
        db.alter_column(u'niqati_code_order', 'episode_id', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['activities.Episode']))

        # Changing field 'Code_Order.activity'
        db.alter_column(u'niqati_code_order', 'activity_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'], null=True))

    def backwards(self, orm):

        # Changing field 'Code.episode'
        db.alter_column(u'niqati_code', 'episode_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Episode'], null=True))

        # User chose to not deal with backwards NULL issues for 'Code.activity'
        raise RuntimeError("Cannot reverse this migration. 'Code.activity' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Code.activity'
        db.alter_column(u'niqati_code', 'activity_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity']))

        # Changing field 'Code_Order.episode'
        db.alter_column(u'niqati_code_order', 'episode_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Episode'], null=True))

        # User chose to not deal with backwards NULL issues for 'Code_Order.activity'
        raise RuntimeError("Cannot reverse this migration. 'Code_Order.activity' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Code_Order.activity'
        db.alter_column(u'niqati_code_order', 'activity_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity']))

    models = {
        u'activities.activity': {
            'Meta': {'object_name': 'Activity'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Category']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'edit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inside_collaborators': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'is_editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'organizers': ('django.db.models.fields.IntegerField', [], {}),
            'outside_collaborators': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'participants': ('django.db.models.fields.IntegerField', [], {}),
            'primary_club': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'primary_activity'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['clubs.Club']"}),
            'public_description': ('django.db.models.fields.TextField', [], {}),
            'requirements': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'secondary_clubs': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_activity'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['clubs.Club']"}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'activities.category': {
            'Meta': {'object_name': 'Category'},
            'ar_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'en_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Category']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'activities.episode': {
            'Meta': {'object_name': 'Episode'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Activity']"}),
            'can_report_early': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'requires_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'requires_story': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'clubs.club': {
            'Meta': {'object_name': 'Club'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'college': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['clubs.College']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'coordination'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deputies': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'deputyships'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'edit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employee'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True', 'null': 'True'}),
            'english_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'memberships'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parenthood'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['clubs.Club']", 'blank': 'True', 'null': 'True'}),
            'special': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'clubs.college': {
            'Meta': {'object_name': 'College'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'section': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'niqati.category': {
            'Meta': {'object_name': 'Category'},
            'ar_label': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'requires_approval': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'niqati.code': {
            'Meta': {'object_name': 'Code'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Activity']", 'null': 'True', 'blank': 'True'}),
            'asset': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['niqati.Category']"}),
            'code_string': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['niqati.Code_Collection']"}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Episode']"}),
            'generation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redeem_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'niqati.code_collection': {
            'Meta': {'object_name': 'Code_Collection'},
            'approved': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'asset': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'code_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['niqati.Category']"}),
            'code_count': ('django.db.models.fields.IntegerField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'date_ordered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delivery_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['niqati.Code_Order']"})
        },
        u'niqati.code_order': {
            'Meta': {'object_name': 'Code_Order'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Activity']", 'null': 'True', 'blank': 'True'}),
            'date_ordered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Episode']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['niqati']