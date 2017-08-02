from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from ..site import site_reference_configs


class ReferenceObjectDoesNotExist(Exception):
    pass


class ReferenceGetter:
    """A class that gets the reference model instance for a given
    model or attributes of the model.

    See also ReferenceModelMixin.
    """

    def __init__(self, field_name=None, model=None, model_obj=None, visit_obj=None,
                 subject_identifier=None, report_datetime=None, visit_code=None,
                 create=None):
        self._object = None
        self.has_value = False
        self.field_name = field_name
        if model_obj:
            try:
                # given a crf model as model_obj
                self.model = model_obj._meta.label_lower
                self.report_datetime = model_obj.visit.report_datetime
                self.subject_identifier = model_obj.visit.subject_identifier
                self.visit_code = model_obj.visit.visit_code
            except AttributeError:
                # given a visit model as model_obj
                self.model = model_obj._meta.label_lower
                self.subject_identifier = model_obj.subject_identifier
                self.report_datetime = model_obj.report_datetime
                self.visit_code = model_obj.visit_code
        elif visit_obj:
            self.model = model
            self.subject_identifier = visit_obj.subject_identifier
            self.report_datetime = visit_obj.report_datetime
            self.visit_code = visit_obj.visit_code
        else:
            # given only the attrs
            self.model = model
            self.subject_identifier = subject_identifier
            self.report_datetime = report_datetime
            self.visit_code = visit_code
        reference_model = site_reference_configs.get_reference_model(
            model=self.model)
        reference_model_cls = django_apps.get_model(reference_model)
        try:
            self.object = reference_model_cls.objects.get(**self._options)
        except ObjectDoesNotExist as e:
            if create:
                self.object = reference_model_cls.objects.create(
                    **self._options)
                self.value = getattr(self.object, 'value')
                self.has_value = True
            else:
                raise ReferenceObjectDoesNotExist(
                    f'{e}. Using {self._options}')
        else:
            self.value = getattr(self.object, 'value')
            self.has_value = True
        setattr(self, self.field_name, self.value)

    def __repr__(self):
        return (f'<{self.__class__.__name__}({self.model}.{self.field_name}\','
                f'\'{self.subject_identifier},{self.report_datetime}'
                f') value={self.value}, has_value={self.has_value}>')

    @property
    def _options(self):
        return dict(
            identifier=self.subject_identifier,
            model=self.model,
            report_datetime=self.report_datetime,
            timepoint=self.visit_code,
            field_name=self.field_name)
