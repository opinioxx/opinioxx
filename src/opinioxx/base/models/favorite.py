from django.conf import settings
from django.db import models


class Favorite(models.Model):
    """ Stores a favourite point for an Idea """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idea = models.ForeignKey('Idea', on_delete=models.CASCADE)
