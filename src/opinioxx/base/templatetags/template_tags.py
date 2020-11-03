# template tags used in the templates
import importlib

from django import template
from django.conf import settings
from django.contrib.auth import get_user
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe

from opinioxx.base.models import Project, Idea, Vote, User

register = template.Library()


@register.simple_tag(takes_context=True)
def signal(context, name, first=False, **kwargs):
    request = context['request']
    module, name = name.rsplit('.', 1)
    module = importlib.import_module(module)
    signal = getattr(module, name)
    elements = []
    for receiver, response in signal.send(request, **kwargs):
        if response and isinstance(response, dict) and response['priority'] and response['value']:
            elements.append(response)
    html = []
    for element in sorted(elements, key=lambda x: x['priority']):
        html.append(element['value'])
        if first:
            break
    return mark_safe(''.join(html))


@register.simple_tag(takes_context=True)
def voting_allowed(context, project_id, idea_id):
    """ Checks if a user (stored in context) is allowed to vote for a given idea in the given project. """
    try:
        request = context['request']
        project = Project.objects.get(id=project_id)
        user = get_user(request)
        if user.is_superuser:
            return False
        if user.is_anonymous:
            if project.public_voting:
                # check if anonymous user already voted and the idea is stored in his session
                if 'idea_ids' not in request.session:
                    return True
                return idea_id not in request.session['idea_ids']
        if idea_id is None:
            # idea does not exist until now (called from "add new feedback page")
            return True
        if not project.voting_allowed(user):
            return False
        # try to access rating object
        idea = Idea.objects.get(id=idea_id)
        idea.vote_set.get(user_id=user.id)
        return not project.anonymous_votes
    except (Project.DoesNotExist, Idea.DoesNotExist):
        return False
    except Vote.DoesNotExist:
        return True


@register.simple_tag(takes_context=True)
def has_rating_from_user(context, idea_id, user_id):
    """ Checks if an given idea already has an rating from a given user (either directly given or use session). """
    request = context['request']
    if not user_id:
        if 'idea_ids' not in request.session:
            return False
        return idea_id in request.session['idea_ids']
    try:
        # try to access rating object
        idea = Idea.objects.get(id=idea_id)
        idea.vote_set.get(user_id=user_id)
        return True
    except ObjectDoesNotExist:
        return False


@register.simple_tag
def get_free_starcount(user_id, project_id):
    """ Gets the amount of free favorites of a given user for a given project. """
    try:
        user = User.objects.get(id=user_id)
        return user.get_free_favorites(project_id)
    except ObjectDoesNotExist:
        return 0


@register.simple_tag
def has_star_from_user(idea_id, user_id):
    """ Checks if a given idea is a favorite of a given user. """
    try:
        idea = Idea.objects.get(id=idea_id)
        idea.favorite_set.get(user_id=user_id)
        return True
    except ObjectDoesNotExist:
        return False


@register.simple_tag
def is_admin_from(user_id, project_id):
    """ Checks if a given user has admin rights for a given project. """
    try:
        user = User.objects.get(id=user_id)
        is_project_admin = Project.objects.filter(id=project_id, admins__id=user_id).exists()
        return is_project_admin or user.is_superuser  # site-administrators have access to all projects
    except ObjectDoesNotExist:
        return False


@register.simple_tag
def allow_registration():
    """ Checks if the registration of new users is allowed (setting in the global config-file).
    If no user exist, the registration is enabled to be able to create the site-administrator. """
    return False if User.objects.count() > 0 and not settings.ALLOW_USER_REGISTRATION else True


@register.simple_tag
def has_new_comments(idea_id, user_id):
    """ Checks if an idea has new comments after the last login of a given user. """
    try:
        idea = Idea.objects.get(id=idea_id)
        user = User.objects.get(id=user_id)
        if user.penultimate_login is not None:
            return idea.comment_set.filter(date__gte=user.penultimate_login).exists()
        else:
            return idea.comment_set.all().exists()
    except ObjectDoesNotExist:
        return False
