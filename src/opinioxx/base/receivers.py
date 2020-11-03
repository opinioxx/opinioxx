from django.dispatch import receiver
from django.templatetags.static import static
from django.urls import reverse

from opinioxx.base.models import Project
from opinioxx.base.signals import display_project_icons, display_user_icon


@receiver(display_project_icons)
def receiver_show_admins(sender, **kwargs):
    if 'project' not in kwargs:
        return None
    project = kwargs['project']
    if project.admins.count() == 0:
        return None
    imgurl = static('base/icon_projectadmin_light.png')
    admins = ''
    for admin in project.admins.all():
        admins += f'<br>{admin.username}'
    value = f'<img src="{imgurl}" class="p-2" style="height: 40px;" data-toggle="tooltip" data-placement="bottom" ' \
            f'data-html="true" title="Projekt-Administratoren: {admins}">'
    return {'priority': 20, 'value': value}


@receiver(display_project_icons)
def receiver_show_settings(sender, **kwargs):
    if 'project' not in kwargs:
        return None
    project = kwargs['project']
    if Project.objects.filter(id=project.id, admins__id=sender.user.id).exists() or sender.user.is_superuser:
        settingsurl = reverse('base:editproject', args=[project.id])
        imgurl = static('base/icon_settings.png')
        value = f'<a href="{settingsurl}"><img src="{imgurl}" class="p-2" style="height: 40px;" ' \
                f'data-toggle="tooltip" data-placement="right" title="Du bist als Administrator für dieses Projekt' \
                f' eingetragen und kannst die Einstellungen des Projekts über diesen Link bearbeiten."></a>'
        return {'priority': 30, 'value': value}
    else:
        return None


@receiver(display_user_icon)
def display_admin_icon(sender, **kwargs):
    value = ''
    imgurl = static('base/icon_projectadmin.png')
    try:
        if 'project' in kwargs and 'author' in kwargs:
            project = kwargs['project']
            author = kwargs['author']
            if Project.objects.filter(id=project.id, admins=author):
                value = f'<img src="{imgurl}" class="p-0" style="height: 20px;" data-toggle="tooltip" ' \
                        f'data-placement="top" title="Projekt-Administrator">'
        return {'priority': 20, 'value': value}
    except Project.DoesNotExist:
        return {'priority': 20, 'value': value}


@receiver(display_user_icon)
def display_global_admin_icon(sender, **kwargs):
    value = ''
    imgurl = static('base/icon_siteadmin.png')
    try:
        if 'author' in kwargs:
            author = kwargs['author']
            if author.is_superuser:
                value = f'<img src="{imgurl}" class="p-0" style="height: 20px;" data-toggle="tooltip" ' \
                        f'data-placement="top" title="globaler Administrator">'
        return {'priority': 10, 'value': value}
    except Project.DoesNotExist:
        return {'priority': 10, 'value': value}
