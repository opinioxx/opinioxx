from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class GlobalSettings(models.Model):
    """ stores application wide settings """
    last_cron_run = models.DateField(default=timezone.now)  # defines the last successful run of the cron job

    def save(self, *args, **kwargs):
        """ custom save function to ensure, that only one object of this type can exist """
        if not self.id and GlobalSettings.objects.exists():
            raise ValidationError('Only one global settings object allowed!')
        return super().save(*args, **kwargs)
