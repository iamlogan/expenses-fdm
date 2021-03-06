# Generated by Django 4.0.1 on 2022-04-17 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expensesapp', '0025_user_step_in_alter_feedback_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='step_in',
            new_name='substitute',
        ),
        migrations.AlterField(
            model_name='claim',
            name='status',
            field=models.CharField(choices=[('1', 'Draft'), ('2', 'Pending'), ('3', 'Sent'), ('4', 'Accepted'), ('5', 'Rejected')], max_length=1),
        ),
    ]
