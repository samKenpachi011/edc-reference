
class FieldSet:
    def __init__(self, name=None, refsets=None):
        self.name = name
        self._values = [getattr(t, name) for t in refsets]

    def all(self):
        return self._values

    def filter(self, *values):
        return [v for v in self._values if v or (len(values) > 0 and v in values)]

    def first(self, value=None):
        """Returns the first value from the list of values.
        """
        try:
            return [v for v in self._values[0]
                    if v or (value is not None and v == value)][0]
        except IndexError:
            return None

    def last(self, value=None):
        """Returns the last value from the list of values.
        """
        try:
            return [v for v in self._values[-1:]
                    if v or (value is not None and v == value)][0]
        except IndexError:
            return None
