# Generated by Django 4.0.1 on 2022-04-17 10:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('expensesapp', '0020_claim_approval_author_claim_approval_datetime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='status_update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 17, 10, 42, 18, 438402, tzinfo=utc)),
            preserve_default=False,
        ),
    ]