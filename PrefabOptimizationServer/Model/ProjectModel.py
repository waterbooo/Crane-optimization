from .AnalyticalModel import *
from .ModelConstants import *

class ProjectModel(object):
    """Data about model"""
    def __init__(self, **kwargs):
        self._rooms = {}
        self._steelAnalyticalModel = AnalyticalModel()
        return super().__init__(**kwargs)

    def AddRoom(self, room):
        """Adds room to model"""
        self._rooms[room.Id] = room

    def GetRoom(self, id):
        """Gets room by id"""
        try:
            return self._rooms[id]
        except:
            return None

    @property
    def SteelAnalyticalModel(self):
        return self._steelAnalyticalModel

    @SteelAnalyticalModel.setter
    def SteelAnalyticalModel(self, value):
        self._steelAnalyticalModel = value

    @SteelAnalyticalModel.deleter
    def SteelAnalyticalModel(self):
        del self._steelAnalyticalModel

    def GetClipsFacts(self, options=None):
        """Forms CLIPS facts for whole model"""
        mc = ModelConstants
        facts = ""
        if options == None or mc.MappingTagRoom in options.Mappings:
            for id,room in self._rooms.items():
                facts += room.GetClipsFacts(options) + "\n"
        facts += self._steelAnalyticalModel.GetClipsFacts(options)
        return facts
