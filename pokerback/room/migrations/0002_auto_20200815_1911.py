# Generated by Django 3.0.7 on 2020-08-15 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("room", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="roommodel",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="roommodel",
            name="game_type",
            field=models.CharField(choices=[("poker", "POKER")], max_length=64),
        ),
        migrations.AlterField(
            model_name="roommodel",
            name="room_status",
            field=models.CharField(
                choices=[("active", "ACTIVE"), ("closed", "CLOSED")], max_length=32
            ),
        ),
        migrations.AddConstraint(
            model_name="roommodel",
            constraint=models.UniqueConstraint(
                condition=models.Q(room_status="active"),
                fields=("room_key",),
                name="unique_active_key",
            ),
        ),
        migrations.AddConstraint(
            model_name="roommodel",
            constraint=models.UniqueConstraint(
                condition=models.Q(room_status="active"),
                fields=("host_user",),
                name="unique_active_per_user",
            ),
        ),
    ]
