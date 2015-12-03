# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0003_auto_20151124_2244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedlink',
            name='feed',
            field=models.ForeignKey(related_name='links', to='feeds.Feed'),
        ),
        migrations.AlterField(
            model_name='feedlink',
            name='link',
            field=models.ForeignKey(to='feeds.Link'),
        ),
    ]
