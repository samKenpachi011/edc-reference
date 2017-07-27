from django.core.management.base import BaseCommand

from edc_reference.populater import Populater


class Command(BaseCommand):

    help = 'Populates the reference model'

    def add_arguments(self, parser):

        parser.add_argument(
            '--models',
            dest='models',
            default=None,
            help=('run for a single model name (label_lower syntax)'),
        )
        parser.add_argument(
            '--exclude_models',
            dest='exclude_models',
            default=None,
            help=('comma separated list of model names to exclude (label_lower syntax)'),
        )

        parser.add_argument(
            '--skip-existing',
            dest='skip_existing',
            default=None,
            help=('skip model if records already exist (Default: False'),
        )

    def handle(self, *args, **options):

        models = options.get('models')
        exclude_models = options.get('exclude_models')
        skip_existing = options.get('skip_existing')
        populater = Populater(
            models=models, exclude_models=exclude_models, skip_existing=skip_existing)
        populater.populate()
