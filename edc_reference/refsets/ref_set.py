from ..site import site_reference_configs


class RefError(Exception):
    pass


class RefSet:
    """An class that represents a queryset of a subject's references for a
    timepoint as a single object.
    """

    def __init__(self, subject_identifier=None, report_datetime=None,
                 timepoint=None, model=None, reference_model_cls=None):
        self.report_datetime = report_datetime
        self.subject_identifier = subject_identifier
        self.timepoint = timepoint
        self.model = model
        self._fields = dict.fromkeys(
            site_reference_configs.get_fields(self.model))
        try:
            self._fields.pop('report_datetime')
        except KeyError:
            pass
        for field_name in self._fields:
            opts = dict(
                identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
                timepoint=timepoint,
                field_name=field_name)
            try:
                reference = reference_model_cls.objects.get(**opts)
            except reference_model_cls.DoesNotExist:
                pass
            else:
                self._fields.update({field_name: reference.value})
        for key, value in self._fields.items():
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
        self._fields.update(report_datetime=self.report_datetime)

    def __repr__(self):
        return (f'{self.__class__.__name__}(model={self.model},'
                f'subject_identifier={self.subject_identifier},'
                f'timepoint={self.timepoint})')
