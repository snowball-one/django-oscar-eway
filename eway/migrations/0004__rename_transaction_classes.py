# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('eway_ewaytransaction', 'eway_transaction')
        db.rename_table('eway_ewayresponsecode', 'eway_responsecode')

        db.rename_table('eway_ewayresponsecode_transactions', 'eway_responsecode_transactions')
        db.rename_column('eway_responsecode_transactions', 'ewayresponsecode_id', 'responsecode_id')
        db.rename_column('eway_responsecode_transactions', 'ewaytransaction_id', 'transaction_id')

    def backwards(self, orm):
        db.rename_table('eway_transaction', 'eway_ewaytransaction')
        db.rename_table('eway_responsecode', 'eway_ewayresponsecode')

        db.rename_column('eway_responsecode_transactions', 'responsecode_id', 'ewayresponsecode_id')
        db.rename_column('eway_responsecode_transactions', 'transaction_id', 'ewaytransaction_id')
        db.rename_table('eway_responsecode_transactions', 'eway_ewayresponsecode_transactions')

    models = {
        'eway.responsecode': {
            'Meta': {'object_name': 'ResponseCode'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transactions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'response_messages'", 'symmetrical': 'False', 'to': "orm['eway.Transaction']"})
        },
        'eway.transaction': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'Transaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_index': 'True'}),
            'request_json': ('django.db.models.fields.TextField', [], {}),
            'request_url': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True'}),
            'response_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'response_json': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'response_message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'token_customer_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'db_index': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['eway']
