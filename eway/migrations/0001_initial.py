# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0003_basket_vouchers'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(verbose_name='date created')),
                ('date_modified', models.DateTimeField(verbose_name='date modified')),
                ('url', models.TextField(default='', verbose_name='request URL')),
                ('method', models.CharField(max_length=255, verbose_name='request_method', blank=True)),
                ('request', models.TextField(verbose_name='request message', blank=True)),
                ('response', models.TextField(default='', verbose_name='response message', blank=True)),
                ('response_code', models.CharField(default='', max_length=2, verbose_name='response code', blank=True)),
                ('response_message', models.CharField(default='', max_length=255, verbose_name='response message', blank=True)),
                ('errors', models.TextField(default='', verbose_name='errors', blank=True)),
            ],
            options={
                'ordering': ('-date_created',),
                'verbose_name': 'request log',
                'verbose_name_plural': 'request logs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(verbose_name='date created')),
                ('date_modified', models.DateTimeField(verbose_name='date modified')),
                ('access_code', models.CharField(max_length=255, verbose_name='access code', blank=True)),
                ('token_customer_id', models.CharField(default='', max_length=16, verbose_name='token customer ID', blank=True)),
                ('transaction_id', models.CharField(default='', max_length=100, verbose_name='transaction ID', blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=12, verbose_name='amount', blank=True, decimal_places=2)),
                ('order_number', models.CharField(default='', max_length=255, verbose_name='order number', blank=True)),
                ('status', models.CharField(default='in progress', max_length=255, verbose_name='status', choices=[('in progress', 'in progress'), ('completed', 'completed'), ('suspicious', 'suspicious')])),
                ('basket', models.ForeignKey(to='basket.Basket', verbose_name='basket', on_delete=django.db.models.deletion.SET_NULL, related_name='eway_transactions', null=True)),
            ],
            options={
                'ordering': ('-date_created',),
                'verbose_name': 'transaction',
                'verbose_name_plural': 'transactions',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='requestlog',
            name='transaction',
            field=models.ForeignKey(to='eway.Transaction', verbose_name='transaction', related_name='request_logs'),
            preserve_default=True,
        ),
    ]
