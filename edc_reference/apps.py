from django.apps import AppConfig as DjangoAppConfig

from .site import site_reference_fields


class AppConfig(DjangoAppConfig):
    name = 'edc_reference'

    def ready(self):
        from .signals import edc_reference_post_delete

        site_reference_fields.autodiscover()
