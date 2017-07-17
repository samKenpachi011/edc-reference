import sys

from django.apps import AppConfig as DjangoAppConfig

from .site import site_reference_fields


class AppConfig(DjangoAppConfig):
    name = 'edc_reference'
    verbose_name = 'Edc Reference'

    def ready(self):
        from .signals import edc_reference_post_delete
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')

        site_reference_fields.autodiscover()

        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
