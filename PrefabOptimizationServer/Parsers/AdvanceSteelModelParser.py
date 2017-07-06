import os, sys, json
__filePath = os.path.dirname(os.path.abspath(__file__))

__AMPath = os.path.join(os.path.split(__filePath)[0], "Model")
if not __AMPath in sys.path:
    sys.path.insert(1, __AMPath)

__OptPath = os.path.join(os.path.split(__filePath)[0], "Optimization")
if not __OptPath in sys.path:
    sys.path.insert(1, __OptPath)

__GeomPath = os.path.join(os.path.split(os.path.split(__filePath)[0])[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from EndpointConstants import EndpointConstants as ec
from Model import *
from BLGeometry.PrefabGeometry import Point
from Parsers.UtilsModelParse import *


class AdvanceSteelModelParser(object):
    """Conversion of AdvanseSteel analytical model JSON into common structures"""

    __ObjTypeBar = "Bar"
    __TagObjectType = "ObjectType"
    
    __TagRooms = "Rooms"
    __TagAnalyticalModel = "AnalyticalModel"
    __TagColumns = "Columns"
    __TagBeams = "Beams"
    __TagProjectInfo = "ProjectInfo"
    __TagStructuralMembers = "StructuralMembers"
    __TagLoads = "Loads"
    __TagBeamColumnConnections = "BeamColumnConnections"
    __TagId = "Id"
    __TagType = "Type"
    __TagBeamId = "BeamId"
    __TagColumnId = "ColumnId"
    __TagBarType = "BarType"
    __TagMaxBeamSize = "MaxBeamSize"
    __TagMinBeamSize = "MinBeamSize"
    __TagMaxBeamLinearWeight = "MaxBeamLinearWeight"
    __TagMaxBeamFlangeThickness = "MaxBeamFlangeThickness"
    __TagMinBeamFlangeThickness = "MinBeamFlangeThickness"
    __TagMinClearSpanDepthRatio = "MinClearSpanDepthRatio"
    __TagMaxColumnDepth = "MaxColumnDepth"
    __TagWebToThicknessRatioOkBeam = "WebToThicknessRatioOkBeam"
    __TagWebToThicknessRatioOkColumn = "WebToThicknessRatioOkColumn"
    __TagAnnotations = "Annotations"
    __TagMemberProductionProcedure = "MemberProductionProcedure"
    __TagRolledShapes = "RolledShapes"
    __TagWeightPerLf = "WeightPerLF"
    __TagWeightPerFt = "WeightPerFt"
    __TagWeight = "Weight"
    __TagTopFlangeThickness = "TopFlangeThickness"
    __TagCutLength = "CutLength"
    __TagDepth = "Depth"

    __TagBottomFlangeThickness = "BottomFlangeThickness"
    __TagCrossSectionalArea = "CrossSectionalArea"
    __TagMomentOfInertiaX = "MomentOfInertiaX"
    __TagMomentOfInertiaY = "MomentOfInertiaY"
    __TagPlasticSectionModulus = "PlasticSectionModulus"
    __TagRadiusOfGyrationX = "RadiusOfGyrationX"
    __TagRadiusOfGyrationY = "RadiusOfGyrationY"
    __TagSection = "Section"
    __TagWebThickness = "WebThickness"
    __TagWidth = "Width"
    __TagStructuralMaterial = "StructuralMaterial"
    __TagPoissonMod = "PoissonMod"
    __TagYoungsModulus = "YoungsModulus"

    __TagBasePoint = "BasePoint"
    __TagTopPoint = "TopPoint"
    __TagStartPoint = "StartPoint"
    __TagEndPoint = "EndPoint"
    __TagLength = "Length"
    __TagCenterPoint = "CenterPoint"

    # Costing
    __TagProjectCostData = "ProjectCostData"
    __TagBarsCostData = "BarsCostData"
    __TagConnectionsCostData = "ConnectionsCostData"

    __TagCostWF = "CostWF"
    __TagOverallCost = "OverallCost"
    __TagMaterialCostPerTon = "MaterialCostPerTon"
    __TagSectionMaterialCost = "SectionMaterialCost"
    __TagSectionFabricationCost = "SectionFabricationCost"
    __TagSectionErectionCost = "SectionErectionCost"
    __TagSectionCost = "SectionCost"

    __TagMaterialCost = "MaterialCost"
    __TagFabricationCost = "FabricationCost"
    __TagErectionCost = "ErectionCost"

    # Bar to element relationships
    __TagConnectedBars = "ConnectedBars"
    __TagGroupedElements = "GroupedElements"
    __TagConnectedNotGroupedElements = "ConnectedNotGroupedElements"
    __TagAssemblyNumber = "AssemblyNumber"
    __TagIsOnGroundColumn = "IsOnGroundColumn"


    def ParseProjectModel(self, modelJSON):
        """Parses Revit model into internal Project model structure"""
        asmp = AdvanceSteelModelParser
        ump = UtilsModelParse

        model = ProjectModel()

        if isinstance(modelJSON, list):
            analyticalModel = AnalyticalModel()
            for obj in modelJSON:
                objType = ump.GetCheckExist(obj, asmp.__TagObjectType)
                if objType and objType == asmp.__ObjTypeBar:
                    analyticalModel.AddBar(self.__ParseBarGeneral(obj))
                    analyticalModel.AddBarToElementRelationships(self.__ParseBarToElementsRelationships(obj))
                else:
                    analyticalModel.AddSupportingObject(self.__ParseSupportingObject(obj))
            model.SteelAnalyticalModel = analyticalModel

        return model

    # def ParseSiteModel(self, modelJSON):
        # """Parses Revit model into internal Project model structure"""
        # from Optimization import SiteData
        # asmp = AdvanceSteelModelParser
        # ump = UtilsModelParse

        # data = SiteData()
        # model = ProjectModel()
        
        # if isinstance(modelJSON, list):
            # analyticalModel = AnalyticalModel.AnalyticalModel()
            # for obj in modelJSON:
                # objType = ump.GetCheckExist(obj, asmp.__TagObjectType)
                # if objType and objType == asmp.__ObjTypeBar:
                    # analyticalModel.AddBar(self.__ParseBarGeneral(obj))
                    # analyticalModel.AddBarToElementRelationships(self.__ParseBarToElementsRelationships(obj))
                # else:
                    # analyticalModel.AddSupportingObject(self.__ParseSupportingObject(obj))
            # model.SteelAnalyticalModel = analyticalModel
        # data.Model = model
        # return data

    def __ParseBarGeneral(self, bar):
        asmp = AdvanceSteelModelParser
        ump = UtilsModelParse
        barInst = None
        barTypeInt = ump.GetCheckExist(bar, asmp.__TagBarType, 0)
        if barTypeInt == 0:
            barInst = AnalyticalBar()
            return self.__ParseBar(barInst, bar)
        elif barTypeInt == 1:
            return self.__ParseBeam(bar)
        elif barTypeInt == 2:
            return self.__ParseCol(bar)
        else:
            return BarType.Bar
            
    def __ParseBar(self, barInst, barJSON):
        asmp = AdvanceSteelModelParser
        ump = UtilsModelParse
        barInst.Id = ump.GetCheckExist(barJSON, asmp.__TagId)
        barInst.StartPoint = ump.GetCheckExistStructure(barJSON, asmp.__TagStartPoint, ump.PointFromXYZ, Point)
        barInst.EndPoint = ump.GetCheckExistStructure(barJSON, asmp.__TagEndPoint, ump.PointFromXYZ, Point)
        barInst.CenterPoint = ump.GetCheckExistStructure(barJSON, asmp.__TagCenterPoint, ump.PointFromXYZ, Point)
        barInst.WeightPerLf = ump.GetCheckExist(barJSON, asmp.__TagWeightPerFt, 0.0)
        barInst.Weight = ump.GetCheckExist(barJSON, asmp.__TagWeight, 0.0)
        barInst.Length = ump.GetCheckExist(barJSON, asmp.__TagLength, 0.0)
        return barInst

    def __ParseBarToElementsRelationships(self, barJSON):
        asmp = AdvanceSteelModelParser
        ump = UtilsModelParse
        rels = BarToElementsRelationships()
        rels.BarId = ump.GetCheckExist(barJSON, asmp.__TagId)
        rels.Connections = ump.GetCheckExist(barJSON, asmp.__TagConnectedBars, [])
        rels.AttachedElements = ump.GetCheckExist(barJSON, asmp.__TagGroupedElements, [])
        rels.RelatedNonAttachedElements = ump.GetCheckExist(barJSON, asmp.__TagConnectedNotGroupedElements, [])
        rels.IsAttached = False
        rels.IsAttachedTo = ""
        rels.AssemblyNumber = ump.GetCheckExist(barJSON, asmp.__TagAssemblyNumber, 0)
        rels.IsOnGroundColumn = ump.GetCheckExist(barJSON, asmp.__TagIsOnGroundColumn, False)
        return rels

    def __ParseCol(self, column):
        """Parses info from Revit analytical column into internal AnalyticalColumn structure"""
        aCol = AnalyticalColumn()
        asmp = AdvanceSteelModelParser
        ump = UtilsModelParse
        self.__ParseBar(aCol, column)
        aCol.BasePoint = aCol.StartPoint
        aCol.TopPoint = aCol.EndPoint
        
        aCol.Depth = ump.GetCheckExist(column, asmp.__TagDepth, 0.0)
        aCol.MemberProductionProcedure = ump.GetCheckExistNested(column, [asmp.__TagAnnotations, asmp.__TagMemberProductionProcedure])
        aCol.RolledShapes = ump.GetCheckExistNested(column, [asmp.__TagAnnotations, asmp.__TagRolledShapes])
        aCol.TopFlangeThickness = ump.GetCheckExist(column, asmp.__TagTopFlangeThickness)

        return aCol

    def __ParseBeam(self, beam):
        """Parses info from Revit analytical beam into internal AnalyticalBeam structure"""
        asmp = AdvanceSteelModelParser
        ump = UtilsModelParse
        aBeam = AnalyticalBeam()
        self.__ParseBar(aBeam, beam)

        aBeam.Depth = ump.GetCheckExist(beam, asmp.__TagDepth, 0.0)
        aBeam.MemberProductionProcedure = ump.GetCheckExistNested(beam, [asmp.__TagAnnotations, asmp.__TagMemberProductionProcedure])
        aBeam.RolledShapes = ump.GetCheckExistNested(beam, [asmp.__TagAnnotations, asmp.__TagRolledShapes])
        aBeam.TopFlangeThickness = ump.GetCheckExist(beam, asmp.__TagTopFlangeThickness)
        aBeam.CutLength = ump.GetCheckExist(beam, asmp.__TagCutLength, 0.0)
        return aBeam

    def __ParseSupportingObject(self, supportingObject):
        asmp = AdvanceSteelModelParser
        ump = UtilsModelParse
        aObj = SupportingObject()
        aObj.Id = ump.GetCheckExist(supportingObject, asmp.__TagId)
        aObj.Type = ump.GetCheckExist(supportingObject, asmp.__TagObjectType, "Unknown")
        aObj.Weight = ump.GetCheckExist(supportingObject, asmp.__TagWeight, 0.0)
        return aObj
