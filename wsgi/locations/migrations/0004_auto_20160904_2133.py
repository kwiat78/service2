# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20160903_2044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='label',
        ),
        migrations.RemoveField(
            model_name='location',
            name='user',
        ),
    ]
