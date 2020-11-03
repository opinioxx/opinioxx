from django.db import models
from django.db.models import Sum


class Idea(models.Model):
    """ A single idea or suggestion what could be made better in a project. """
    OPEN = 'O'
    SUCCESS = 'Y'
    REJECTED = 'N'
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    state = models.CharField(max_length=1, default=OPEN, choices=[
        (OPEN, 'open'),
        (SUCCESS, 'success'),
        (REJECTED, 'rejected')
    ])
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_vote_value(self):
        """ returns the current value of votes and favorites for this idea """
        favorites_value = round(self.favorite_set.all().count() * self.project.favorite_value)
        votes_value = self.vote_set.aggregate(Sum('value'))['value__sum']
        if not votes_value:
            votes_value = 0
        return votes_value + favorites_value

    def get_css(self):
        """ returns the css classes set to the feedback depending on the current rating """
        if self.get_vote_value() > 0:
            return 'bg-success positive'
        elif self.get_vote_value() < 0:
            return 'bg-danger negative'
        else:
            return 'bg-dark text-light'

    def get_vote_count(self):
        return self.vote_set.count()

    def get_star_count(self):
        return self.favorite_set.count()

    def get_comment_count(self):
        return self.comment_set.count()

    def is_active(self):
        return self.state == Idea.OPEN
