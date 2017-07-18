from django.apps import apps as django_apps

from ..site import site_reference_configs


class ReferenceTestHelperError(Exception):
    pass


class ReferenceTestHelper:

    def __init__(self, visit_model=None, subject_identifier=None):
        self.subject_identifier = subject_identifier
        self.app_label = visit_model.split('.')[0]
        self.reference_model_cls = django_apps.get_model(
            site_reference_configs.get_reference_model(visit_model))

    def get(self, **kwargs):
        return self.reference_model_cls.objects.get(**kwargs)

    def filter(self, **kwargs):
        return self.reference_model_cls.objects.filter(**kwargs)

    def create_for_model(self, model=None, report_datetime=None, visit_code=None, **options):
        model = f'{self.app_label}.{model}'
        for field_name in site_reference_configs.get_fields(model):
            reference = self.reference_model_cls.objects.create(
                model=model,
                identifier=self.subject_identifier,
                report_datetime=report_datetime,
                timepoint=visit_code,
                field_name=field_name)
            try:
                value, internal_type = options.get(field_name)
            except TypeError:
                pass
            else:
                reference.update_value(
                    value=value, internal_type=internal_type)
        return self.reference_model_cls.objects.filter(
            model=model, identifier=self.subject_identifier,
            report_datetime=report_datetime)

    def update_for_model(self, model=None, report_datetime=None, valueset=None):
        for field_name, internal_type, value in valueset:
            reference = self.reference_model_cls.objects.create(
                model=f'{self.app_label}.{model}',
                identifier=self.subject_identifier,
                report_datetime=report_datetime,
                field_name=field_name)
            reference.update_value(value=value, internal_type=internal_type)

    def create_visit(self, report_datetime=None, timepoint=None):
        reference = self.reference_model_cls.objects.create(
            identifier=self.subject_identifier,
            model='bcpp_subject.subjectvisit',
            report_datetime=report_datetime,
            timepoint=timepoint,
            field_name='report_datetime')
        return reference
