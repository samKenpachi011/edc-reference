from django.apps import apps as django_apps


class ReferenceModelGetter:
    """A class that gets the reference model instance for a given
    model and field name previously created by the given model.

    See also ReferenceModelMixin.
    """

    def __init__(self, model_obj=None, field_name=None,
                 model=None, visit=None, reference_model=None):
        self._object = None
        self.has_value = False
        if model_obj:
            self.model = model_obj._meta.label_lower
            self.model_obj = model_obj
            self.reference_model_cls = django_apps.get_model(
                model_obj.edc_reference_model)
            self.visit = model_obj.visit
        else:
            self.model = model
            self.model_obj = None
            self.reference_model_cls = django_apps.get_model(reference_model)
            self.visit = visit
        self.field_name = field_name
        self.value = getattr(self.object, 'value')
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

    @property
    def object(self):
        if not self._object:
            try:
                self._object = self.reference_model_cls.objects.get(
                    **self._options)
            except self.reference_model_cls.DoesNotExist:
                self._object = self.reference_model_cls.objects.create(
                    **self._options)
            else:
                self.has_value = True
        return self._object
