# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0013_auto_20161024_0010'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookPost',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='askbot.Post')),
                ('facebook_id', models.CharField(max_length=64)),
                ('picture_url', models.URLField()),
                ('facebook_url', models.URLField()),
                ('facebook_author_id', models.PositiveIntegerField()),
                ('likes', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Facebook post',
                'verbose_name_plural': 'Facebook posts',
            },
            bases=('askbot.post',),
        ),
    ]
