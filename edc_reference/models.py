from django.db import models

from edc_base.model_mixins import BaseUuidModel

from .managers import ReferenceManager
from pprint import pprint


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

    objects = ReferenceManager()

    def __str__(self):
        return (f'{self.identifier}@{self.timepoint} {self.model}.'
                f'{self.field_name}={self.value}')

    def update_value(self, value=None, internal_type=None, field=None):
        """Updates the correct `value` field based on the
        field class datatype.
        """
        internal_type = internal_type or field.get_internal_type()
        update = None
        for fld in self._meta.get_fields():
            if fld.name.startswith('value'):  # e.g. value_str, value_int, etc
                if fld.get_internal_type() == internal_type:
                    update = (fld.name, value)
                    break
        if update:
            setattr(self, *update),
        else:
            raise ReferenceFieldDatatypeNotFound(
                f'Reference field internal_type not found. Got \'{internal_type}\'. '
                f'model={self.model}.{self.field_name} '
                f'Expected a django.models.field internal type like \'CharField\', '
                '\'DateTimeField\', etc.')
        self.save()

    @property
    def value(self):
        for field_name in ['value_str', 'value_int', 'value_date', 'value_datetime']:
            value = getattr(self, field_name)
            if value is not None:
                break
        return value

    class Meta:
        unique_together = ['identifier', 'timepoint',
                           'report_datetime', 'model', 'field_name']
        index_together = ['identifier', 'timepoint',
                          'report_datetime', 'model', 'field_name']
        ordering = ('identifier', 'report_datetime')
