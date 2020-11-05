from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from opinioxx.base.models import User, Idea, GlobalSettings


class CustomUserAdmin(UserAdmin):
    """ Defines the user administration interface """
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (  # new fieldset added to the bottom
            'E-Mail-Benachrichtigungen',
            {
                'fields': (
                    'notifiable_projects',
                    'notify_interval',
                    'add_new_projects_to_notify_list',
                    'notify_new_idea',
                    'notify_state_changed',
                    'notify_comments',
                ),
            },
        ),
    )
    filter_horizontal = ['notifiable_projects']  # add selected projects
    list_display = ['username', 'email', 'is_active', 'last_login', 'get_projects']  # columns to show in the overview

    @staticmethod
    def get_projects(user):
        """ helper function to display the projects as text in one line """
        return ", ".join([p.name for p in user.notifiable_projects.all()])


# register needed classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(Idea)
admin.site.register(GlobalSettings)
