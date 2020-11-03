from django.db import models

from opinioxx import settings


class Comment(models.Model):
    """ Stores a comment related to an idea. Comments with a specific category change the state of the idea. """
    CLOSE = 'C'
    ACCEPT = 'A'
    REOPEN = 'R'
    NORMAL = 'N'
    content = models.CharField(max_length=5000)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    idea = models.ForeignKey('Idea', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=1, blank=True, default=NORMAL, choices=[
        (CLOSE, 'closes'),
        (ACCEPT, 'accepts'),
        (REOPEN, 'reopens'),
        (NORMAL, 'normal')
    ])
