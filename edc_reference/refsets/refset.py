from ..site import site_reference_configs
from edc_reference.site import SiteReferenceFieldsError
from pprint import pprint


class RefsetError(Exception):
    pass


class RefsetOverlappingField(Exception):
    pass


class Refset:
    """An class that represents a queryset of a subject's references for a
    timepoint as a single object.
    """

    ordering_attrs = ['report_datetime', 'timepoint']

    def __init__(self, subject_identifier=None, report_datetime=None,
                 timepoint=None, model=None, reference_model_cls=None):
        # checking for these values so that field values
        # that are None are so because the reference instance
        # does not exist and not because these values were none.
        if not report_datetime:
            raise RefsetError('Expected report_datetime. Got None')
        if not timepoint:
            raise RefsetError('Expected timepoint. Got None')
        if not subject_identifier:
            raise RefsetError('Expected subject_identifier. Got None')
        self.subject_identifier = subject_identifier
        self.report_datetime = report_datetime
        self.timepoint = timepoint
        self.model = model
        opts = dict(
            identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            timepoint=timepoint)
        try:
            self._fields = dict.fromkeys(
                site_reference_configs.get_fields(self.model))
        except SiteReferenceFieldsError as e:
            raise RefsetError(f'{e}. See {repr(self)}')
        try:
            self._fields.pop('report_datetime')
        except KeyError:
            pass
        self.ordering_attrs.extend(list(self._fields))
        try:
            references = reference_model_cls.objects.filter(**opts)
        except AttributeError as e:
            raise RefsetError(e)
        if references:
            self._fields.update(report_datetime=self.report_datetime)
            for field_name in self._fields:
                try:
                    obj = references.get(field_name=field_name)
                except reference_model_cls.DoesNotExist as e:
                    pass
                else:
                    self._fields.update({field_name: obj.value})
            for key, value in self._fields.items():
                try:
                    existing_value = getattr(self, key)
                except AttributeError:
                    setattr(self, key, value)
                else:
                    if existing_value == value:
                        setattr(self, key, value)
                    else:
                        raise RefsetOverlappingField(
                            f'Attribute {key} already exists with a different value. '
                            f'Got {existing_value} == {value}. See {self.model}')

    def __repr__(self):
        return (f'{self.__class__.__name__}(model={self.model},'
                f'subject_identifier={self.subject_identifier},'
                f'timepoint={self.timepoint})')
