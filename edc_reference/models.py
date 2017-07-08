from django.db import models

from edc_base.model_mixins import BaseUuidModel


class ReferenceFieldDatatypeNotFound(Exception):
    pass


class Reference(BaseUuidModel):

    identifier = models.CharField(max_length=50)

    timepoint = models.CharField(max_length=50)

    report_datetime = models.DateTimeField()

    model = models.CharField(max_length=50)

    field_name = models.CharField(max_length=50)

    datatype = models.CharField(max_length=50)

    value_str = models.CharField(max_length=50, null=True)

    value_int = models.IntegerField(null=True)

    value_date = models.DateField(null=True)

    value_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.identifier}@{self.timepoint} {self.model}.{self.field_name}'

    def update_value(self, value=None, field=None, model=None):
        """Updates the correct `value` field based on the
        field class datatype.
        """
        self.label_lower = model
        self.datatype = field.get_internal_type()
        update = None
        for fld in self._meta.get_fields():
            if fld.name.startswith('value'):
                if fld.get_internal_type() == self.datatype:
                    update = (fld.name, value)
                    break
        if update:
            setattr(self, *update),
        else:
            raise ReferenceFieldDatatypeNotFound(
                f'Reference field datatype not found. Got {model}.{field.name}.')

    @property
    def value(self):
        for field_name in ['value_str', 'value_int', 'value_date', 'value_datetime']:
            value = getattr(self, field_name)
            if value:
                break
        return value

    class Meta:
        unique_together = ['identifier', 'timepoint',
                           'report_datetime', 'model', 'field_name']
        index_together = ['identifier', 'timepoint',
                          'report_datetime', 'model', 'field_name']
