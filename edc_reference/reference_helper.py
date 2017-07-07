from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class ReferenceHelper:

    reference_model = 'edc_reference.reference'

    def __init__(self, field_name=None, visit=None, model=None, **kwargs):
        self.reference_model_cls = django_apps.get_model(self.reference_model)
        self.visit = visit
        self.model = model
        self.field_name = field_name
        try:
            reference_object = self.reference_model_cls.objects.get(
                identifier=self.visit.subject_identifier,
                model=self.model,
                timepoint=self.visit.visit_code,
                field_name=self.field_name)
        except ObjectDoesNotExist:
            pass
        else:
            setattr(self, field_name, getattr(reference_object, 'value'))
