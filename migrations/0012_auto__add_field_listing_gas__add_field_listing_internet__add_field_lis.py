# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Listing.gas'
        db.add_column('listings_listing', 'gas',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Listing.internet'
        db.add_column('listings_listing', 'internet',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Listing.cable'
        db.add_column('listings_listing', 'cable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Listing.lawn_care'
        db.add_column('listings_listing', 'lawn_care',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Listing.snow_removal'
        db.add_column('listings_listing', 'snow_removal',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Listing.trash'
        db.add_column('listings_listing', 'trash',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Listing.allUtilities'
        db.add_column('listings_listing', 'allUtilities',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Listing.utilitiesNotListed'
        db.add_column('listings_listing', 'utilitiesNotListed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Listing.gas'
        db.delete_column('listings_listing', 'gas')

        # Deleting field 'Listing.internet'
        db.delete_column('listings_listing', 'internet')

        # Deleting field 'Listing.cable'
        db.delete_column('listings_listing', 'cable')

        # Deleting field 'Listing.lawn_care'
        db.delete_column('listings_listing', 'lawn_care')

        # Deleting field 'Listing.snow_removal'
        db.delete_column('listings_listing', 'snow_removal')

        # Deleting field 'Listing.trash'
        db.delete_column('listings_listing', 'trash')

        # Deleting field 'Listing.allUtilities'
        db.delete_column('listings_listing', 'allUtilities')

        # Deleting field 'Listing.utilitiesNotListed'
        db.delete_column('listings_listing', 'utilitiesNotListed')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'listings.listing': {
            'Meta': {'ordering': "['-listingID']", 'object_name': 'Listing'},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '254', 'blank': 'True'}),
            'allUtilities': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'area': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'available': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'bedrooms': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'cable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'catsAllowed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'dateListingPosted': ('django.db.models.fields.DateTimeField', [], {}),
            'dateListingScraped': ('django.db.models.fields.DateTimeField', [], {}),
            'dateListingUpdated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateRecordUpdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dogsAllowed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'electricity': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gas': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'heat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'internet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'laundry': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '99', 'blank': 'True'}),
            'lawn_care': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'listingBody': ('django.db.models.fields.TextField', [], {}),
            'listingID': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'listingType': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'mapUrl': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'neighborhood': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'noSmoking': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'parking': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '99', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'shared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snow_removal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sublet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trash': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updatedBy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'utilitiesNotListed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'water': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['listings']