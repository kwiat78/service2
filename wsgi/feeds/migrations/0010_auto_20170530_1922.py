# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0009_post_seen'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feedlink',
            options={'ordering': ('position',)},
        ),
        migrations.AddField(
            model_name='post',
            name='mentioned',
            field=models.BooleanField(default=False),
        ),
    ]
