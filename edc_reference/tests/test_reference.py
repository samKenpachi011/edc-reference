from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from uuid import uuid4

from edc_base.utils import get_utcnow

from ..models import Reference, ReferenceFieldDatatypeNotFound
from ..reference_model_config import ReferenceModelConfig
from ..reference_model_config import ReferenceDuplicateField, ReferenceFieldValidationError
from ..reference_model_deleter import ReferenceModelDeleter
from ..reference_model_getter import ReferenceModelGetter
from ..reference_model_updater import ReferenceModelUpdater, ReferenceFieldNotFound
from ..site import site_reference_fields, SiteReferenceFieldsError
from .models import CrfOne, SubjectVisit
from .models import CrfWithUnknownDatatype, TestModel, SubjectRequisition


class TestReferenceModel(TestCase):

    def setUp(self):
        site_reference_fields.registry = {}
        self.subject_identifier = '1'
        subjectvisit_reference = ReferenceModelConfig(
            model='edc_reference.subjectvisit',
            fields=['report_datetime', 'visit_code'])
        self.testmodel_reference = ReferenceModelConfig(
            model='edc_reference.testmodel', fields=['field_str'])
        self.crfone_reference = ReferenceModelConfig(
            model='edc_reference.crfone',
            fields=['field_str', 'field_date', 'field_datetime', 'field_int'])
        site_reference_fields.register(subjectvisit_reference)
        site_reference_fields.register(self.testmodel_reference)
        site_reference_fields.register(self.crfone_reference)
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='code')

    @tag('2')
    def test_updater_repr(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        self.assertTrue(repr(ReferenceModelUpdater(model_obj=model_obj)))

    def test_model_repr(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
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
        ReferenceModelUpdater(model_obj=model_obj)
        model_obj.field_str = 'bob'
        ReferenceModelUpdater(model_obj=model_obj)
        reference = Reference.objects.get(
            identifier=self.subject_identifier,
            timepoint=self.subject_visit.visit_code,
            field_name='field_str')
        self.assertEqual(reference.value, 'bob')

    def test_updater_with_bad_field_name(self):
        site_reference_fields.registry = {}
        self.testmodel_reference = ReferenceModelConfig(
            model='edc_reference.testmodel', fields=['blah'])
        site_reference_fields.register(self.testmodel_reference)
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        self.assertRaises(
            ReferenceFieldNotFound,
            ReferenceModelUpdater, model_obj=model_obj)

    def test_deleter(self):
        model_obj = TestModel.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
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
        self.assertGreater(Reference.objects.filter(
            model='edc_reference.crfone').count(), 2)
        crf_one.delete()
        self.assertEqual(0, Reference.objects.filter(
            model='edc_reference.crfone').count())

    def test_model_creates_reference(self):
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        self.assertEqual(
            len(site_reference_fields.get_fields(
                'edc_reference.crfone')), 4)
        self.assertEqual(Reference.objects.all().count(), 6)

    def test_model_creates_reference2(self):
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str='erik')
        try:
            reference = Reference.objects.get(
                identifier=self.subject_identifier,
                timepoint=self.subject_visit.visit_code,
                report_datetime=self.subject_visit.report_datetime,
                model='edc_reference.crfone',
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
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str=strval,
            field_int=integer,
            field_date=dte,
            field_datetime=dtetime)
        for field_name in site_reference_fields.get_fields('edc_reference.crfone'):
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

    def test_model_raises_on_duplicate_field_name(self):
        self.assertRaises(
            ReferenceDuplicateField,
            ReferenceModelConfig,
            model='edc_reference.crfwithduplicatefield',
            fields=['field_int', 'field_int', 'field_datetime', 'field_str'])

    def test_model_raises_on_bad_field_name(self):
        reference_config = ReferenceModelConfig(
            model='edc_reference.crfwithbadfield',
            fields=['blah1', 'blah2', 'blah3', 'blah4'])
        self.assertRaises(
            ReferenceFieldValidationError,
            reference_config.validate)

    def test_model_raises_on_bad_field_name_validated_by_site(self):
        reference_config = ReferenceModelConfig(
            model='edc_reference.crfwithbadfield',
            fields=['blah1', 'blah2', 'blah3', 'blah4'])
        site_reference_fields.register(reference_config)
        self.assertRaises(
            SiteReferenceFieldsError,
            site_reference_fields.validate)

    def test_raises_on_missing_model_mixin(self):
        reference_config = ReferenceModelConfig(
            model='edc_reference.TestModel',
            fields=['report_datetime'])
        site_reference_fields.reregister(reference_config)
        self.assertRaises(
            SiteReferenceFieldsError,
            site_reference_fields.validate)

    def test_model_raises_on_unknown_field_datatype(self):
        reference_config = ReferenceModelConfig(
            model='edc_reference.CrfWithUnknownDatatype',
            fields=['field_uuid'])
        site_reference_fields.register(reference_config)
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

    def test_site_validates_no_fields_raises(self):
        model = 'edc_reference.crfone'
        site_reference_fields.registry = {}
        self.assertRaises(
            ReferenceFieldValidationError,
            ReferenceModelConfig,
            fields=[],
            model=model)

    def test_site_validates_no_fields_raises2(self):
        model = 'edc_reference.crfone'
        site_reference_fields.registry = {}
        self.assertRaises(
            ReferenceFieldValidationError,
            ReferenceModelConfig,
            model=model)

    def test_reference_getter_without_crf_type_model(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer)
        reference = ReferenceModelGetter(
            field_name='field_int',
            model='edc_reference.crfone',
            visit_obj=crf_one.visit)
        self.assertEqual(reference.field_int, integer)

    def test_reference_getter_with_bad_field(self):
        integer = 100
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_int=integer)
        reference = ReferenceModelGetter(
            field_name='blah',
            model='edc_reference.crfone',
            model_obj=crf_one.visit)
        self.assertFalse(reference.has_value)
        self.assertIsNone(reference.value)

    def test_model_manager_crf(self):
        strval = 'erik'
        integer = 100
        dte = date.today()
        dtetime = get_utcnow()
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str=strval,
            field_int=integer,
            field_date=dte,
            field_datetime=dtetime)
        qs = Reference.objects.filter_crf_for_visit(
            'edc_reference.crfone', self.subject_visit)
        self.assertEqual(qs.count(), 4)

    def test_model_manager_crf_by_field(self):
        strval = 'erik'
        integer = 100
        dte = date.today()
        dtetime = get_utcnow()
        CrfOne.objects.create(
            subject_visit=self.subject_visit,
            field_str=strval,
            field_int=integer,
            field_date=dte,
            field_datetime=dtetime)
        obj = Reference.objects.get_crf_for_visit(
            'edc_reference.crfone', self.subject_visit, 'field_str')
        self.assertEqual(obj.value, 'erik')
        obj = Reference.objects.get_crf_for_visit(
            'edc_reference.crfone', self.subject_visit, 'field_int')
        self.assertEqual(obj.value, integer)
        obj = Reference.objects.get_crf_for_visit(
            'edc_reference.crfone', self.subject_visit, 'field_date')
        self.assertEqual(obj.value, dte)
        obj = Reference.objects.get_crf_for_visit(
            'edc_reference.crfone', self.subject_visit, 'field_datetime')
        self.assertEqual(obj.value, dtetime)
        obj = Reference.objects.get_crf_for_visit(
            'edc_reference.crfone', self.subject_visit, 'blah')
        self.assertIsNone(obj)

    def test_model_manager_requisition(self):
        reference_config = ReferenceModelConfig(
            model='edc_reference.subjectrequisition',
            fields=['panel_name'])
        site_reference_fields.register(reference_config)
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name='cd4')
        obj = Reference.objects.get_requisition_for_visit(
            'edc_reference.subjectrequisition', self.subject_visit, panel_name='cd4')
        self.assertEqual(obj.value, 'cd4')
        obj = Reference.objects.get_requisition_for_visit(
            'edc_reference.subjectrequisition', self.subject_visit, panel_name='blah')
        self.assertIsNone(obj)
