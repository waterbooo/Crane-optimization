from .AnalyticalBar import *
from .ModelConstants import ModelConstants

class AnalyticalColumn(AnalyticalBar):
    """Steel analytical column"""

    @property
    def BasePoint(self):
        """Base column point"""
        return self._startPoint

    @BasePoint.setter
    def BasePoint(self, value):
        self._startPoint = value

    @property
    def TopPoint(self):
        """Top column point"""
        return self._endPoint

    @TopPoint.setter
    def TopPoint(self, value):
        self._endPoint = value

    @property
    def BarType(self):
        """Type of Bar"""
        return BarType.Column

    def GetClipsSlots(self, options = None):
        """Forms CLIPS slots for whole object"""
        mc = ModelConstants
        slots = super().GetClipsSlots(options)
        if not options or mc.MappingColumnObject in options.Mappings[mc.MappingTagAnalyticalColumn]:
            slots[mc.MappingColumnObject] = ""
            slots[mc.MappingColumnObject] += " (BasePoint " + str(self._startPoint.X) + " " + str(self._startPoint.Y) + " " + str(self._startPoint.Z) + ") "
            slots[mc.MappingColumnObject] += " (TopPoint " + str(self._endPoint.X) + " " + str(self._endPoint.Y) + " " + str(self._endPoint.Z) + ")"
        return slots

    def GetClipsFacts(self, options = None):
        """Forms CLIPS fact for whole object"""
        mc = ModelConstants
        fact = ""
        if not options or mc.MappingTagAnalyticalColumn in options.Mappings:
            slots = self.GetClipsSlots(options)
            if options and mc.MappingColumnData in options.Mappings[mc.MappingTagAnalyticalColumn]:
                fact += "(ColumnData "
                fact += slots[mc.MappingBarData]
                fact += ")\n"
            if not options or mc.MappingColumnObject in options.Mappings[mc.MappingTagAnalyticalColumn]:
                fact += "(AnalyticalColumn "
                fact += slots[mc.MappingBarObject]
                fact += slots[mc.MappingColumnObject]
                fact += ")"
        return fact
