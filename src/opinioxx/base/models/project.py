from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from opinioxx.base.signals import add_notifications, access_allowed_project, project_get_special_users


class Project(models.Model):
    """ A project is the frame for a set of Ideas with all necessary meta information. """
    OPEN = 'O'
    ARCHIVED = 'A'
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admins')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='users', blank=True)
    public_visible = models.BooleanField(default=False)
    public_voting = models.BooleanField(default=False)
    public_comments = models.BooleanField(default=False)
    anonymous_votes = models.BooleanField(default=False)
    automatic_closing_limit = models.IntegerField(default=-3)
    new_idea_description = models.CharField(max_length=500, blank=True)
    max_favorites = models.IntegerField(default=1)
    favorite_value = models.FloatField(default=1)
    state = models.CharField(max_length=1, default=OPEN, choices=[
        (OPEN, 'open'),
        (ARCHIVED, 'archived'),
    ])

    def __str__(self):
        return self.name

    def add_notifications(self):
        """ Adds notifications for this (newly created) project to all users who has default notifications enabled """
        for userobj in get_user_model().objects.filter(add_new_projects_to_notify_list=True).all():
            user = get_user_model().objects.get(id=userobj.id)
            if user in self.admins.all() or user in self.users.all() or user.is_superuser:
                user.notifiable_projects.add(self)
                user.save()
        add_notifications.send(self)

    def access_allowed(self, user):
        """ Checks if a user is allowed to access the project """
        return_value = False
        if self.public_visible or \
                Project.objects.filter(id=self.id, admins=user) or \
                Project.objects.filter(id=self.id, users=user) or \
                user.is_superuser:
            return_value = True
        for receiver, response in access_allowed_project.send(self, user=user):
            if response and isinstance(response, bool):
                return_value = return_value or response
        return return_value

    def voting_allowed(self, user):
        """ Checks if a user is allowed to vote """
        if user.is_anonymous and self.public_voting:
            return True
        elif user.is_superuser:
            return False
        elif not user.is_anonymous and (Project.objects.filter(id=self.id, users=user).exists() or
                                        Project.objects.filter(id=self.id, admins=user).exists()):
            return True
        return False

    def get_special_users(self):
        """ returns a list of all users with special rights in this project """
        users = self.admins.all()
        for receiver, response in project_get_special_users.send(self):
            if response:
                users = users | response
        return users

    def archived(self):
        return self.state == Project.ARCHIVED
