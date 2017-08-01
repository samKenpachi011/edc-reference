# needed for site_reference_configs.autodiscover test
from ..reference_model_config import ReferenceModelConfig
from ..site import site_reference_configs

reference = ReferenceModelConfig(
    fields=['f1', 'f2', 'f3', 'f4'], model='edc_reference.erik')

site_reference_configs.register(reference=reference)
