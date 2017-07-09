from django.test import TestCase, tag

from ..site import site_reference_fields, ReferenceModelConfig
from ..site import AlreadyRegistered, SiteReferenceFieldsImportError
from ..site import ReferenceFieldValidationError, ReferenceModelValidationError
from ..site import ReferenceDuplicateField


@tag('site')
class TestSite(TestCase):

    def test_site_register(self):
        model = 'edc_reference.crfone'
        fields = [
            'field_date', 'field_datetime', 'field_int', 'field_str', ]
        site_reference_fields.registry = {}
        reference = ReferenceModelConfig(fields=fields, model=model)
        site_reference_fields.register(reference=reference)
        self.assertEqual(fields, site_reference_fields.get_fields(model))

    def test_site_reregister(self):
        model = 'edc_reference.crfone'
        site_reference_fields.registry = {}
        reference = ReferenceModelConfig(
            fields=['field_date', 'field_datetime',
                    'field_int', 'field_str', ],
            model=model)
        site_reference_fields.register(reference=reference)
        self.assertRaises(
            AlreadyRegistered, site_reference_fields.register, reference=reference)

    def test_autodiscover(self):
        site_reference_fields.registry = {}
        site_reference_fields.loaded = False
        site_reference_fields.autodiscover('tests.reference_fields')
        self.assertTrue(site_reference_fields.loaded)
        self.assertIn('edc_reference.erik', list(
            site_reference_fields.registry))

        self.assertEqual(['f1', 'f2', 'f3', 'f4'],
                         site_reference_fields.get_fields('edc_reference.erik'))

    def test_autodiscover_bad(self):
        self.assertRaises(
            SiteReferenceFieldsImportError,
            site_reference_fields.autodiscover, 'tests.reference_fields_bad')

    def test_validate_ok(self):
        model = 'edc_reference.crfone'
        fields = [
            'field_str', 'field_date', 'field_datetime', 'field_int']
        site_reference_fields.registry = {}
        reference = ReferenceModelConfig(fields=fields, model=model)
        try:
            reference.validate()
        except (ReferenceFieldValidationError, ReferenceModelValidationError) as e:
            self.fail(
                f'Reference validation error unexpectedly raised. Got{e}')

    def test_validate_ok2(self):
        model = 'edc_reference.crfone'
        site_reference_fields.registry = {}
        reference = ReferenceModelConfig(
            fields=['field_str', 'field_date', 'field_datetime', 'field_int'],
            model=model)
        site_reference_fields.register(reference=reference)
        site_reference_fields.validate()

    def test_validate_bad_model(self):
        model = 'edc_reference.erik'
        fields = ['f1']
        reference = ReferenceModelConfig(fields=fields, model=model)
        self.assertRaises(
            ReferenceModelValidationError,
            reference.validate)

    def test_validate_bad_fields(self):
        model = 'edc_reference.crfone'
        fields = ['f1']
        site_reference_fields.registry = {}
        reference = ReferenceModelConfig(fields=fields, model=model)
        self.assertRaises(
            ReferenceFieldValidationError,
            reference.validate)

    def test_raises_on_duplicate_field_name(self):
        model = 'edc_reference.crfone'
        fields = ['f1', 'f1']
        self.assertRaises(
            ReferenceDuplicateField,
            ReferenceModelConfig, fields=fields, model=model)
