from .fieldset import Fieldset
from .refset import Refset


class LongitudinalRefsetError(Exception):
    pass


class InvalidOrdering(Exception):
    pass


class NoRefsetObjectsExist(Exception):
    pass


class LongitudinalRefset:
    """A collection of a subject's `Refset` objects for a given visit model.
    """

    fieldset_cls = Fieldset
    refset_cls = Refset

    def __init__(self, subject_identifier=None, visit_model=None, model=None,
                 reference_model_cls=None, **options):
        self.ordering = None
        self.subject_identifier = subject_identifier
        self.visit_references = reference_model_cls.objects.filter(
            identifier=self.subject_identifier,
            model=visit_model,
            field_name='report_datetime',
            **options)
        self._refsets = []
        for visit_reference in self.visit_references:
            self._refsets.append(self.refset_cls(
                subject_identifier=subject_identifier,
                report_datetime=visit_reference.report_datetime,
                timepoint=visit_reference.timepoint,
                model=model,
                reference_model_cls=reference_model_cls))
        self.order_by('report_datetime')

    def __repr__(self):
        return f'{self.__class__.__name__}({self._refsets})'

    def __iter__(self):
        return iter(self._refsets)

    def order_by(self, field=None):
        """Re-order the collection ref objects by a single field.
        """
        if field and field.replace('-', '') not in self.refset_cls.ordering_attrs:
            raise InvalidOrdering(
                f'Invalid ordering field. field={field}. Expected one of '
                f'{self.refset_cls.ordering_attrs}')
        field = field or 'report_datetime'
        self.ordering = field
        reverse = False
        if field.startswith('-'):
            field = field[1:]
            reverse = True
        self._refsets.sort(
            key=lambda x: getattr(x, field) or 0, reverse=reverse)
        return self

    def fieldset(self, field_name=None):
        """Returns a FieldSet for this field name.
        """
        if not self._refsets:
            raise NoRefsetObjectsExist(
                f'No Ref objects exist for this subject. '
                f'Got subject_identifier={self.subject_identifier}')
        return self.fieldset_cls(field=field_name, refsets=self._refsets)
