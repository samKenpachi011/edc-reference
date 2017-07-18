from django.db import models

from .reference import ReferenceDeleter, ReferenceUpdater


class ReferenceModelMixin(models.Model):

    edc_reference_model_deleter_cls = ReferenceDeleter
    edc_reference_model_updater_cls = ReferenceUpdater

    def save(self, *args, **kwargs):
        self.edc_reference_model_updater_cls(model_obj=self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
