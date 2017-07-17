from .models import Reference
from .site import site_reference_configs


class RefError(Exception):
    pass


class Ref:
    """An class that represents a queryset of references as a single object.
    """

    def __init__(self, subject_identifier=None, report_datetime=None,
                 timepoint=None, model=None):
        self.report_datetime = report_datetime
        self.subject_identifier = subject_identifier
        self.timepoint = timepoint
        self.model = model
        model_values = {}
        model_values = model_values.get(self.model, {})
        model_values.update(model=self.model)
        field_names = site_reference_configs.get_fields(self.model)
        for field_name in field_names:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
                timepoint=timepoint,
                field_name=field_name)
            model_values.update({field_name: reference.value})
        for key, value in model_values.items():
            try:
                existing_value = getattr(self, key)
            except AttributeError:
                setattr(self, key, value)
            else:
                if existing_value == value:
                    setattr(self, key, value)
                else:
                    raise RefError(
                        f'Attribute {key} already exists with a different value. '
                        f'Got {existing_value} == {value}. See {self.model}')

    def __repr__(self):
        return (f'{self.__class__.__name__}(model={self.model},'
                f'subject_identifier={self.subject_identifier},'
                f'timepoint={self.timepoint})')


class LongitudinalRefSet:
    """A class that is a collection of a subject's `Ref` objects for
    a given visit model.
    """

    def __init__(self, subject_identifier=None, visit_model=None, model=None):
        self.subject_identifier = subject_identifier
        self.ordering = None
        visit_references = Reference.objects.filter(
            identifier=self.subject_identifier,
            model=visit_model,
            field_name='report_datetime').order_by('report_datetime')
        self._refs = []
        for visit_reference in visit_references:
            self._refs.append(Ref(
                subject_identifier=subject_identifier,
                report_datetime=visit_reference.report_datetime,
                timepoint=visit_reference.timepoint,
                model=model))

    def __repr__(self):
        return f'{self.__class__.__name__}({self._refs})'

    def __iter__(self):
        return iter(self._refs)

    def order_by(self, field_name=None):
        """Re-order by a single timepoint field.
        """
        if not field_name:
            field_name = 'report_datetime'
            self.ordering = field_name
            reverse = False
        elif field_name.startswith('-'):
            field_name = field_name[1:]
            reverse = True
        else:
            reverse = False
        self._refs.sort(key=lambda x: getattr(
            x, field_name), reverse=reverse)
        self.ordering = field_name

    def get(self, field_name=None):
        return [getattr(t, field_name) for t in self._refs]
