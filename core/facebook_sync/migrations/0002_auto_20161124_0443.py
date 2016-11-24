# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_sync', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookpost',
            name='facebook_author_id',
            field=models.CharField(max_length=100),
        ),
    ]
