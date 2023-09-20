# from django.test import TestCase, tag
#
# from edc_base.utils import get_utcnow
# from edc_sync.models import OutgoingTransaction
#
# from .models import SubjectVisit
#
# from ..reference_model_config import ReferenceModelConfig
# from ..site import site_reference_configs
# from .models import TestModel
#
#
# class TestSyncModels(TestCase):
#
#     def setUp(self):
#         site_reference_configs.registry = {}
#         self.subject_identifier = '1'
#         subjectvisit_reference = ReferenceModelConfig(
#             name='edc_reference.subjectvisit',
#             fields=['report_datetime', 'visit_code'])
#         self.testmodel_reference = ReferenceModelConfig(
#             name='edc_reference.testmodel', fields=['field_str', 'report_datetime'])
#         self.crfone_reference = ReferenceModelConfig(
#             name='edc_reference.crfone',
#             fields=['field_str', 'field_date',
#                       'field_datetime', 'field_int', 'report_datetime'])
#         site_reference_configs.register(subjectvisit_reference)
#         site_reference_configs.register(self.testmodel_reference)
#         site_reference_configs.register(self.crfone_reference)
#         self.subject_visit = SubjectVisit.objects.create(
#             subject_identifier=self.subject_identifier,
#             visit_code='code')
#
#     def test_reference_synchronizes(self):
#         self.assertEqual(OutgoingTransaction.objects.filter(
#             tx_name='edc_reference.reference').count(), 6)
#         TestModel.objects.create(
#             subject_visit=self.subject_visit,
#             field_str='erik')
#         self.assertEqual(OutgoingTransaction.objects.filter(
#             tx_name='edc_reference.reference').count(), 12)
