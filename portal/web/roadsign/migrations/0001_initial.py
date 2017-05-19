# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 13:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields
import roadsign.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('particle_id', models.CharField(max_length=255)),
                ('status', enumfields.fields.EnumField(enum=roadsign.models.SignStatusType, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SignPanel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImagePanel',
            fields=[
                ('signpanel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='roadsign.SignPanel')),
                ('image', models.ImageField(upload_to='')),
            ],
            options={
                'abstract': False,
            },
            bases=('roadsign.signpanel',),
        ),
        migrations.CreateModel(
            name='TextPanel',
            fields=[
                ('signpanel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='roadsign.SignPanel')),
                ('line1', models.CharField(max_length=255)),
                ('line2', models.CharField(max_length=255)),
                ('line3', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('roadsign.signpanel',),
        ),
        migrations.AddField(
            model_name='signpanel',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_roadsign.signpanel_set+', to='contenttypes.ContentType'),
        ),
    ]
