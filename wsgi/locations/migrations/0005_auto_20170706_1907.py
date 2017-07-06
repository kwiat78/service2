# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_auto_20160904_2133'),
    ]

    operations = [
        migrations.RenameField(
            model_name='track',
            old_name='procesed',
            new_name='processed',
        ),
        migrations.AddField(
            model_name='track',
            name='ended',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='location',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
