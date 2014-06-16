# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Listing.available'
        db.add_column('listings_listing', 'available',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Listing.available'
        db.delete_column('listings_listing', 'available')


    models = {
        'listings.listing': {
            'Meta': {'ordering': "['-listingID']", 'object_name': 'Listing'},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '254', 'blank': 'True'}),
            'area': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'available': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'bedrooms': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'catsAllowed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'dateListingPosted': ('django.db.models.fields.DateTimeField', [], {}),
            'dateListingScraped': ('django.db.models.fields.DateTimeField', [], {}),
            'dateListingUpdated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateRecordUpdated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'dogsAllowed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'laundry': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '99', 'blank': 'True'}),
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
            'shared': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'sublet': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['listings']