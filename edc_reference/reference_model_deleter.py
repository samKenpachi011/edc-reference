from django.apps import apps as django_apps
from django.db import transaction

from .site import site_reference_configs


class ReferenceModelDeleter:

    """A class to delete all instances for the reference
    model for this model instance.

    See signals.
    """

    def __init__(self, model_obj=None):
        reference_model = site_reference_configs.get_reference_model(
            model=model_obj._meta.label_lower)
        self.reference_model_cls = django_apps.get_model(reference_model)
        self.model_obj = model_obj
        self.reference_objects = self.reference_model_cls.objects.filter(
            **self.options)
        with transaction.atomic():
            self.reference_objects.delete()

    @property
    def options(self):
        return dict(
            identifier=self.model_obj.visit.subject_identifier,
            report_datetime=self.model_obj.visit.report_datetime,
            timepoint=self.model_obj.visit.visit_code,
            model=self.model_obj._meta.label_lower)
