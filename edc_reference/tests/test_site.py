from django.test import TestCase, tag

from ..reference_model_config import ReferenceModelConfig
from ..reference_model_config import ReferenceFieldValidationError, ReferenceDuplicateField
from ..reference_model_config import ReferenceModelValidationError
from ..site import site_reference_configs
from ..site import AlreadyRegistered, SiteReferenceConfigImportError
from ..site import SiteReferenceConfigError, ReferenceConfigNotRegistered
from .dummy import DummySite, DummyVisitSchedule, DummySchedule


class TestSite(TestCase):

    def test_site_register(self):
        model = 'edc_reference.crfone'
        fields = [
            'field_date', 'field_datetime', 'field_int', 'field_str', ]
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(fields=fields, model=model)
        site_reference_configs.register(reference=reference)
        self.assertEqual(fields, site_reference_configs.get_fields(model))

    def test_site_reregister(self):
        model = 'edc_reference.crfone'
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(
            fields=['field_date', 'field_datetime',
                    'field_int', 'field_str', ],
            model=model)
        site_reference_configs.register(reference=reference)
        self.assertRaises(
            AlreadyRegistered, site_reference_configs.register, reference=reference)

    def test_autodiscover(self):
        site_reference_configs.registry = {}
        site_reference_configs.loaded = False
        site_reference_configs.autodiscover('tests.reference_fields')
        self.assertTrue(site_reference_configs.loaded)
        self.assertIn('edc_reference.erik', list(
            site_reference_configs.registry))

        self.assertEqual(['f1', 'f2', 'f3', 'f4'],
                         site_reference_configs.get_fields('edc_reference.erik'))

    def test_autodiscover_bad(self):
        self.assertRaises(
            SiteReferenceConfigImportError,
            site_reference_configs.autodiscover, 'tests.reference_fields_bad')

    def test_validate_ok(self):
        model = 'edc_reference.crfone'
        fields = [
            'field_str', 'field_date', 'field_datetime', 'field_int']
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(fields=fields, model=model)
        try:
            reference.validate()
        except (ReferenceFieldValidationError, ReferenceModelValidationError) as e:
            self.fail(
                f'Reference validation error unexpectedly raised. Got{e}')

    def test_validate_ok2(self):
        model = 'edc_reference.crfone'
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(
            fields=['field_str', 'field_date', 'field_datetime', 'field_int'],
            model=model)
        site_reference_configs.register(reference=reference)
        site_reference_configs.validate()

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
        site_reference_configs.registry = {}
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

    def test_not_registered_for_fields(self):
        model = 'edc_reference.crfone'
        site_reference_configs.registry = {}
        self.assertRaises(
            SiteReferenceConfigError,
            site_reference_configs.get_fields, model)

    def test_not_registered_for_reference_model(self):
        model = 'edc_reference.crfone'
        site_reference_configs.registry = {}
        self.assertRaises(
            SiteReferenceConfigError,
            site_reference_configs.get_reference_model, model)

    def test_not_registered_for_reregister(self):
        model = 'edc_reference.crfone'
        fields = ['f1']
        reference = ReferenceModelConfig(fields=fields, model=model)
        site_reference_configs.registry = {}
        self.assertRaises(
            ReferenceConfigNotRegistered,
            site_reference_configs.reregister, reference)

    def test_get_config(self):
        model = 'edc_reference.crfone'
        fields = ['f1']
        reference = ReferenceModelConfig(fields=fields, model=model)
        site_reference_configs.register(reference)
        self.assertEqual(
            reference, site_reference_configs.get_config(model='edc_reference.crfone'))
        self.assertRaises(
            SiteReferenceConfigError,
            site_reference_configs.get_config, model=None)

    def test_register_reference_models_from_visit_schedule(self):
        site_visit_schedules = DummySite()
        visit_schedule = DummyVisitSchedule()
        schedule = DummySchedule()
        visit_schedule.schedules.update(schedule=schedule)
        site_visit_schedules.registry.update(visit_schedule=visit_schedule)
        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            site_visit_schedules=site_visit_schedules)
        self.assertTrue(
            site_reference_configs.get_config(model='edc_reference.crfone'))

    def test_reregister_reference_models_from_visit_schedule(self):
        site_visit_schedules = DummySite()
        visit_schedule = DummyVisitSchedule()
        schedule = DummySchedule()
        visit_schedule.schedules.update(schedule=schedule)
        site_visit_schedules.registry.update(visit_schedule=visit_schedule)
        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            site_visit_schedules=site_visit_schedules)
        # do again
        site_reference_configs.register_from_visit_schedule(
            site_visit_schedules=site_visit_schedules)
        self.assertTrue(
            site_reference_configs.get_config(model='edc_reference.crfone'))

    def test_add_fields_to_reference_config(self):
        model = 'edc_reference.crfone'
        fields = ['f1']
        site_reference_configs.registry = {}
        reference_config = ReferenceModelConfig(fields=fields, model=model)
        site_reference_configs.register(reference_config)
        self.assertEqual(reference_config.field_names, ['f1'])
        site_reference_configs.add_fields_to_config(model, ['f2', 'f3'])
        self.assertEqual(reference_config.field_names, ['f1', 'f2', 'f3'])
