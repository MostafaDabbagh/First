# Generated by Django 4.0.2 on 2022-02-28 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='file',
        ),
        migrations.AddField(
            model_name='file',
            name='filename',
            field=models.TextField(default=None, max_length=200),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='created',
            field=models.DateTimeField(),
        ),
    ]
