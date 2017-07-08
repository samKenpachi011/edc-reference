from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, weak=False, dispatch_uid="edc_reference_post_delete")
def edc_reference_post_delete(instance, using, **kwargs):
    try:
        instance.edc_reference_model_deleter_cls(model_obj=instance)
    except AttributeError:
        pass
