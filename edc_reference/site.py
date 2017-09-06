import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule
from django.core.management.color import color_style

from .reference_model_config import ReferenceDuplicateField, ReferenceModelValidationError
from .reference_model_config import ReferenceFieldValidationError
from .reference_model_config import ReferenceModelConfig
from edc_reference.reference_model_config import ReferenceFieldAlreadyAdded


class AlreadyRegistered(Exception):
    pass


class ReferenceConfigNotRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteReferenceConfigImportError(Exception):
    pass


class SiteReferenceConfigError(Exception):
    pass


class ReferenceUpdater:

    def update(self, model=None, fields=None, get_config=None):
        try:
            reference = get_config(model)
        except SiteReferenceConfigError:
            reference = ReferenceModelConfig(
                model=model,
                fields=fields)
        else:
            for field in fields:
                try:
                    reference.add_fields([field])
                except ReferenceFieldAlreadyAdded:
                    pass
        return reference


class Site:

    reference_updater = ReferenceUpdater()

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, reference=None):
        model = reference.model.lower()
        if model in self.registry:
            raise AlreadyRegistered(
                f'Reference fields have already been registered. '
                f'Got {reference.model}')
        self.registry.update({model: reference})
        self.loaded = True

    def reregister(self, reference=None):
        if reference.model not in self.registry:
            raise ReferenceConfigNotRegistered(
                f'Reregister failed. Reference model configuration has not '
                f'been registered. Got {reference.model}')
        self.registry.update({reference.model: reference})

    def unregister(self, model=None):
        if model not in self.registry:
            raise ReferenceConfigNotRegistered(
                f'Unregister failed. Reference model configuration has not '
                f'been registered. Got {model}')
        self.registry = {k: v for k, v in self.registry.items() if k != model}

    def get_config(self, model=None):
        try:
            reference_config = self.registry.get(model.lower())
        except AttributeError:
            reference_config = None
        if not reference_config:
            raise SiteReferenceConfigError(
                f'Model not registered. Got {model}')
        return reference_config

    def get_fields(self, model=None):
        """Returns a list of fields associated with the
        reference configuration of "model".
        """
        return self.get_config(model).field_names

    def get_reference_model(self, model=None):
        """Returns the reference model associated with the
        reference configuration of "model".
        """
        return self.get_config(model).reference_model

    def validate(self):
        """Validates the reference data for all classes in the
        registry.
        """
        style = color_style()
        sys.stdout.write('Validating site reference models and fields.\n')
        for model, reference in self.registry.items():
            sys.stdout.write(f' (*) {model} ...    \r')
            try:
                reference.validate()
            except (ReferenceDuplicateField, ReferenceModelValidationError,
                    ReferenceFieldValidationError) as e:
                sys.stdout.write(
                    f' ( ) {model}. {style.ERROR("ERROR!!")}    \n')
                raise SiteReferenceConfigError(e) from e
            else:
                sys.stdout.write(f' (*) {model}. {style.SUCCESS("OK")}    \n')
        sys.stdout.write('Done.\n')

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the reference_model_configs.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or 'reference_model_configs'
        sys.stdout.write(f' * checking for {module_name} ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_reference_configs.registry)
                    import_module(f'{app}.{module_name}')
                    sys.stdout.write(
                        f' * registered reference model configs from application \'{app}\'\n')
                except Exception as e:
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        site_reference_configs.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise SiteReferenceConfigImportError(e) from e
            except ImportError:
                pass

    def register_from_visit_schedule(self, site_visit_schedules=None):
        site_visit_schedules.autodiscover(verbose=False)
        for visit_schedule in site_visit_schedules.registry.values():

            reference = self.reference_updater.update(
                model=visit_schedule.visit_model,
                fields=['report_datetime'],
                get_config=self.get_config)
            self._register_if_new(reference)

            for schedule in visit_schedule.schedules.values():
                for visit in schedule.visits.values():
                    for crf in visit.crfs:
                        reference = self.reference_updater.update(
                            model=crf.model,
                            fields=['report_datetime'],
                            get_config=self.get_config)
                        self._register_if_new(reference)
                    for requisition in visit.requisitions:
                        reference = self.reference_updater.update(
                            model=requisition.model,
                            fields=['requisition_datetime', 'panel_name', 'is_drawn',
                                    'reason_not_drawn'],
                            get_config=self.get_config)
                        self._register_if_new(reference)

    def _register_if_new(self, reference):
        try:
            self.register(reference)
        except AlreadyRegistered:
            self.reregister(reference)

    def add_fields_to_config(self, model=None, fields=None):
        reference_config = self.get_config(model)
        reference_config.add_fields(fields)


site_reference_configs = Site()
