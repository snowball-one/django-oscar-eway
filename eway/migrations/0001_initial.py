# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EwayTransaction'
        db.create_table('eway_ewaytransaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order_number', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_index=True)),
            ('token_customer_id', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, db_index=True)),
            ('txn_url', self.gf('django.db.models.fields.CharField')(max_length=800, null=True)),
            ('txn_method', self.gf('django.db.models.fields.CharField')(max_length=12, null=True)),
            ('txn_ref', self.gf('django.db.models.fields.CharField')(max_length=16, null=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('response_code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('response_message', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('request_json', self.gf('django.db.models.fields.TextField')()),
            ('response_json', self.gf('django.db.models.fields.TextField')(null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('eway', ['EwayTransaction'])

        # Adding model 'EwayResponseCode'
        db.create_table('eway_ewayresponsecode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('eway', ['EwayResponseCode'])

        # Adding M2M table for field transactions on 'EwayResponseCode'
        db.create_table('eway_ewayresponsecode_transactions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ewayresponsecode', models.ForeignKey(orm['eway.ewayresponsecode'], null=False)),
            ('ewaytransaction', models.ForeignKey(orm['eway.ewaytransaction'], null=False))
        ))
        db.create_unique('eway_ewayresponsecode_transactions', ['ewayresponsecode_id', 'ewaytransaction_id'])


    def backwards(self, orm):
        # Deleting model 'EwayTransaction'
        db.delete_table('eway_ewaytransaction')

        # Deleting model 'EwayResponseCode'
        db.delete_table('eway_ewayresponsecode')

        # Removing M2M table for field transactions on 'EwayResponseCode'
        db.delete_table('eway_ewayresponsecode_transactions')


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
            'txn_method': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True'}),
            'txn_ref': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True'}),
            'txn_url': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True'})
        }
    }

    complete_apps = ['eway']