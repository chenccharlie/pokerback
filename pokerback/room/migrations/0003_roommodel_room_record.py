# Generated by Django 3.0.7 on 2020-08-16 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("room", "0002_auto_20200815_1911"),
    ]

    operations = [
        migrations.AddField(
            model_name="roommodel",
            name="room_record",
            field=models.TextField(blank=True, null=True),
        ),
    ]
