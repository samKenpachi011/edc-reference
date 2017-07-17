from django.apps import apps as django_apps


class ReferenceModelValidationError(Exception):
    pass


class ReferenceFieldValidationError(Exception):
    pass


class ReferenceDuplicateField(Exception):
    pass


class ReferenceModelConfig:

    reference_model = 'edc_reference.reference'

    def __init__(self, fields=None, model=None):
        if not fields:
            raise ReferenceFieldValidationError('No fields declared.')
        self.field_names = list(set(fields))
        self.field_names.sort()
        self.model = model.lower()
        if len(fields) != len(self.field_names):
            raise ReferenceDuplicateField(
                f'Duplicate field detected. Got {fields}. See \'{model}\'')

    def add_fields(self, fields=None):
        self.field_names.extend(fields)
        self.field_names = list(set(fields))
        self.field_names.sort()

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
