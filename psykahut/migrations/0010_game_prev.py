# Generated by Django 2.0.7 on 2018-08-01 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('psykahut', '0009_auto_20180731_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='prev',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prev', to='psykahut.Question'),
        ),
    ]
