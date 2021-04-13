from django.apps import AppConfig


class OpinioxxBaseConfig(AppConfig):
    name = 'opinioxx.base'
    verbose_name = 'Opinioxx Base'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from . import signals
        from . import receivers
