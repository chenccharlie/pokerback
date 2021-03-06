from django.db import models


"""
All the users (entities that could start a game)
"""


class User(models.Model):
    is_authenticated: bool = True

    uuid = models.UUIDField(unique=True, db_index=True)
