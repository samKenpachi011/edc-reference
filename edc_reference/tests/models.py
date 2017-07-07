from django.db import models
from django.db.models.deletion import PROTECT

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..model_mixins import ReferenceModelMixin


class SubjectVisit(BaseUuidModel):

    subject_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=50)


class CrfOne(ReferenceModelMixin, BaseUuidModel):

    edc_reference_fields = ['field_str', 'field_date',
                            'field_datetime', 'field_int']

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithBadField(ReferenceModelMixin, BaseUuidModel):

    edc_reference_fields = ['blah1', 'blah2', 'blah3', 'blah4']

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithDuplicateField(ReferenceModelMixin, BaseUuidModel):

    edc_reference_fields = [
        'field_int', 'field_int', 'field_datetime', 'field_str']

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithUnknownDatatype(ReferenceModelMixin, BaseUuidModel):

    edc_reference_fields = ['field_uuid', ]

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_uuid = models.UUIDField()
