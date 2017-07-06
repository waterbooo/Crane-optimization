from BLGeometry.PrefabGeometry import *

class BLStructuralObject(object):
    """base class for elements with center point"""

    def __init__(self, **kwargs):

        self._centerPoint = Point()
        self._weight = 0.0

        return super().__init__(**kwargs)

    @property
    def CenterPoint(self):
        """Bar mass center point"""
        return self._centerPoint

    @CenterPoint.setter
    def CenterPoint(self, value):
        self._centerPoint = value

    @CenterPoint.deleter
    def CenterPoint(self):
        del self._centerPoint

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