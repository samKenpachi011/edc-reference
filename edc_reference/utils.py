from django.utils.text import slugify


def get_reference_name(model, panel_name):
    model = model.lower()
    panel_name = panel_name.lower()
    return f'{model}.{slugify(panel_name)}'
