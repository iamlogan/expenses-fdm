# Generated by Django 4.0.1 on 2022-04-14 17:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expensesapp', '0013_user_manager'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='manager',
            new_name='primary_manager',
        ),
    ]