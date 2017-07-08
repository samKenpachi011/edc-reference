from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_reference'

    def ready(self):
        from .signals import edc_reference_post_delete
