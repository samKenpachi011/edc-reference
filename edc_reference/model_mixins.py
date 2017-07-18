from django.db import models

from .reference import ReferenceDeleter, ReferenceUpdater


class ReferenceModelMixin(models.Model):

    reference_deleter_cls = ReferenceDeleter
    reference_updater_cls = ReferenceUpdater

    def save(self, *args, **kwargs):
        self.reference_updater_cls(model_obj=self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
