# Generated by Django 4.0.1 on 2022-01-13 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expensesapp', '0007_alter_claim_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='reference',
            field=models.CharField(default='0', max_length=8),
        ),
    ]