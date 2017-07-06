from .AnalyticalModel import *
from .BLObject import *
from .ModelConstants import *
from .BLStructuralObject import *

from BLGeometry.BoundingStructures import BoundingBox

class AnalyticalPanel(BLObject, BLStructuralObject):
    """Panel properties"""

    def __init__(self, **kwargs):
        self._length = 0
        self._startPoint = Point()
        self._endPoint = Point()

        self._thickness = 0.0
        self._corners = []
        return super().__init__(**kwargs)

    @property
    def Length(self):
        """Length of bar in feet"""
        return self._length

    @Length.setter
    def Length(self, value):
        self._length = value

    @Length.deleter
    def Length(self):
        del self._length

    @property
    def StartPoint(self):
        """Bar start end point"""
        return self._startPoint

    @StartPoint.setter
    def StartPoint(self, value):
        self._startPoint = value

    @StartPoint.deleter
    def StartPoint(self):
        del self._startPoint

    @property
    def EndPoint(self):
        """Bar end end point"""
        return self._endPoint

    @EndPoint.setter
    def EndPoint(self, value):
        self._endPoint = value

    @EndPoint.deleter
    def EndPoint(self):
        del self._endPoint

    @property
    def Thickness(self):
        """Thickness of Panel"""
        return self._thickness

    @Thickness.setter
    def Thickness(self, value):
        self._thickness = value

    @Thickness.deleter
    def Thickness(self):
        del self._thickness

    def AddCorner(self, corner):
        """Adds a corner to the model"""
        self._corners.append(corner)

    def GetCorners(self):
        """Gets all corners"""
        return self._corners

    def getBBforZCheck(self, delta=1.5):
        bb = BoundingBox()

        bb.minPoint.X = min([c.X for c in self._corners]) - delta
        bb.maxPoint.X = max([c.X for c in self._corners]) + delta
        bb.minPoint.Y = min([c.Y for c in self._corners]) - delta
        bb.maxPoint.Y = max([c.Y for c in self._corners]) + delta
        bb.minPoint.Z = min([c.Z for c in self._corners]) - delta
        bb.maxPoint.Z = max([c.Z for c in self._corners]) + delta
        return bb