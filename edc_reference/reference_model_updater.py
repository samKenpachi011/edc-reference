from .reference_model_getter import ReferenceModelGetter
from .site import site_reference_fields


class ReferenceFieldNotFound(Exception):
    pass


class ReferenceModelUpdater:
    """Updates or creates each reference model instance; one for
    each field in `edc_reference_fields` for this model_obj.
    """

    getter_cls = ReferenceModelGetter

    def __init__(self, model_obj=None):
        edc_reference_fields = site_reference_fields.get_fields(
            model=model_obj._meta.label_lower)
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
            reference.object.update_value(value=value, field=field_obj)
            reference.object.save()
