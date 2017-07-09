from django.db import models

from .reference_model_deleter import ReferenceModelDeleter
from .reference_model_updater import ReferenceModelUpdater


class ReferenceModelMixin(models.Model):

    edc_reference_model_deleter_cls = ReferenceModelDeleter
    edc_reference_model_updater_cls = ReferenceModelUpdater

    def save(self, *args, **kwargs):
        self.edc_reference_model_updater_cls(model_obj=self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
