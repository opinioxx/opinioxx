from django.apps import AppConfig


class OpinioxxBaseConfig(AppConfig):
    name = 'opinioxx.base'
    verbose_name = 'Opinioxx Base'

    def ready(self):
        from . import signals
        from . import receivers


default_app_config = 'opinioxx.base.OpinioxxBaseConfig'
