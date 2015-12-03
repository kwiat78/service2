# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('reg_exp', models.CharField(blank=True, null=True, max_length=511)),
            ],
        ),
        migrations.RemoveField(
            model_name='feed',
            name='reg_exp',
        ),
        migrations.RemoveField(
            model_name='link',
            name='feed',
        ),
        migrations.AddField(
            model_name='feedlink',
            name='feed',
            field=models.ForeignKey(to='feeds.Feed'),
        ),
        migrations.AddField(
            model_name='feedlink',
            name='link',
            field=models.ForeignKey(to='feeds.Link'),
        ),
    ]
