from .AnalyticalBar import *
from .ModelConstants import ModelConstants

class AnalyticalBeam(AnalyticalBar):
    """Steel analytical beam data"""
    def __init__(self, **kwargs):
        self._cutLength = 0.0
        return super().__init__(**kwargs)

    @property
    def CutLength(self):
        """Cut length"""
        return self._cutLength

    @CutLength.setter
    def CutLength(self, value):
        self._cutLength = value

    @CutLength.deleter
    def CutLength(self):
        del self._cutLength

    @property
    def BarType(self):
        """Type of Bar"""
        return BarType.Beam

    def GetClipsSlots(self, options = None):
        mc = ModelConstants
        slots = super().GetClipsSlots(options)
        if options and mc.MappingTagAnalyticalBeam in options.Mappings and mc.MappingBeamData in options.Mappings[mc.MappingTagAnalyticalBeam]:
            slots[mc.MappingBeamData] = "(CutLength " + str(self.CutLength) + ") "
        return slots

    def GetClipsFacts(self, options = None):
        """Forms CLIPS fact for whole object"""
        mc = ModelConstants
        fact = ""
        if not options or mc.MappingTagAnalyticalBeam in options.Mappings:
            slots = self.GetClipsSlots(options)
            if options and mc.MappingBeamData in options.Mappings[mc.MappingTagAnalyticalBeam]:
                fact += "(BeamData "
                fact += slots[mc.MappingBarData]
                fact += slots[mc.MappingBeamData]
                fact += ")\n"
            if not options or mc.MappingBeamObject in options.Mappings[mc.MappingTagAnalyticalBeam]:
                fact += "(AnalyticalBeam "
                fact += slots[mc.MappingBarObject]
                fact += ")"
        return fact


