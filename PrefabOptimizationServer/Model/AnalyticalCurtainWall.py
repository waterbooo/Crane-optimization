from .AnalyticalModel import *
from .BLObject import *
from .ModelConstants import *
from BLGeometry.PrefabGeometry import *

class AnalyticalCurtainWall(BLObject):
    """Curtain wall properties"""

    def __init__(self, **kwargs):
        self._startPoint = Point()
        self._endPoint = Point()
        self._height = 0.0
        self._mullions = {}
        self._panels = {}
        return super().__init__(**kwargs)

    @property
    def StartPoint(self):
        """Wall start point"""
        return self._startPoint

    @StartPoint.setter
    def StartPoint(self, value):
        self._startPoint = value

    @StartPoint.deleter
    def StartPoint(self):
        del self._startPoint

    @property
    def EndPoint(self):
        """Wall end point"""
        return self._endPoint

    @EndPoint.setter
    def EndPoint(self, value):
        self._endPoint = value

    @EndPoint.deleter
    def EndPoint(self):
        del self._endPoint

    @property
    def Height(self):
        """Length of bar in feet"""
        return self._height

    @Height.setter
    def Height(self, value):
        self._height = value

    @Height.deleter
    def Height(self):
        del self._height

    def AddMullion(self, mullion):
        """Adds a mullion to the model"""
        self._mullions[mullion.Id] = mullion

    def GetMullion(self, id):
        """Gets bar by id"""
        try:
            return self._mullions[id]
        except:
            return None

    def AddPanel(self, panel):
        """Adds a panel to the model"""
        self._panels[panel.Id] = panel

    def GetPanel(self, id):
        """Gets panel by id"""
        try:
            return self._panels[id]
        except:
            return None

    def GetPanels(self):
        """Gets all panels"""
        return self._panels