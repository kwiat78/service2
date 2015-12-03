# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('max_posts', models.IntegerField(default=20)),
                ('icon', models.CharField(max_length=511)),
                ('position', models.IntegerField()),
                ('reg_exp', models.CharField(max_length=511, null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=511)),
                ('feed', models.ForeignKey(to='feeds.Feed')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=511)),
                ('post_date', models.DateTimeField()),
                ('add_date', models.DateTimeField()),
                ('view', models.BooleanField()),
                ('feed', models.ForeignKey(to='feeds.Feed')),
            ],
        ),
    ]
