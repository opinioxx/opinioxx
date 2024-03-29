import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from opinioxx.base.models import Favorite, GlobalSettings, Idea, Comment, Project
from opinioxx.base.signals import get_projects_for_user


class User(AbstractUser):
    """ Holds all information about a user of the application. """
    INTERVALS = (
        (1, 'daily'),
        (7, 'weekly'),
        (30, 'monthly'),
    )
    notifiable_projects = models.ManyToManyField('Project', blank=True)
    notify_interval = models.IntegerField(choices=INTERVALS, default=7)
    add_new_projects_to_notify_list = models.BooleanField(default=True)
    notify_new_idea = models.BooleanField(default=True)
    notify_state_changed = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=True)
    penultimate_login = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """ saves a user but stores his last login in a separate field """
        try:
            user = User.objects.get(id=self.id)
            if user.last_login != self.last_login:
                self.penultimate_login = user.last_login
        except User.DoesNotExist:
            pass
        super(User, self).save()

    def get_free_favorites(self, project_id):
        """ returns the amount of free favourite stars a user can currently give for a project """
        project = Project.objects.get(id=project_id)
        allowed_favorites = project.max_favorites
        used_stars = Favorite.objects.filter(user_id=self.id,
                                             idea__project_id=project.id,
                                             idea__state=Idea.OPEN
                                             ).count()
        if used_stars >= allowed_favorites:
            return 0
        else:
            return allowed_favorites - used_stars

    @staticmethod
    def get_projects(user, state=Project.OPEN):
        """ returns all projects that a given user is allowed to access """
        if user.is_anonymous:
            projects = Project.objects.filter(public_visible=True, state=state).order_by(Lower('name'))
        elif user.is_superuser:
            projects = Project.objects.all().filter(state=state).order_by(Lower('name'))
        else:
            projects = Project.objects.filter(admins__id=user.id, state=state) | Project.objects.filter(
                users__id=user.id, state=state) | Project.objects.filter(public_visible=True, state=state)
        for receiver, response in get_projects_for_user.send(user):
            if response:
                projects = projects | response
        return projects.distinct().order_by(Lower('name'))

    def send_notification(self):
        """ Send a notification to the user if notifications are requested in the settings from the user. """
        if not self.is_active:
            return  # inactive users do not receive notifications
        changes = False
        globalsettings = GlobalSettings.objects.get_or_create(id=1)[0]
        message = [f'Hallo {self.username},', '',
                   f'es gab folgende Änderungen im {settings.TITLE}, die du unter {settings.BASE_URL} einsehen kannst.']
        for project in self.notifiable_projects.all():
            if project not in User.get_projects(self):
                # user is not allowed to see the project, remove from notify-list
                self.notifiable_projects.remove(project)
                self.save()
                pass
            # get all ideas not voted yet by this user
            ideas_db = project.idea_set.filter(
                Q(state=Idea.OPEN),
                Q(date__gte=globalsettings.last_cron_run),
                ~Q(date=datetime.date.today()),
                ~Q(vote__user=self)
            ).order_by('date', 'id')
            # remove all ideas that the user is not allowed to see
            ideas = []
            for idea in ideas_db:
                if project.voting_allowed(self) or idea.project.access_allowed(self) or self.is_superuser:
                    ideas.append(idea)
            # get all new comments that changed the state of an idea
            category_comments_db = Comment.objects.select_related('idea').filter(
                Q(idea__project_id=project.id),
                Q(idea__state__in=[Idea.SUCCESS, Idea.REJECTED]),
                Q(date__gte=globalsettings.last_cron_run),
                ~Q(date=datetime.date.today()),
                Q(category__in=[Comment.REOPEN, Comment.ACCEPT, Comment.CLOSE])
            ).order_by('date', 'id')
            # remove all comments that the user is not allowed to see
            category_comments = []
            for comment in category_comments_db:
                if project.voting_allowed(self) or comment.idea.project.access_allowed(self) or self.is_superuser:
                    category_comments.append(comment)
            # get all new comments not written by the user (if not commented anonymously)
            comments_db = project.idea_set.filter(
                Q(comment__date__gte=globalsettings.last_cron_run),
                ~Q(date=datetime.date.today()),
                ~Q(comment__author__id=self.id)
            ).distinct().order_by('date', 'id')
            # remove all comments that the user is not allowed to see
            comments = []
            for idea in comments_db:
                if project.voting_allowed(self) or idea.project.access_allowed(self) or self.is_superuser:
                    comments.append(idea)
            # add items to the mail
            if (ideas and self.notify_new_idea) or (category_comments and self.notify_state_changed) or (
                    comments and self.notify_comments):
                message.append('')
                message.append(f'{project.name}:')
                if self.notify_new_idea:
                    for idea in ideas:
                        message.append(f'* Neues Feedback: {idea.title}')
                        changes = True
                if self.notify_state_changed:
                    for comment in category_comments:
                        action = ''
                        if comment.category == Comment.CLOSE:
                            action = 'Feedback abgelehnt:'
                        elif comment.category == Comment.ACCEPT:
                            action = 'Feedback umgesetzt:'
                        elif comment.category == Comment.REOPEN:
                            action = 'Feedback wiedereröffnet:'
                        message.append(f'* {action} {comment.idea.title}')
                        changes = True
                if self.notify_comments:
                    for idea in comments:
                        message.append(f'* neue Kommentare: {idea.title}')
                        changes = True
        message.extend(['', 'Viele Grüße', f'Dein {settings.TITLE}-Team', '', '',
                        f'PS: Solltest Du diese E-Mail nicht mehr erhalten wollen, kannst Du sie unter {settings.BASE_URL}/profile?tab=email abbestellen.'])
        message = '\n'.join(message)
        if changes:
            send_mail(f'[{settings.TITLE}] Benachrichtigung über Änderungen', message, settings.DEFAULT_FROM_EMAIL,
                      [self.email])
