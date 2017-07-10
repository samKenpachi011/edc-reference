from django.test import TestCase, tag
from edc_reference.populater import Populater


@tag('pop')
class TestPopulater(TestCase):

    def test_(self):
        Populater()
