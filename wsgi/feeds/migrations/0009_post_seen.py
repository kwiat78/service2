# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0008_feedlink_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='seen',
            field=models.BooleanField(default=True),
        ),
    ]
