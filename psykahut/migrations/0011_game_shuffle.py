# Generated by Django 2.2.28 on 2022-09-08 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psykahut', '0010_game_prev'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='shuffle',
            field=models.BooleanField(default=True),
        ),
    ]
