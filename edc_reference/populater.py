import arrow
import sys

from django.apps import apps as django_apps

from .reference import ReferenceUpdater
from .site import site_reference_configs


class PopulaterAttributeError(Exception):
    pass


class Populater:

    def populate(self):
        t = arrow.utcnow().to('Africa/Gaborone').strftime('%H:%M')
        sys.stdout.write(
            f'Populating reference model. Started: {t}\n')
        for model in site_reference_configs.registry:
            index = 0
            sys.stdout.write(f'{model}           \r')
            model_cls = django_apps.get_model(model)
            qs = model_cls.objects.all()
            total = qs.count()
            for index, model_obj in enumerate(qs):
                index += 1
                sys.stdout.write(f'{model} {index} / {total} ...    \r')
                ReferenceUpdater(model_obj=model_obj)
            sys.stdout.write(f'{model} {index} / {total} . OK    \n')
        t = arrow.utcnow().to('Africa/Gaborone').strftime('%H:%M')
        sys.stdout.write(f'Done. Ended: {t}\n')
