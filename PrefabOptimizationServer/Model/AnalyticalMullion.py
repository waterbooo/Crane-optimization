from .AnalyticalModel import *
from .ModelConstants import *
from .BLObject import *
from BLGeometry.PrefabGeometry import *

class AnalyticalMullion(BLObject):
    """Mullion properties"""

    def __init__(self, **kwargs):
        self._startPoint = Point()
        self._endPoint = Point()
        self._width = 0.0
        self._thickness = 0.0
        return super().__init__(**kwargs)

    @property
    def Id(self):
        """Wall identifier in model"""
        return self._id

    @Id.setter
    def Id(self, value):
        self._id = value

    @Id.deleter
    def Id(self):
        del self._id

    @property
    def StartPoint(self):
        """Mullion start point"""
        return self._startPoint

    @StartPoint.setter
    def StartPoint(self, value):
        self._startPoint = value

    @StartPoint.deleter
    def StartPoint(self):
        del self._startPoint

    @property
    def EndPoint(self):
        """Mullion end point"""
        return self._endPoint

    @EndPoint.setter
    def EndPoint(self, value):
        self._endPoint = value

    @EndPoint.deleter
    def EndPoint(self):
        del self._endPoint

    @property
    def Width(self):
        """Width of mullion"""
        return self._width

    @Width.setter
    def Width(self, value):
        self._width = value

    @Width.deleter
    def Width(self):
        del self._width

    @property
    def Thickness(self):
        """Thickness of mullion"""
        return self._thickness

    @Thickness.setter
    def Thickness(self, value):
        self._thickness = value

    @Thickness.deleter
    def Thickness(self):
        del self._thickness