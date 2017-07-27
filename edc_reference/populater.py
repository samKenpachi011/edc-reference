import arrow
import sys

from django.apps import apps as django_apps

from .reference import ReferenceUpdater
from .site import site_reference_configs


class PopulaterAttributeError(Exception):
    pass


class DryRunDummy:
    def __init__(self, **kwargs):
        pass


class Populater:

    reference_updater_cls = ReferenceUpdater

    def __init__(self, models=None, exclude_models=None, skip_existing=None,
                 dry_run=None):
        self.skip_existing = skip_existing
        if not models:
            models = list(site_reference_configs.registry)
        if not exclude_models:
            exclude_models = []
        exclude_models = [m.strip() for m in exclude_models]
        self.models = [m.strip() for m in models if m not in exclude_models]
        self.dry_run = dry_run

    def summarize(self):
        for model in self.models:
            reference_model = site_reference_configs.get_reference_model(
                model=model)
            reference_model_cls = django_apps.get_model(reference_model)
            count = reference_model_cls.objects.filter(model=model).count()
            sys.stdout.write(f' * {model}: {count} records\n')

    def populate(self):
        if self.dry_run:
            self.reference_updater_cls = DryRunDummy
        t_start = arrow.utcnow().to('Africa/Gaborone').strftime('%H:%M')
        sys.stdout.write(
            f'Populating reference model. Started: {t_start}\n')
        sys.stdout.write(
            f' - found {len(site_reference_configs.registry)} models in registry.\n')
        sys.stdout.write(
            f' - running for {len(self.models)} selected models.\n')
        if self.skip_existing:
            sys.stdout.write(f' - skipping models with existing references\n')
        if self.dry_run:
            sys.stdout.write(
                f' - This is a dry run. No data will be created/modified.\n')
        for model in self.models:
            index = 0
            if self.skip(model=model):
                sys.stdout.write(f' * skipping {model}\n')
                continue
            sys.stdout.write(f' * {model}           \r')
            model_cls = django_apps.get_model(model)
            qs = model_cls.objects.all()
            total = qs.count()
            sub_start_time = arrow.utcnow().to('Africa/Gaborone').datetime
            for index, model_obj in enumerate(qs):
                index += 1
                sub_end_time = arrow.utcnow().to('Africa/Gaborone').datetime
                tdelta = sub_end_time - sub_start_time
                sys.stdout.write(
                    f' * {model} {index} / {total} ... {str(tdelta)}    \r')
                self.reference_updater_cls(model_obj=model_obj)
            sub_end_time = arrow.utcnow().to('Africa/Gaborone').datetime
            tdelta = sub_end_time - sub_start_time
            sys.stdout.write(
                f' * {model} {index} / {total} . OK  in {str(tdelta)}      \n')
        t_end = arrow.utcnow().to('Africa/Gaborone').strftime('%H:%M')
        sys.stdout.write(f'Done. Ended: {t_end}\n')

    def skip(self, model=None):
        if self.skip_existing:
            reference_model = site_reference_configs.get_reference_model(
                model=model)
            reference_model_cls = django_apps.get_model(
                reference_model)
            return reference_model_cls.objects.filter(model=model).exists()
        return False
