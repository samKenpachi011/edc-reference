import copy
import sys
from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule
from django.core.management.color import color_style

from .reference_model_config import ReferenceDuplicateField, ReferenceModelValidationError
from .reference_model_config import ReferenceFieldValidationError
from .reference_model_config import ReferenceModelConfig
from .reference_model_config import ReferenceFieldAlreadyAdded
from .utils import get_reference_name


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

    def update(self, name=None, fields=None, get_config=None):
        try:
            reference = get_config(name=name)
        except SiteReferenceConfigError:
            reference = ReferenceModelConfig(name=name, fields=fields)
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
        if reference.name in self.registry:
            raise AlreadyRegistered(
                f'Reference fields have already been registered. '
                f'Got {reference.name}')
        self.registry.update({reference.name: reference})
        self.loaded = True

    def reregister(self, reference=None):
        if reference.name not in self.registry:
            raise ReferenceConfigNotRegistered(
                f'Reregister failed. Reference model configuration has not '
                f'been registered. Got {reference.name}')
        self.registry.update({reference.name: reference})

    def unregister(self, name=None):
        if name not in self.registry:
            raise ReferenceConfigNotRegistered(
                f'Unregister failed. Reference model configuration has not '
                f'been registered. Got {name}')
        self.registry = {k: v for k,
                         v in self.registry.items() if k != name}

    def get_config(self, name=None):
        try:
            reference_config = self.registry.get(name)
        except AttributeError:
            reference_config = None
        if not reference_config:
            raise SiteReferenceConfigError(
                f'Model not registered. Got {name}')
        return reference_config

    def get_fields(self, name=None):
        """Returns a list of fields associated with the
        reference configuration of "model".
        """
        return self.get_config(name=name).field_names

    def get_reference_model(self, name=None):
        """Returns the reference model associated with the
        reference configuration of "model".
        """
        return self.get_config(name=name).reference_model

    def validate(self):
        """Validates the reference data for all classes in the
        registry.
        """
        style = color_style()
        sys.stdout.write('Validating site reference models and fields.\n')
        for name, reference in self.registry.items():
            sys.stdout.write(f' (*) {name} ...    \r')
            try:
                reference.validate()
            except (ReferenceDuplicateField, ReferenceModelValidationError,
                    ReferenceFieldValidationError) as e:
                sys.stdout.write(
                    f' ( ) {name}. {style.ERROR("ERROR!!")}    \n')
                raise SiteReferenceConfigError(e) from e
            else:
                sys.stdout.write(
                    f' (*) {name}. {style.SUCCESS("OK")}    \n')
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

    def register_from_visit_schedule(self, site_visit_schedules=None, autodiscover=None):
        autodiscover = True if autodiscover is None else autodiscover
        if autodiscover:
            site_visit_schedules.autodiscover(verbose=False)
        for visit_schedule in site_visit_schedules.registry.values():

            reference = self.reference_updater.update(
                name=visit_schedule.visit_model,
                fields=['report_datetime'],
                get_config=self.get_config)
            self._register_if_new(reference)

            for schedule in visit_schedule.schedules.values():
                for visit in schedule.visits.values():
                    for crf in visit.crfs:
                        reference = self.reference_updater.update(
                            name=crf.model,
                            fields=['report_datetime'],
                            get_config=self.get_config)
                        self._register_if_new(reference)
                    for requisition in visit.requisitions:
                        reference = self.reference_updater.update(
                            name=get_reference_name(
                                requisition.model, requisition.panel.name),
                            fields=['requisition_datetime', 'panel_name', 'is_drawn',
                                    'reason_not_drawn'],
                            get_config=self.get_config)
                        self._register_if_new(reference)

    def _register_if_new(self, reference):
        try:
            self.register(reference)
        except AlreadyRegistered:
            self.reregister(reference)

    def add_fields_to_config(self, name=None, fields=None):
        reference_config = self.get_config(name=name)
        reference_config.add_fields(fields)


site_reference_configs = Site()
