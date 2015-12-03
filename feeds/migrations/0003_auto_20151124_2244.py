# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0002_auto_20151124_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedlink',
            name='link',
            field=models.ForeignKey(to='feeds.Link', related_name='links'),
        ),
    ]
