from .field_set import FieldSet
from .ref_set import RefSet


class NoRefObjectsExist(Exception):
    pass


class LongitudinalRefSet:
    """A collection of a subject's `Ref` objects for a given visit model.
    """

    def __init__(self, subject_identifier=None, visit_model=None, model=None,
                 reference_model_cls=None, **options):
        self.subject_identifier = subject_identifier
        self.ordering = 'report_datetime'
        self.visit_references = reference_model_cls.objects.filter(
            identifier=self.subject_identifier,
            model=visit_model,
            field_name='report_datetime',
            **options).order_by('report_datetime')
        self._refsets = []
        for visit_reference in self.visit_references:
            self._refsets.append(RefSet(
                subject_identifier=subject_identifier,
                report_datetime=visit_reference.report_datetime,
                timepoint=visit_reference.timepoint,
                model=model,
                reference_model_cls=reference_model_cls))

    def __repr__(self):
        return f'{self.__class__.__name__}({self._refsets})'

    def __iter__(self):
        return iter(self._refsets)

    def order_by(self, field_name=None):
        """Re-order the collection ref objects by a single field.
        """
        field_name = field_name or 'report_datetime'
        self.ordering = field_name
        reverse = False
        if field_name.startswith('-'):
            field_name = field_name[1:]
            reverse = True
        self._refsets.sort(
            key=lambda x: getattr(x, field_name) or 0, reverse=reverse)
        self._reorder_sets()
        return self

    def _reorder_sets(self):
        """Reorders all sets according the the currrent order of the
        ref objects.
        """
        for attr in self.__dict__:
            if isinstance(getattr(self, attr), FieldSet):
                setattr(self, attr, FieldSet(name=attr, refsets=self._refsets))

    def get_fieldset(self, field_name=None):
        """Sets attr `{field_name}_set` with the value of field_name
        for each ref object (maintaining the current order).
        """
        if not self._refsets:
            raise NoRefObjectsExist(
                f'No Ref objects exist for this subject. '
                f'Got subject_identifier={self.subject_identifier}')
        setattr(self, field_name, FieldSet(
            name=field_name, refsets=self._refsets))
        self._cache = lambda x: getattr(x, field_name)
        return self
