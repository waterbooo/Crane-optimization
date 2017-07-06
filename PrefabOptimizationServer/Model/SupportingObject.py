from .BLObject import *

class SupportingObject(BLObject):
    """Small objects from steel analytical model like plates, bolts etc."""
    def __init__(self, *args, **kwargs):
        self._type = ""
        self._weight = 0.0
        return super().__init__(*args, **kwargs)

    @property
    def Type(self):
        """Supporting object type string"""
        return self._type

    @Type.setter
    def Type(self, value):
        self._type = value

    @Type.deleter
    def Type(self):
        del self._type

    @property
    def Weight(self):
        """Weight in pounds"""
        return self._weight

    @Weight.setter
    def Weight(self, value):
        self._weight = value

    @Weight.deleter
    def Weight(self):
        del self._weight
