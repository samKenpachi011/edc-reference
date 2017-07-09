# needed for site_reference_fields.autodiscover test
from ..reference_model_config import ReferenceModelConfig
from ..site import site_reference_fields

reference = ReferenceModelConfig(
    fields=['f1', 'f2', 'f3', 'f4'], model='edc_reference.erik')

site_reference_fields.register(reference=reference)
