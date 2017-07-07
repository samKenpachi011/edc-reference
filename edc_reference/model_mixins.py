from django.db import models

from .models import Reference


class ReferenceDuplicateField(Exception):
    pass


class ReferenceFieldNotFound(Exception):
    pass


class ReferenceModelMixin(models.Model):

    reference_fields = []

    def save(self, *args, **kwargs):
        edc_reference_fields = list(set(self.edc_reference_fields))
        if len(edc_reference_fields) != len(self.edc_reference_fields):
            raise ReferenceDuplicateField(
                f'Duplicate field detected. Got {self.edc_reference_fields}. '
                f'See model \'{self._meta.verbose_name}\'')
        for field_name in edc_reference_fields:
            try:
                reference = Reference.objects.get(
                    identifier=self.subject_visit.subject_identifier,
                    report_datetime=self.report_datetime,
                    timepoint=self.subject_visit.visit_code,
                    model=self._meta.label_lower,
                    field_name=field_name)
            except Reference.DoesNotExist:
                reference = Reference.objects.create(
                    identifier=self.subject_visit.subject_identifier,
                    report_datetime=self.report_datetime,
                    model=self._meta.label_lower,
                    timepoint=self.subject_visit.visit_code,
                    field_name=field_name)
            try:
                field = [fld for fld in self._meta.get_fields() if fld.name ==
                         field_name][0]
            except IndexError:
                raise ReferenceFieldNotFound(
                    f'Reference field not found. Got \'{field_name}\'. '
                    f'See {self._meta.verbose_name}.')
            value = getattr(self, field_name)
            reference.update_value(value=value, field=field)
            reference.save()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
