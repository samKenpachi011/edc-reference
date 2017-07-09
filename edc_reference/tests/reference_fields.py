# needed for site_reference_fields.autodiscover test
from edc_reference.site import site_reference_fields, ReferenceModelConfig

reference = ReferenceModelConfig(
    fields=['f1', 'f2', 'f3', 'f4'], model='edc_reference.erik')

site_reference_fields.register(reference=reference)
