# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0005_auto_20151126_2136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feed',
            old_name='max_posts',
            new_name='limit',
        ),
    ]
