from .site import site_reference_configs


class RefError(Exception):
    pass


class Ref:
    """An class that represents a queryset of references as a single object.
    """

    def __init__(self, subject_identifier=None, report_datetime=None,
                 timepoint=None, model=None, reference_model=None):
        self.report_datetime = report_datetime
        self.subject_identifier = subject_identifier
        self.timepoint = timepoint
        self.model = model
        model_values = {}
        model_values = model_values.get(self.model, {})
        model_values.update(model=self.model)
        field_names = site_reference_configs.get_fields(self.model)
        try:
            field_names.pop(field_names.index('report_datetime'))
        except ValueError:
            pass
        model_values.update(report_datetime=self.report_datetime)
        for field_name in field_names:
            opts = dict(
                identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
                timepoint=timepoint,
                field_name=field_name)
            try:
                reference = reference_model.objects.get(**opts)
            except reference_model.DoesNotExist:
                pass
            else:
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

    def __init__(self, subject_identifier=None, visit_model=None, model=None,
                 reference_model=None):
        self.subject_identifier = subject_identifier
        self.ordering = None
        visit_references = reference_model.objects.filter(
            identifier=self.subject_identifier,
            model=visit_model,
            field_name='report_datetime').order_by('report_datetime')
        self._refs = []
        for visit_reference in visit_references:
            self._refs.append(Ref(
                subject_identifier=subject_identifier,
                report_datetime=visit_reference.report_datetime,
                timepoint=visit_reference.timepoint,
                model=model,
                reference_model=reference_model))

    def __repr__(self):
        return f'{self.__class__.__name__}({self._refs})'

    def __iter__(self):
        return iter(self._refs)

    def order_by(self, field_name=None):
        """Re-order by a single field.
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
        self.ordering = field_name
        self._refs.sort(
            key=lambda x: getattr(x, self.ordering), reverse=reverse)
        self._reorder_sets()
        return self

    def _reorder_sets(self):
        for attr in self.__dict__:
            if attr.endswith('_set'):
                setattr(self, attr,
                        [getattr(t, '_set'.join(attr.split('_set')[:-1]))
                         for t in self._refs])

    def get(self, field_name=None):
        setattr(self, f'{field_name}_set',
                [getattr(t, field_name) for t in self._refs])
        return self
