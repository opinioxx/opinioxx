from django.conf import settings
from django.db import models


class Vote(models.Model):
    """ Stores a vote for an Idea """
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1
    value = models.IntegerField(choices=[
        (POSITIVE, 'positive'),
        (NEUTRAL, 'neutral'),
        (NEGATIVE, 'negative'),
    ])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    idea = models.ForeignKey('Idea', on_delete=models.CASCADE)
