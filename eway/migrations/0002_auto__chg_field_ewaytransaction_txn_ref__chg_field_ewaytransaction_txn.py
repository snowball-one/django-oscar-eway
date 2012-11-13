# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'EwayTransaction.txn_ref'
        db.alter_column('eway_ewaytransaction', 'txn_ref', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'EwayTransaction.txn_method'
        db.alter_column('eway_ewaytransaction', 'txn_method', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

    def backwards(self, orm):

        # Changing field 'EwayTransaction.txn_ref'
        db.alter_column('eway_ewaytransaction', 'txn_ref', self.gf('django.db.models.fields.CharField')(max_length=16, null=True))

        # Changing field 'EwayTransaction.txn_method'
        db.alter_column('eway_ewaytransaction', 'txn_method', self.gf('django.db.models.fields.CharField')(max_length=12, null=True))

    models = {
        'eway.ewayresponsecode': {
            'Meta': {'object_name': 'EwayResponseCode'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transactions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'response_messages'", 'symmetrical': 'False', 'to': "orm['eway.EwayTransaction']"})
        },
        'eway.ewaytransaction': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'EwayTransaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_index': 'True'}),
            'request_json': ('django.db.models.fields.TextField', [], {}),
            'response_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'response_json': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'response_message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'token_customer_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'db_index': 'True'}),
            'txn_method': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'txn_ref': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'txn_url': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True'})
        }
    }

    complete_apps = ['eway']