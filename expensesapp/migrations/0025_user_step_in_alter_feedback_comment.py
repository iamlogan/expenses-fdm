# Generated by Django 4.0.1 on 2022-04-17 13:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expensesapp', '0024_alter_feedback_action_desc_alter_feedback_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='step_in',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='other_managers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='comment',
            field=models.CharField(max_length=300),
        ),
    ]