from .reference_model_config import ReferenceModelConfig
from .site import site_reference_fields, AlreadyRegistered


def register_from_visit_schedule(site_visit_schedules=None):
    for visit_schedule in site_visit_schedules.registry.values():
        for schedule in visit_schedule.schedules.values():
            for visit in schedule.visits.values():
                for crf in visit.crfs:
                    reference = ReferenceModelConfig(
                        model=crf.model,
                        fields=['report_datetime'])
                    try:
                        site_reference_fields.register(reference)
                    except AlreadyRegistered:
                        pass
                for requisition in visit.requisitions:
                    reference = ReferenceModelConfig(
                        model=requisition.model,
                        fields=['panel_name'])
                    try:
                        site_reference_fields.register(reference)
                    except AlreadyRegistered:
                        pass
