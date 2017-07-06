import os, sys
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(os.path.split(__filePath)[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from BLGeometry.PrefabGeometry import *
from BLGeometry.BoundingStructures import BoundingBox
from .BLObject import *
from .ModelConstants import ModelConstants
from .BLStructuralObject import *
from .SteelMaterial import *
from enum import Enum


class BarType(Enum):
    Bar = 0
    Beam = 1
    Column = 2

class AnalyticalBar(BLObject, BLStructuralObject):
    """General steel analytical bar properties"""

    def __init__(self, **kwargs):
        self._length = 0

        self._startPoint = Point()
        self._endPoint = Point()

        self._weightPerLf = 0.0

        self._materialName = ""
        self._sectionName = ""

        self._slendernessClassification = 0

        self._memberProductionProcedure = ""
        self._rolledShapes = ""
        self._weightPerLf = 0.0
        self._topFlangeThickness = 0.0
        
        self._depth = 0.0

        self._CostWF = 0.0
        self._OverallCost = 0.0
        self._MaterialCostPerTon = 0.0
        self._SectionMaterialCost = 0.0
        self._SectionFabricationCost = 0.0
        self._SectionErectionCost = 0.0
        self._SectionCost = 0.0
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
    def MaterialName(self):
        """Steel material name"""
        return self._materialName

    @MaterialName.setter
    def MaterialName(self, value):
        self._materialName = value

    @MaterialName.deleter
    def MaterialName(self):
        del self._materialName

    @property
    def SectionName(self):
        """Steel section name"""
        return self._sectionName

    @SectionName.setter
    def SectionName(self, value):
        self._sectionName = value

    @SectionName.deleter
    def SectionName(self):
        del self._sectionName

    @property
    def BarType(self):
        """Type of Bar"""
        return BarType.Bar

    #============== Analytical model props ====================
    
    @property
    def MemberProductionProcedure(self):
        """Member production procedure"""
        return self._memberProductionProcedure

    @MemberProductionProcedure.setter
    def MemberProductionProcedure(self, value):
        self._memberProductionProcedure = value

    @MemberProductionProcedure.deleter
    def MemberProductionProcedure(self):
        del self._memberProductionProcedure

    @property
    def RolledShapes(self):
        """Rolled shapes"""
        return self._rolledShapes

    @RolledShapes.setter
    def RolledShapes(self, value):
        self._rolledShapes = value

    @RolledShapes.deleter
    def RolledShapes(self):
        del self._rolledShapes

    @property
    def WeightPerLf(self):
        """Weight per length foot"""
        return self._weightPerLf

    @WeightPerLf.setter
    def WeightPerLf(self, value):
        self._weightPerLf = value

    @WeightPerLf.deleter
    def WeightPerLf(self):
        del self._weightPerLf

    @property
    def TopFlangeThickness(self):
        """Top flange thickness"""
        return self._topFlangeThickness

    @TopFlangeThickness.setter
    def TopFlangeThickness(self, value):
        self._topFlangeThickness = value

    @TopFlangeThickness.deleter
    def TopFlangeThickness(self):
        del self._topFlangeThickness

    @property
    def Depth(self):
        """Bar depth"""
        return self._depth

    @Depth.setter
    def Depth(self, value):
        self._depth = value

    @Depth.deleter
    def Depth(self):
        del self._depth

    # ----------------Cost properties------------------
    @property
    def CostWF(self):
        """Cost of wide flange"""
        return self._CostWF

    @CostWF.setter
    def CostWF(self, value):
        self._CostWF = value

    @CostWF.deleter
    def CostWF(self):
        del self._CostWF

    @property
    def OverallCost(self):
        """Cost of wide flange and connections"""
        return self._OverallCost

    @OverallCost.setter
    def OverallCost(self, value):
        self._OverallCost = value

    @OverallCost.deleter
    def OverallCost(self):
        del self._OverallCost

    @property
    def MaterialCostPerTon(self):
        """Cost of material per ton"""
        return self._MaterialCostPerTon

    @MaterialCostPerTon.setter
    def MaterialCostPerTon(self, value):
        self._MaterialCostPerTon = value

    @MaterialCostPerTon.deleter
    def MaterialCostPerTon(self):
        del self._MaterialCostPerTon

    @property
    def SectionMaterialCost(self):
        """Cost of material for section"""
        return self._SectionMaterialCost

    @SectionMaterialCost.setter
    def SectionMaterialCost(self, value):
        self._SectionMaterialCost = value

    @SectionMaterialCost.deleter
    def SectionMaterialCost(self):
        del self._SectionMaterialCost

    @property
    def SectionFabricationCost(self):
        """Cost of section fabrication"""
        return self._SectionFabricationCost

    @SectionFabricationCost.setter
    def SectionFabricationCost(self, value):
        self._SectionFabricationCost = value

    @SectionFabricationCost.deleter
    def SectionFabricationCost(self):
        del self._SectionFabricationCost

    @property
    def SectionErectionCost(self):
        """Cost of section erection"""
        return self._SectionErectionCost

    @SectionErectionCost.setter
    def SectionErectionCost(self, value):
        self._SectionErectionCost = value

    @SectionErectionCost.deleter
    def SectionErectionCost(self):
        del self._SectionErectionCost

    @property
    def SectionCost(self):
        """Total section cost"""
        return self._SectionCost

    @SectionCost.setter
    def SectionCost(self, value):
        self._SectionCost = value

    @SectionCost.deleter
    def SectionCost(self):
        del self._SectionCost

    def GetClipsFacts(self, options=None):
        """Forms CLIPS fact for whole object"""
        mc = ModelConstants
        if not options or mc.MappingTagAnalyticalColumn in options.Mappings or mc.MappingTagAnalyticalBeam in options.Mappings or mc.MappingTagAnalyticalBar in options.Mappings:
            slots = self.GetClipsSlots(options)
            if not options or (mc.MappingTagAnalyticalBar in options.Mappings and mc.MappingBarObject in options.Mappings[mc.MappingTagAnalyticalBar]):
                fact = "(AnalyticalBar "
                fact += slots[mc.MappingBarObject]
                fact += ")"
        return fact

    def GetClipsSlots(self, options=None):
        """Forms CLIPS slots for whole object"""
        mc = ModelConstants
        slots = {}
        commonSlots = "(Id " + self._id + ") "
        commonSlots += "(WeightPerLf " + str(self._weightPerLf) + ") "
        commonSlots += "(Length " + str(self._length) + ") "
        commonSlots += "(CostWF " + str(self._CostWF) + ") "
        commonSlots += "(OverallCost " + str(self._OverallCost) + ") "
        commonSlots += "(MaterialCostPerTon " + str(self._MaterialCostPerTon) + ") "
        commonSlots += "(SectionMaterialCost " + str(self._SectionMaterialCost) + ") "
        commonSlots += "(SectionFabricationCost " + str(self._SectionFabricationCost) + ") "
        commonSlots += "(SectionErectionCost " + str(self._SectionErectionCost) + ") "
        commonSlots += "(SectionCost " + str(self._SectionCost) + ") "

        if not options or (mc.MappingTagAnalyticalColumn in options.Mappings and mc.MappingBarObject in options.Mappings[mc.MappingTagAnalyticalColumn]) or (mc.MappingTagAnalyticalBeam in options.Mappings and mc.MappingBarObject in options.Mappings[mc.MappingTagAnalyticalBeam]) or (mc.MappingTagAnalyticalBar in options.Mappings and mc.MappingBarObject in options.Mappings[mc.MappingTagAnalyticalBar]):
            slots[mc.MappingBarObject] = ""
            slots[mc.MappingBarObject] += commonSlots
            slots[mc.MappingBarObject] += "(StartPoint " + str(self._startPoint.X) + " " + str(self._startPoint.Y) + " " + str(self._startPoint.Z) + ") "
            slots[mc.MappingBarObject] += "(CenterPoint " + str(self._centerPoint.X) + " " + str(self._centerPoint.Y) + " " + str(self._centerPoint.Z) + ") "
            slots[mc.MappingBarObject] += "(EndPoint " + str(self._endPoint.X) + " " + str(self._endPoint.Y) + " " + str(self._endPoint.Z) + ") "
        
            slots[mc.MappingBarObject] += "(Weight " + str(self._weight) + ") "
        
            slots[mc.MappingBarObject] += "(MaterialName \"" + self._materialName + "\") "
            slots[mc.MappingBarObject] += "(SectionName \"" + self._sectionName + "\") "

            slots[mc.MappingBarObject] += "(SlendernessClassification " + str(self._slendernessClassification) + ") "
        if options and ((mc.MappingTagAnalyticalColumn in options.Mappings and mc.MappingBarData in options.Mappings[mc.MappingTagAnalyticalColumn]) or (mc.MappingTagAnalyticalBeam in options.Mappings and mc.MappingBarData in options.Mappings[mc.MappingTagAnalyticalBeam]) or (mc.MappingTagAnalyticalBar in options.Mappings and mc.MappingBarData in options.Mappings[mc.MappingTagAnalyticalBar])):
            slots[mc.MappingBarData] = ""
            slots[mc.MappingBarData] += commonSlots
            slots[mc.MappingBarData] += "(MemberProductionProcedure " + str(self._memberProductionProcedure) + ") "
            slots[mc.MappingBarData] += "(RolledShapes " + str(self._rolledShapes) + ") "
            slots[mc.MappingBarData] += "(TopFlangeThickness " + str(self._topFlangeThickness) + ") "
            slots[mc.MappingBarData] += "(Depth " + str(self._depth) + ") "

        return slots

    def getBBforZCheck(self, delta=1.5):
        bb = BoundingBox()
        bb.minPoint.X = min(self.StartPoint.X, self.EndPoint.X) - delta
        bb.maxPoint.X = max(self.StartPoint.X, self.EndPoint.X) + delta
        bb.minPoint.Y = min(self.StartPoint.Y, self.EndPoint.Y) - delta
        bb.maxPoint.Y = max(self.StartPoint.Y, self.EndPoint.Y) + delta
        bb.minPoint.Z = min(self.StartPoint.Z, self.EndPoint.Z) - delta
        bb.maxPoint.Z = max(self.StartPoint.Z, self.EndPoint.Z) + delta
        return bb