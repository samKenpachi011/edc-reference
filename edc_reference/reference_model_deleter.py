from django.apps import apps as django_apps


class ReferenceModelDeleter:

    """A class to delete all instances for the reference
    model for this model instance.

    See signals.
    """

    def __init__(self, model_obj=None):
        self.reference_model_cls = django_apps.get_model(
            model_obj.edc_reference_model)
        self.model_obj = model_obj
        self.reference_objects = self.reference_model_cls.objects.filter(
            identifier=self.model_obj.visit.subject_identifier,
            report_datetime=self.model_obj.visit.report_datetime,
            timepoint=self.model_obj.visit.visit_code,
            model=self.model_obj._meta.label_lower)
        self.reference_objects.delete()
