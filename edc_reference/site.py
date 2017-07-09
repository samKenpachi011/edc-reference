import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule
from django.core.management.color import color_style


class AlreadyRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteReferenceFieldsImportError(Exception):
    pass


class SiteReferenceFieldsError(Exception):
    pass


class ReferenceModelValidationError(Exception):
    pass


class ReferenceFieldValidationError(Exception):
    pass


class ReferenceDuplicateField(Exception):
    pass


class ReferenceModelConfig:

    reference_model = 'edc_reference.reference'

    def __init__(self, fields=None, model=None):
        self.field_names = list(set(fields))
        self.field_names.sort()
        self.model = model.lower()
        if len(fields) != len(self.field_names):
            raise ReferenceDuplicateField(
                f'Duplicate field detected. Got {fields}. See \'{model}\'')

    def __repr__(self):
        return f'{self.__class__.__name__}(model={self.model})'

    def validate(self):
        """Validates the model class by doing a django.get_model lookup
        and confirming all fields exist on the model class.
        """
        try:
            model_cls = django_apps.get_model(self.model)
        except LookupError as e:
            raise ReferenceModelValidationError(
                f'Invalid model. Got {self.model}, {e}. See {repr(self)}.')
        model_field_names = [fld.name for fld in model_cls._meta.get_fields()]
        for field_name in self.field_names:
            if field_name not in model_field_names:
                raise ReferenceFieldValidationError(
                    f'Invalid reference field. Got {field_name} not found '
                    f'on model {repr(model_cls)}. See {repr(self)}.')
        try:
            model_cls.edc_reference_model_updater_cls
            model_cls.edc_reference_model_deleter_cls
        except AttributeError:
            raise ReferenceFieldValidationError(
                f'Missing reference model mixin. See model {repr(model_cls)}')


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
