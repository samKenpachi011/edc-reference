from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_reference.site import site_reference_fields


class ReferenceModelGetter:
    """A class that gets the reference model instance for a given
    model and field name previously created by the given model.

    See also ReferenceModelMixin.
    """

    def __init__(self, model_obj=None, field_name=None,
                 model=None, visit=None, create=None):
        self._object = None
        self.has_value = False
        if model_obj:
            self.model = model_obj._meta.label_lower
            self.model_obj = model_obj
            self.visit = model_obj.visit
        else:
            self.model = model
            self.model_obj = None
            self.visit = visit
        reference_model = site_reference_fields.get_reference_model(
            model=self.model)
        reference_model_cls = django_apps.get_model(reference_model)
        self.field_name = field_name
        try:
            self.object = reference_model_cls.objects.get(**self._options)
        except ObjectDoesNotExist:
            if create:
                self.object = reference_model_cls.objects.create(
                    **self._options)
            else:
                self.object = None
            self.value = None
        else:
            self.value = getattr(self.object, 'value')
            self.has_value = True
        setattr(self, self.field_name, self.value)

    def __repr__(self):
        return (f'<{self.__class__.__name__}({self.model_obj},\'{self.model}.'
                f'{self.field_name}\') value={self.value}, has_value={self.has_value}>')

    @property
    def _options(self):
        return dict(
            identifier=self.visit.subject_identifier,
            model=self.model,
            report_datetime=self.visit.report_datetime,
            timepoint=self.visit.visit_code,
            field_name=self.field_name)
