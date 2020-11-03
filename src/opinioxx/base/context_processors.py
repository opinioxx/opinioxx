from django.conf import settings
from django.contrib.auth import get_user

from opinioxx.base.models import User


def common_variables(request):
    """ Helper method to add common variables to the context. Called in the settings.py file. """
    user = get_user(request)
    projects = User.get_projects(user)
    context = {
        'site_title': settings.TITLE,
        'version': settings.VERSION_NUMBER,
        'projects': projects,
    }
    return context
