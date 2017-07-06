import os, sys
__filePath = os.path.dirname(os.path.realpath(__file__))

__GeomPath = os.path.join(os.path.split(__filePath)[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from BLGeometry.PrefabGeometry import *
from .BLObject import *
from .ModelConstants import ModelConstants

class BLRoom(BLObject):
    """Room descriptor"""
    def __init__(self, **kwargs):
        self._center = Point()
        return super().__init__(**kwargs)

    @property 
    def Center(self):
        return self._center

    @Center.setter
    def Center(self, value):
        self._center = value

    @Center.deleter
    def Center(self):
        del self._center

    def GetClipsFacts(self, options=None):
        """Forms CLIPS fact for whole object"""
        mc = ModelConstants
        if not options or mc.MappingTagRoom in options.Mappings:
            fact = "(Room "
            fact += self.GetClipsSlots(options)
            fact += ") \n"
            fact += self.Center.GetClipsFacts(options)
        return fact

    def GetClipsSlots(self, options=None):
        """Forms CLIPS slots for whole object"""
        slots = "(Id \"" + self._id + "\") "
        slots += "(CenterId " + str(Point.FreeId) + ") "
        #slots += "(Center " + str(self._center.X) + " " + str(self._center.Y) + ") "
        return slots

    def LoadFromJSON(self, JSON):
        self._id = JSON["Id"]
        self._center = Point(JSON["Center"]["X"], JSON["Center"]["Y"], JSON["Center"]["Z"])
