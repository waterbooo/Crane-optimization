from .BLObject import *
from .ModelConstants import ModelConstants

class AnalyticalBeamColumnConnection(BLObject):
    """Beam to Column connection from steel analytical model"""
    def __init__(self, **kwargs):
        self._Type = ""
        self._BeamId = ""
        self._ColumnId = ""
        self._MaxBeamSize = 0.0
        self._MinBeamSize = 0.0
        self._MaxBeamLinearWeight = 0.0
        self._MaxBeamFlangeThickness = 0.0
        self._MinBeamFlangeThickness = 0.0
        self._MinClearSpanDepthRatio = 0.0
        self._MaxColumnDepth = 0.0
        self._WebToThicknessRatioOkBeam = "TRUE"
        self._WebToThicknessRatioOkColumn = "TRUE"
        self._MaterialCost = 0.0
        self._FabricationCost = 0.0
        self._ErectionCost = 0.0
        return super().__init__(**kwargs)

    @property
    def Type(self):
        """Type of connection e.g. WUFW"""
        return self._Type

    @Type.setter
    def Type(self, value):
        self._Type = value

    @Type.deleter
    def Type(self):
        del self._Type

    @property
    def BeamId(self):
        """Beam id in connection"""
        return self._BeamId

    @BeamId.setter
    def BeamId(self, value):
        self._BeamId = value

    @BeamId.deleter
    def BeamId(self):
        del self._BeamId

    @property
    def ColumnId(self):
        """Column id in connection"""
        return self._ColumnId

    @ColumnId.setter
    def ColumnId(self, value):
        self._ColumnId = value

    @ColumnId.deleter
    def ColumnId(self):
        del self._ColumnId

    @property
    def MaxBeamSize(self):
        """Max allowed beam depth for connection"""
        return self._MaxBeamSize

    @MaxBeamSize.setter
    def MaxBeamSize(self, value):
        self._MaxBeamSize = value

    @MaxBeamSize.deleter
    def MaxBeamSize(self):
        del self._MaxBeamSize

    @property
    def MinBeamSize(self):
        """Minimum beam depth suitable for connection"""
        return self._MinBeamSize

    @MinBeamSize.setter
    def MinBeamSize(self, value):
        self._MinBeamSize = value

    @MinBeamSize.deleter
    def MinBeamSize(self):
        del self._MinBeamSize

    @property
    def MaxBeamLinearWeight(self):
        """Maximum beam weight applicable for connection"""
        return self._MaxBeamLinearWeight

    @MaxBeamLinearWeight.setter
    def MaxBeamLinearWeight(self, value):
        self._MaxBeamLinearWeight = value

    @MaxBeamLinearWeight.deleter
    def MaxBeamLinearWeight(self):
        del self._MaxBeamLinearWeight

    @property
    def MaxBeamFlangeThickness(self):
        """Maximum beam flange thickness applicable for connection"""
        return self._MaxBeamFlangeThickness

    @MaxBeamFlangeThickness.setter
    def MaxBeamFlangeThickness(self, value):
        self._MaxBeamFlangeThickness = value

    @MaxBeamFlangeThickness.deleter
    def MaxBeamFlangeThickness(self):
        del self._MaxBeamFlangeThickness

    @property
    def MinBeamFlangeThickness(self):
        """Minimum beam flange thickness applicable for connection"""
        return self._MinBeamFlangeThickness

    @MinBeamFlangeThickness.setter
    def MinBeamFlangeThickness(self, value):
        self._MinBeamFlangeThickness = value

    @MinBeamFlangeThickness.deleter
    def MinBeamFlangeThickness(self):
        del self._MinBeamFlangeThickness

    @property
    def MinClearSpanDepthRatio(self):
        """Minimum clear span depth applicable for connection"""
        return self._MinClearSpanDepthRatio

    @MinClearSpanDepthRatio.setter
    def MinClearSpanDepthRatio(self, value):
        self._MinClearSpanDepthRatio = value

    @MinClearSpanDepthRatio.deleter
    def MinClearSpanDepthRatio(self):
        del self._MinClearSpanDepthRatio

    @property
    def MaxColumnDepth(self):
        """Max allowed column depth for connection"""
        return self._MaxColumnDepth

    @MaxColumnDepth.setter
    def MaxColumnDepth(self, value):
        self._MaxColumnDepth = value

    @MaxColumnDepth.deleter
    def MaxColumnDepth(self):
        del self._MaxColumnDepth

    @property
    def WebToThicknessRatioOkBeam(self):
        """Indicates if web thickness to beam width ratio is applicable"""
        return self._WebToThicknessRatioOkBeam

    @WebToThicknessRatioOkBeam.setter
    def WebToThicknessRatioOkBeam(self, value):
        self._WebToThicknessRatioOkBeam = value

    @WebToThicknessRatioOkBeam.deleter
    def WebToThicknessRatioOkBeam(self):
        del self._WebToThicknessRatioOkBeam

    @property
    def WebToThicknessRatioOkColumn(self):
        """Indicates if web thickness to column width ratio is applicable"""
        return self._WebToThicknessRatioOkColumn

    @WebToThicknessRatioOkColumn.setter
    def WebToThicknessRatioOkColumn(self, value):
        self._WebToThicknessRatioOkColumn = value

    @WebToThicknessRatioOkColumn.deleter
    def WebToThicknessRatioOkColumn(self):
        del self._WebToThicknessRatioOkColumn

    @property
    def MaterialCost(self):
        """Cost of material for connection"""
        return self._MaterialCost

    @MaterialCost.setter
    def MaterialCost(self, value):
        self._MaterialCost = value

    @MaterialCost.deleter
    def MaterialCost(self):
        del self._MaterialCost

    @property
    def FabricationCost(self):
        """Cost of fabrication for connection"""
        return self._FabricationCost

    @FabricationCost.setter
    def FabricationCost(self, value):
        self._FabricationCost = value

    @FabricationCost.deleter
    def FabricationCost(self):
        del self._FabricationCost

    @property
    def ErectionCost(self):
        """Cost of Erection for connection"""
        return self._ErectionCost

    @ErectionCost.setter
    def ErectionCost(self, value):
        self._ErectionCost = value

    @ErectionCost.deleter
    def ErectionCost(self):
        del self._ErectionCost

    def GetClipsSlots(self, options = None):
        """Forms CLIPS slots for object"""
        slots = "(Id " + str(self._id) + ") "
        slots += "(Type " + str(self._Type) + ") "
        slots += "(BeamId " + str(self._BeamId) + ") "
        slots += "(ColumnId " + str(self._ColumnId) + ") "
        slots += "(MaxBeamSize " + str(self._MaxBeamSize) + ") "
        slots += "(MinBeamSize " + str(self._MinBeamSize) + ") "
        slots += "(MaxBeamLinearWeight " + str(self._MaxBeamLinearWeight) + ") "
        slots += "(MaxBeamFlangeThickness " + str(self._MaxBeamFlangeThickness) + ") "
        slots += "(MinBeamFlangeThickness " + str(self._MinBeamFlangeThickness) + ") "
        slots += "(MinClearSpanDepthRatio " + str(self._MinClearSpanDepthRatio) + ") "
        slots += "(MaxColumnDepth " + str(self._MaxColumnDepth) + ") "
        slots += "(WebToThicknessRatioOkBeam " + str(self._WebToThicknessRatioOkBeam) + ") "
        slots += "(WebToThicknessRatioOkColumn " + str(self._WebToThicknessRatioOkColumn) + ") "
        slots += "(MaterialCost " + str(self._MaterialCost) + ") "
        slots += "(FabricationCost " + str(self._FabricationCost) + ") "
        slots += "(ErectionCost " + str(self._ErectionCost) + ") "

        return slots

    def GetClipsFacts(self, options = None):
        """Forms CLIPS fact for whole object"""
        mc = ModelConstants
        fact = ""
        if not options or mc.MappingTagAnalyticalBeamToColumnConnection in options.Mappings:
            fact = "(AnalyticalConnectionData "
            fact += self.GetClipsSlots(options)
            fact += ")"
        return fact
