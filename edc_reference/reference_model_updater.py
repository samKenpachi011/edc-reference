from .reference_model_getter import ReferenceModelGetter


class ReferenceDuplicateField(Exception):
    pass


class ReferenceFieldNotFound(Exception):
    pass


class ReferenceModelUpdater:
    """Updates or creates each reference model instance; one for
    each field in `edc_reference_fields` for this model_obj.
    """

    getter_cls = ReferenceModelGetter

    def __init__(self, model_obj=None):
        # validate reference fields for duplicates
        edc_reference_fields = list(set(model_obj.edc_reference_fields))
        if len(edc_reference_fields) != len(model_obj.edc_reference_fields):
            raise ReferenceDuplicateField(
                f'Duplicate field detected. Got {model_obj.edc_reference_fields}. '
                f'See model \'{model_obj._meta.verbose_name}\'')
        # loop through fields and update or create each
        # reference model instance
        for field_name in edc_reference_fields:
            try:
                field_obj = [fld for fld in model_obj._meta.get_fields()
                             if fld.name == field_name][0]
            except IndexError:
                raise ReferenceFieldNotFound(
                    f'Reference field not found. Got \'{field_name}\'. '
                    f'See {model_obj._meta.verbose_name}.')
            reference = self.getter_cls(
                model_obj=model_obj,
                field_name=field_name,
                create=True)
            value = getattr(model_obj, field_obj.name)
            reference.object.update_value(
                value=value, field=field_obj, model=model_obj._meta.label_lower)
            reference.object.save()
