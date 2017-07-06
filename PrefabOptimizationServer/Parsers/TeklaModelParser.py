import os, sys, json
__filePath = os.path.dirname(os.path.abspath(__file__))

__AMPath = os.path.join(os.path.split(__filePath)[0], "Model")
if not __AMPath in sys.path:
    sys.path.insert(1, __AMPath)

__GeomPath = os.path.join(os.path.split(os.path.split(__filePath)[0])[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from Model import *
from BLGeometry.PrefabGeometry import Point

class TeklaModelParser(object):
    """Utility object which parses Tekla analytical model into internal known structures"""

    __TagBasePoint = "BasePoint"
    __TagTopPoint = "TopPoint"
    __TagStartPoint = "StartPoint"
    __TagEndPoint = "EndPoint"
    __TagLength = "Length"
    __TagWeightPerLf = "WeightPerLF"
    __TagColumns = "Columns"
    __TagBeams = "Beams"
    __TagId = "Id"
    __TagBottomFlangeThickness = "BottomFlangeThickness"
    __TagCrossSectionalArea = "CrossSectionalArea"
    __TagDepth = "Depth"
    __TagMomentOfInertiaX = "MomentOfInertiaX"
    __TagMomentOfInertiaY = "MomentOfInertiaY"
    __TagAnnotations = "Annotations"
    __TagPlasticSectionModulus = "PlasticSectionModulus"
    __TagRadiusOfGyrationX = "RadiusOfGyrationX"
    __TagRadiusOfGyrationY = "RadiusOfGyrationY"
    __TagSection = "Section"
    __TagTopFlangeThickness = "TopFlangeThickness"
    __TagWebThickness = "WebThickness"
    __TagWidth = "Width"
    __TagStructuralMaterial = "StructuralMaterial"
    __TagPoissonMod = "PoissonMod"
    __TagYoungsModulus = "YoungsModulus"
    
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def ParseProjectModel(self, modelJSON):
        """Parses Tekla analytical model info into internal AnalyticalModel structure"""
        pm = ProjectModel()
        model = AnalyticalModel()
        if TeklaModelParser.__TagColumns in modelJSON:
            columns = modelJSON[TeklaModelParser.__TagColumns]
            for column in columns:
                aSection = self.__ParseSectionInfo(column)
                if not model.ContainsSection(aSection.SectionName):
                    model.AddSection(aSection)
                aMaterial = self.__ParseMaterialInfo(column)
                if not model.ContainsMaterial(aMaterial.MaterialName):
                    model.AddMaterial(aMaterial)
                aCol = self.__ParseCol(column)
                aCol.MaterialName = aMaterial.MaterialName
                aCol.SectionName = aSection.SectionName
                model.AddBar(aCol)

        if TeklaModelParser.__TagBeams in modelJSON:
            beams = modelJSON[TeklaModelParser.__TagBeams]
            for beam in beams:
                aSection = self.__ParseSectionInfo(beam)
                if not model.ContainsSection(aSection.SectionName):
                    model.AddSection(aSection)
                aMaterial = self.__ParseMaterialInfo(beam)
                if not model.ContainsMaterial(aMaterial.MaterialName):
                    model.AddMaterial(aMaterial)
                aBeam = self.__ParseBeam(beam)
                aBeam.MaterialName = aMaterial.MaterialName
                aBeam.SectionName = aSection.SectionName
                model.AddBar(aBeam)
        pm.SteelAnalyticalModel = model
        return pm

    def __ParseCol(self, column):
        """Parses info from Tekla analytical column into internal AnalyticalColumn structure"""
        aCol = AnalyticalColumn()
        id = column[TeklaModelParser.__TagId]
        if id:
            aCol.Id = id
        aCol.BasePoint = Point(column[TeklaModelParser.__TagBasePoint][0], column[TeklaModelParser.__TagBasePoint][1], column[TeklaModelParser.__TagBasePoint][2])
        aCol.TopPoint = Point(column[TeklaModelParser.__TagTopPoint][0], column[TeklaModelParser.__TagTopPoint][1], column[TeklaModelParser.__TagTopPoint][2])
        aCol.CenterPoint = Point((aCol.BasePoint.X + aCol.TopPoint.X) / 2.0,
                                    (aCol.BasePoint.Y + aCol.TopPoint.Y) / 2.0,
                                    (aCol.BasePoint.Z + aCol.TopPoint.Z) / 2.0);
        aCol.Length = float(column[TeklaModelParser.__TagLength])
        aCol.WeightPerLf = float(column[TeklaModelParser.__TagWeightPerLf])
        aCol.Weight = aCol.Length * aCol.WeightPerLf
        return aCol

    def __ParseBeam(self, beam):
        """Parses info from Tekla analytical beam into internal AnalyticalBeam structure"""
        aBeam = AnalyticalBeam()
        id = beam[TeklaModelParser.__TagId]
        if id:
            aBeam.Id = id
        aBeam.StartPoint = Point(beam[TeklaModelParser.__TagStartPoint][0], beam[TeklaModelParser.__TagStartPoint][1], beam[TeklaModelParser.__TagStartPoint][2])
        aBeam.EndPoint = Point(beam[TeklaModelParser.__TagEndPoint][0], beam[TeklaModelParser.__TagEndPoint][1], beam[TeklaModelParser.__TagEndPoint][2])
        aBeam.CenterPoint = Point((aBeam.StartPoint.X + aBeam.EndPoint.X) / 2.0,
                                    (aBeam.StartPoint.Y + aBeam.EndPoint.Y) / 2.0,
                                    (aBeam.StartPoint.Z + aBeam.EndPoint.Z) / 2.0);
        aBeam.Length = float(beam[TeklaModelParser.__TagLength])
        aBeam.WeightPerLf = float(beam[TeklaModelParser.__TagWeightPerLf])
        aBeam.Weight = aBeam.Length * aBeam.WeightPerLf
        return aBeam

    def __ParseSectionInfo(self, bar):
        """Parses section info from either Tekla beam or column"""
        aSection = SteelSectionInfo()
        aSection.BottomFlangeThickness = bar[TeklaModelParser.__TagBottomFlangeThickness]
        aSection.CrossSectionalArea = bar[TeklaModelParser.__TagCrossSectionalArea]
        aSection.Depth = bar[TeklaModelParser.__TagDepth]
        aSection.MomentOfInertiaX = bar[TeklaModelParser.__TagMomentOfInertiaX]
        aSection.MomentOfInertiaY = bar[TeklaModelParser.__TagMomentOfInertiaY]
        aSection.PlasticSectionModulusX = bar[TeklaModelParser.__TagAnnotations][TeklaModelParser.__TagPlasticSectionModulus]
        aSection.RadiusOfGyrationX = bar[TeklaModelParser.__TagRadiusOfGyrationX]
        aSection.RadiusOfGyrationY = bar[TeklaModelParser.__TagRadiusOfGyrationY]
        aSection.SectionName = bar[TeklaModelParser.__TagSection]
        aSection.TopFlangeThickness = bar[TeklaModelParser.__TagTopFlangeThickness]
        aSection.WebThickness = bar[TeklaModelParser.__TagWebThickness]
        aSection.Width = bar[TeklaModelParser.__TagWidth]
        return aSection

    def __ParseMaterialInfo(self, bar):
        """Parses material info from either Tekla beam or column info"""
        aMaterial = SteelMaterial()
        matName = bar[TeklaModelParser.__TagStructuralMaterial]
        if matName:
            aMaterial.MaterialName = matName
        aMaterial.PoissonRatio = bar[TeklaModelParser.__TagPoissonMod]
        aMaterial.YoungsModulus = bar[TeklaModelParser.__TagYoungsModulus]
        return aMaterial