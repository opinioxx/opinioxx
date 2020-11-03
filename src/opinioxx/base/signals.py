import django.dispatch


display_project_icons = django.dispatch.Signal()
display_user_icon = django.dispatch.Signal()
display_idea_icons = django.dispatch.Signal()
form_project_init = django.dispatch.Signal()
form_project_save = django.dispatch.Signal()
add_notifications = django.dispatch.Signal()
get_projects_for_user = django.dispatch.Signal()
access_allowed_project = django.dispatch.Signal()
access_allowed_ideas = django.dispatch.Signal()
project_get_special_users = django.dispatch.Signal()
