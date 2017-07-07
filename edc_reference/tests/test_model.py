from datetime import date
from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..models import Reference, ReferenceFieldDatatypeNotFound
from ..model_mixins import ReferenceDuplicateField, ReferenceFieldNotFound
from .models import CrfOne, SubjectVisit, CrfWithBadField, CrfWithDuplicateField
from edc_reference.tests.models import CrfWithUnknownDatatype
from uuid import uuid4
from pprint import pprint


class TestModel(TestCase):

    def setUp(self):
        self.subject_identifier = '1'
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='code')

    def test_model_creates_in_reference(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=crf_one.report_datetime,
            field_name='field_str')
        self.assertEqual(reference.value, 'erik')

    def test_model_updates_in_reference(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        crf_one.field_str = 'bob'
        crf_one.save()
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=crf_one.report_datetime,
            field_name='field_str')
        self.assertEqual(reference.value, 'bob')

    def test_model_creates_for_date(self):
        dte = date.today()
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_date=dte)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=crf_one.report_datetime,
            field_name='field_date')
        self.assertEqual(reference.value, dte)

    def test_model_creates_for_datetime(self):
        dte = get_utcnow()
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_datetime=dte)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=crf_one.report_datetime,
            field_name='field_datetime')
        self.assertEqual(reference.value, dte)

    def test_model_creates_for_int(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=crf_one.report_datetime,
            field_name='field_int')
        self.assertEqual(reference.value, integer)

    def test_model_creates_for_all(self):
        strval = 'erik'
        integer = 100
        dte = date.today()
        dtetime = get_utcnow()
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str=strval,
            field_int=integer,
            field_date=dte,
            field_datetime=dtetime)
        for field_name in crf_one.reference_fields:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.visit_code,
                report_datetime=crf_one.report_datetime,
                field_name=field_name)
            self.assertIn(reference.value, [strval, integer, dte, dtetime])

    def test_model_create_handles_none(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=None)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=crf_one.report_datetime,
            field_name='field_int')
        self.assertEqual(reference.value, None)

    def test_model_raises_on_bad_field_name(self):
        self.assertRaises(
            ReferenceFieldNotFound,
            CrfWithBadField.objects.create,
            subject_visit=self.subject_visit,
            field_int=None)

    def test_model_raises_on_duplicate_field_name(self):
        self.assertRaises(
            ReferenceDuplicateField,
            CrfWithDuplicateField.objects.create,
            subject_visit=self.subject_visit,
            field_int=None)

    @tag('1')
    def test_model_raises_on_unknown_field_datatype(self):
        self.assertRaises(
            ReferenceFieldDatatypeNotFound,
            CrfWithUnknownDatatype.objects.create,
            subject_visit=self.subject_visit,
            field_uuid=uuid4())
