# Generated by Django 4.0.1 on 2022-01-10 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expensesapp', '0002_alter_user_first_name_alter_user_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
    ]