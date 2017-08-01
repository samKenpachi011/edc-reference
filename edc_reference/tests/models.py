from django.db import models
from django.db.models.deletion import PROTECT

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..model_mixins import ReferenceModelMixin


class CrfModelMixin(models.Model):

    @property
    def visit(self):
        return self.subject_visit

    class Meta:
        abstract = True


class SubjectVisit(ReferenceModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=50)


class SubjectRequisition(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    panel_name = models.CharField(max_length=50)


class TestModel(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)


class CrfOne(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithBadField(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithDuplicateField(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_str = models.CharField(max_length=50)

    field_date = models.DateField(null=True)

    field_datetime = models.DateTimeField(null=True)

    field_int = models.IntegerField(null=True)


class CrfWithUnknownDatatype(CrfModelMixin, ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    field_uuid = models.UUIDField()
