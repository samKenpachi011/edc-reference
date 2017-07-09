import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule
from django.core.management.color import color_style

from .reference_model_config import ReferenceDuplicateField, ReferenceModelValidationError
from .reference_model_config import ReferenceFieldValidationError


class AlreadyRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteReferenceFieldsImportError(Exception):
    pass


class SiteReferenceFieldsError(Exception):
    pass


class Site:

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, reference=None):
        if reference.model in self.registry:
            raise AlreadyRegistered(
                f'Reference fields have already been registered. '
                f'Got {reference.model}')
        self.registry.update({reference.model: reference})
        self.loaded = True

    def get_fields(self, model=None):
        try:
            return self.registry.get(model).field_names
        except AttributeError:
            raise SiteReferenceFieldsError(
                f'Model not registered. Got {model}')

    def get_reference_model(self, model=None):
        try:
            return self.registry.get(model).reference_model
        except AttributeError:
            raise SiteReferenceFieldsError(
                f'Model not registered. Got {model}')

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
                raise SiteReferenceFieldsError(e) from e
            else:
                sys.stdout.write(f' (*) {model}. {style.SUCCESS("OK")}    \n')
        sys.stdout.write('Done.\n')

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the reference_fields.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or 'reference_fields'
        sys.stdout.write(f' * checking for {module_name} ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_reference_fields.registry)
                    import_module(f'{app}.{module_name}')
                    sys.stdout.write(
                        f' * registered reference fields from application \'{app}\'\n')
                except Exception as e:
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        site_reference_fields.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise SiteReferenceFieldsImportError(e) from e
            except ImportError:
                pass


site_reference_fields = Site()
