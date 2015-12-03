# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0007_auto_20151127_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedlink',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]
