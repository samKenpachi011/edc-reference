from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from uuid import uuid4

from edc_base.utils import get_utcnow

from ..models import Reference, ReferenceFieldDatatypeNotFound
from ..reference_model_deleter import ReferenceModelDeleter
from ..reference_model_getter import ReferenceModelGetter
from ..reference_model_updater import ReferenceFieldNotFound, ReferenceDuplicateField
from ..reference_model_updater import ReferenceModelUpdater
from .models import CrfOne, SubjectVisit, CrfWithBadField, CrfWithDuplicateField
from .models import CrfWithUnknownDatatype, TestModel


class TestReferenceModel(TestCase):

    def setUp(self):
        self.subject_identifier = '1'
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='code')

    def test_updater_repr(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        model_obj.reference_model = 'edc_reference.reference'
        self.assertTrue(repr(ReferenceModelUpdater(model_obj=model_obj)))

    def test_model_repr(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        model_obj.reference_model = 'edc_reference.reference'
        ReferenceModelUpdater(model_obj=model_obj)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            field_name='field_str')
        self.assertTrue(repr(reference))

    def test_updater_creates_reference(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        model_obj.reference_model = 'edc_reference.reference'
        ReferenceModelUpdater(model_obj=model_obj)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            field_name='field_str')
        self.assertEqual(reference.value, 'erik')

    def test_updater_updates_reference(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        model_obj.reference_model = 'edc_reference.reference'
        ReferenceModelUpdater(model_obj=model_obj)
        model_obj.field_str = 'bob'
        ReferenceModelUpdater(model_obj=model_obj)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            field_name='field_str')
        self.assertEqual(reference.value, 'bob')

    def test_deleter(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        model_obj.reference_model = 'edc_reference.reference'
        ReferenceModelUpdater(model_obj=model_obj)
        model_obj.delete()
        ReferenceModelDeleter(model_obj=model_obj)
        try:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.visit_code,
                field_name='field_str')
        except ObjectDoesNotExist:
            pass
        else:
            self.fail(f'Object unexpectedly exists. Got {reference}')

    def test_model_mixin_deleter(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        crf_one.delete()
        self.assertEqual(0, Reference.objects.all().count())

    def test_model_creates_reference(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        self.assertEqual(len(crf_one.edc_reference_fields), 4)
        self.assertEqual(len(crf_one.edc_reference_fields),
                         Reference.objects.all().count())

    def test_model_creates_reference2(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        try:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.visit_code,
                report_datetime=self.subject_visit.report_datetime,
                model=crf_one._meta.label_lower,
                field_name='field_str')
        except ObjectDoesNotExist as e:
            self.fail(f'ObjectDoesNotExist unexpectedly raised. Got {e}')
        self.assertEqual(reference.value, 'erik')

    def test_model_updates_reference(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        crf_one.field_str = 'bob'
        crf_one.save()
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=self.subject_visit.report_datetime,
            field_name='field_str')
        self.assertEqual(reference.value, 'bob')

    def test_model_creates_for_date(self):
        dte = date.today()
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_date=dte)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=self.subject_visit.report_datetime,
            field_name='field_date')
        self.assertEqual(reference.value, dte)

    def test_model_creates_for_datetime(self):
        dte = get_utcnow()
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_datetime=dte)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=self.subject_visit.report_datetime,
            field_name='field_datetime')
        self.assertEqual(reference.value, dte)

    def test_model_creates_for_int(self):
        integer = 100
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=self.subject_visit.report_datetime,
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
        for field_name in crf_one.edc_reference_fields:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.visit_code,
                report_datetime=self.subject_visit.report_datetime,
                field_name=field_name)
            self.assertIn(reference.value, [strval, integer, dte, dtetime])

    def test_model_create_handles_none(self):
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=None)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            report_datetime=self.subject_visit.report_datetime,
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

    def test_model_raises_on_unknown_field_datatype(self):
        self.assertRaises(
            ReferenceFieldDatatypeNotFound,
            CrfWithUnknownDatatype.objects.create,
            subject_visit=self.subject_visit,
            field_uuid=uuid4())

    def test_getter_repr(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=100)
        reference = ReferenceModelGetter(
            field_name='field_int',
            model_obj=crf_one)
        self.assertTrue(repr(reference))

    def test_reference_getter_sets_attr(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer)
        reference = ReferenceModelGetter(
            field_name='field_int',
            model_obj=crf_one)
        self.assertEqual(reference.field_int, integer)

    def test_reference_getter_sets_attr_even_if_none(self):
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit)
        reference = ReferenceModelGetter(
            field_name='field_int',
            model_obj=crf_one)
        self.assertEqual(reference.field_int, None)

    def test_reference_getter_without_model_obj(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer)
        reference = ReferenceModelGetter(
            field_name='field_int',
            model='edc_reference.crfone',
            visit=crf_one.visit,
            reference_model=crf_one.edc_reference_model)
        self.assertEqual(reference.field_int, integer)
