# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0004_auto_20151124_2245'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feed',
            old_name='icon',
            new_name='favIcon',
        ),
    ]
