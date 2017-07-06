import os, sys, json, math
__filePath = os.path.dirname(os.path.abspath(__file__))

__AMPath = os.path.join(os.path.split(__filePath)[0], "Model")
if not __AMPath in sys.path:
    sys.path.insert(1, __AMPath)

__GeomPath = os.path.join(os.path.split(os.path.split(__filePath)[0])[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from Model import *
from BLGeometry.PrefabGeometry import Point

class RevitModelParser(object):
    """Conversion of Revit analytical model JSON into common structures"""

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

    __TagCurtainWalls = "CurtainWalls"
    __TagMullions = "Mullions"
    __TagPanels = "Panels"
    __TagHeight = "Height"
    __TagThickness = "Thickness"
    __TagCorners = "Corners"
    __TagCorner = "Corner"

    __TagCranePlacements = "CranePlacements"
    __TagMaterialDropoff = "MaterialDropoff"
    __TagPoints = "Points"
    __TagPoint = "Point"

    __in2ft = 12.0

    def ParseProjectModel(self, modelJSON):
        """Parses Revit model into internal Project model structure"""
        rmp = RevitModelParser

        model = ProjectModel()
        
        # Parse Rooms
        if rmp.__TagRooms in modelJSON:
            rooms = modelJSON[rmp.__TagRooms]
            for room in rooms:
                parsedRoom = BLRoom()
                parsedRoom.LoadFromJSON(room)
                model.AddRoom(parsedRoom)

        # Parse Analytical model
        if rmp.__TagAnalyticalModel in modelJSON:
            analyticalModel = modelJSON[rmp.__TagAnalyticalModel]
            model.SteelAnalyticalModel = AnalyticalModel()
            self.__ParseAnalyticalModel(analyticalModel, model)
        
        # Parse connections
        if rmp.__TagBeamColumnConnections in modelJSON:
            connList = modelJSON[rmp.__TagBeamColumnConnections]
            self.__ParseBeamColumnConnections(connList, model)

        # Parse cost data
        if rmp.__TagProjectCostData in modelJSON:
            costs =modelJSON[rmp.__TagProjectCostData]
            if rmp.__TagBarsCostData in costs:
                barCosts = costs[rmp.__TagBarsCostData]
                for barCost in barCosts:
                    bar = model.SteelAnalyticalModel.GetBar(barCost[rmp.__TagId])
                    bar.CostWF = barCost[rmp.__TagCostWF]
                    bar.MaterialCostPerTon = barCost[rmp.__TagMaterialCostPerTon]
                    bar.OverallCost = barCost[rmp.__TagOverallCost]
                    bar.SectionMaterialCost = barCost[rmp.__TagSectionMaterialCost]
                    bar.SectionFabricationCost = barCost[rmp.__TagSectionFabricationCost]
                    bar.SectionErectionCost = barCost[rmp.__TagSectionErectionCost]
                    bar.SectionCost = barCost[rmp.__TagSectionCost]
            if rmp.__TagConnectionsCostData in costs:
                connCosts = costs[rmp.__TagConnectionsCostData]
                for connCost in connCosts:
                    conn = model.SteelAnalyticalModel.GetBeamColumnConnection(connCost[rmp.__TagId])
                    conn.MaterialCost = connCost[rmp.__TagMaterialCost]
                    conn.FabricationCost = connCost[rmp.__TagFabricationCost]
                    conn.ErectionCost = connCost[rmp.__TagErectionCost]

        return model

    def __ParseAnalyticalModel(self, analyticalModel, model):
        """Analytical model parser for Revit"""
        rmp = RevitModelParser
        if analyticalModel == None or not rmp.__TagStructuralMembers in analyticalModel:
            return

        # Parse crane and material boundaries
        if rmp.__TagCranePlacements in analyticalModel:
            cranePlacements = analyticalModel[rmp.__TagCranePlacements]
            for cranePlacement in cranePlacements:
                polygon = self.__ParseBoundaries(cranePlacement)
                model.SteelAnalyticalModel.AddCranePlacementRegion(polygon)

        if rmp.__TagMaterialDropoff in analyticalModel:
            materialDropoffs = analyticalModel[rmp.__TagMaterialDropoff]
            for materialDropoff in materialDropoffs:
                polygon = self.__ParseBoundaries(materialDropoff)
                model.SteelAnalyticalModel.AddMaterialDropoffRegion(polygon)

        # Parse columns
        if rmp.__TagColumns in analyticalModel[rmp.__TagStructuralMembers]:
            columns = analyticalModel[rmp.__TagStructuralMembers][rmp.__TagColumns]
            for column in columns:
                aSection = self.__ParseSectionInfo(column)
                if not model.SteelAnalyticalModel.ContainsSection(aSection.SectionName):
                    model.SteelAnalyticalModel.AddSection(aSection)
                aMaterial = self.__ParseMaterialInfo(column)
                if not model.SteelAnalyticalModel.ContainsMaterial(aMaterial.MaterialName):
                    model.SteelAnalyticalModel.AddMaterial(aMaterial)
                aCol = self.__ParseCol(column)
                aCol.MaterialName = aMaterial.MaterialName
                aCol.SectionName = aSection.SectionName
                model.SteelAnalyticalModel.AddBar(aCol)

        # Parse beams
        if rmp.__TagBeams in analyticalModel[rmp.__TagStructuralMembers]:
            beams = analyticalModel[rmp.__TagStructuralMembers][rmp.__TagBeams]
            for beam in beams:
                aSection = self.__ParseSectionInfo(beam)
                if not model.SteelAnalyticalModel.ContainsSection(aSection.SectionName):
                    model.SteelAnalyticalModel.AddSection(aSection)
                aMaterial = self.__ParseMaterialInfo(beam)
                if not model.SteelAnalyticalModel.ContainsMaterial(aMaterial.MaterialName):
                    model.SteelAnalyticalModel.AddMaterial(aMaterial)
                aBeam = self.__ParseBeam(beam)
                aBeam.MaterialName = aMaterial.MaterialName
                aBeam.SectionName = aSection.SectionName
                model.SteelAnalyticalModel.AddBar(aBeam)

        # Parse walls
        if rmp.__TagCurtainWalls in analyticalModel[rmp.__TagStructuralMembers]:
            curtainWalls = analyticalModel[rmp.__TagStructuralMembers][rmp.__TagCurtainWalls]
            for curtainWall in curtainWalls:
                wall = self.__ParseWall(curtainWall)
                model.SteelAnalyticalModel.AddCurtainWall(wall)

    def __ParseBeamColumnConnections(self, connList, model):
        """Beam-to-column connections parser"""
        if connList == None:
            return
        for conn in connList:
            parsedConn = self.__ParseConnection(conn)
            model.SteelAnalyticalModel.AddBeamColumnConnection(parsedConn)

    def __ParseCol(self, column):
        """Parses info from Revit analytical column into internal AnalyticalColumn structure"""
        aCol = AnalyticalColumn()
        rmp = RevitModelParser
        id = column[rmp.__TagId]
        if id:
            aCol.Id = id
        aCol.BasePoint = Point(column[rmp.__TagBasePoint][0] / rmp.__in2ft, column[rmp.__TagBasePoint][1] / rmp.__in2ft, column[rmp.__TagBasePoint][2] / rmp.__in2ft)
        aCol.TopPoint = Point(column[rmp.__TagTopPoint][0] / rmp.__in2ft, column[rmp.__TagTopPoint][1] / rmp.__in2ft, column[rmp.__TagTopPoint][2] / rmp.__in2ft)
        aCol.CenterPoint = Point((aCol.BasePoint.X + aCol.TopPoint.X) / 2.0,
                                    (aCol.BasePoint.Y + aCol.TopPoint.Y) / 2.0,
                                    (aCol.BasePoint.Z + aCol.TopPoint.Z) / 2.0);
        aCol.Length = float(column[rmp.__TagLength]) / rmp.__in2ft
        aCol.WeightPerLf = float(column[rmp.__TagWeightPerLf])
        aCol.Weight = aCol.Length * aCol.WeightPerLf

        aCol.Depth = column[rmp.__TagDepth] / rmp.__in2ft
        aCol.MemberProductionProcedure = column[rmp.__TagAnnotations][rmp.__TagMemberProductionProcedure]
        aCol.RolledShapes = column[rmp.__TagAnnotations][rmp.__TagRolledShapes]
        aCol.TopFlangeThickness = column[rmp.__TagTopFlangeThickness] / rmp.__in2ft

        return aCol

    def __ParseBeam(self, beam):
        """Parses info from Revit analytical beam into internal AnalyticalBeam structure"""
        aBeam = AnalyticalBeam()
        rmp = RevitModelParser
        id = beam[rmp.__TagId]
        if id:
            aBeam.Id = id
        aBeam.StartPoint = Point(beam[rmp.__TagStartPoint][0] / rmp.__in2ft, beam[rmp.__TagStartPoint][1] / rmp.__in2ft, beam[rmp.__TagStartPoint][2] / rmp.__in2ft)
        aBeam.EndPoint = Point(beam[rmp.__TagEndPoint][0] / rmp.__in2ft, beam[rmp.__TagEndPoint][1] / rmp.__in2ft, beam[rmp.__TagEndPoint][2] / rmp.__in2ft)
        aBeam.CenterPoint = Point((aBeam.StartPoint.X + aBeam.EndPoint.X) / 2.0,
                                    (aBeam.StartPoint.Y + aBeam.EndPoint.Y) / 2.0,
                                    (aBeam.StartPoint.Z + aBeam.EndPoint.Z) / 2.0);
        aBeam.Length = float(beam[rmp.__TagLength]) / rmp.__in2ft
        aBeam.WeightPerLf = float(beam[rmp.__TagWeightPerLf])
        aBeam.Weight = aBeam.Length * aBeam.WeightPerLf

        aBeam.Depth = beam[rmp.__TagDepth] / rmp.__in2ft
        aBeam.MemberProductionProcedure = beam[rmp.__TagAnnotations][rmp.__TagMemberProductionProcedure]
        aBeam.RolledShapes = beam[rmp.__TagAnnotations][rmp.__TagRolledShapes]
        aBeam.TopFlangeThickness = beam[rmp.__TagTopFlangeThickness] / rmp.__in2ft
        aBeam.CutLength = beam[rmp.__TagCutLength]
        return aBeam

    def __ParseConnection(self, conn):
        """Parses info from Revit BL beam-to-column connection into internal AnalyticalBeamColumnConnection structure"""
        rmp = RevitModelParser
        aConn = AnalyticalBeamColumnConnection()
        aConn.Id = conn[rmp.__TagId]
        aConn.BeamId = conn[rmp.__TagBeamId]
        aConn.ColumnId = conn[rmp.__TagColumnId]
        aConn.MaxBeamFlangeThickness = conn[rmp.__TagMaxBeamFlangeThickness]
        aConn.MaxBeamLinearWeight = conn[rmp.__TagMaxBeamLinearWeight]
        aConn.MaxBeamSize = conn[rmp.__TagMaxBeamSize]
        aConn.MaxColumnDepth = conn[rmp.__TagMaxColumnDepth]
        aConn.MinBeamFlangeThickness = conn[rmp.__TagMinBeamFlangeThickness]
        aConn.MinBeamSize = conn[rmp.__TagMinBeamSize]
        aConn.MinClearSpanDepthRatio = conn[rmp.__TagMinClearSpanDepthRatio]
        aConn.Type = conn[rmp.__TagType]
        aConn.WebToThicknessRatioOkBeam = conn[rmp.__TagWebToThicknessRatioOkBeam]
        aConn.WebToThicknessRatioOkColumn = conn[rmp.__TagWebToThicknessRatioOkColumn]
        return aConn

    def __ParseSectionInfo(self, bar):
        """Parses section info from either Revit beam or column"""
        aSection = SteelSectionInfo()
        aSection.BottomFlangeThickness = bar[RevitModelParser.__TagBottomFlangeThickness]
        aSection.CrossSectionalArea = bar[RevitModelParser.__TagCrossSectionalArea]
        aSection.Depth = bar[RevitModelParser.__TagDepth]
        aSection.MomentOfInertiaX = bar[RevitModelParser.__TagMomentOfInertiaX]
        aSection.MomentOfInertiaY = bar[RevitModelParser.__TagMomentOfInertiaY]
        aSection.PlasticSectionModulusX = bar[RevitModelParser.__TagAnnotations][RevitModelParser.__TagPlasticSectionModulus]
        aSection.RadiusOfGyrationX = bar[RevitModelParser.__TagRadiusOfGyrationX]
        aSection.RadiusOfGyrationY = bar[RevitModelParser.__TagRadiusOfGyrationY]
        aSection.SectionName = bar[RevitModelParser.__TagSection]
        aSection.TopFlangeThickness = bar[RevitModelParser.__TagTopFlangeThickness]
        aSection.WebThickness = bar[RevitModelParser.__TagWebThickness]
        aSection.Width = bar[RevitModelParser.__TagWidth]
        return aSection

    def __ParseMaterialInfo(self, bar):
        """Parses material info from either Revit beam or column info"""
        aMaterial = SteelMaterial()
        matName = bar[RevitModelParser.__TagStructuralMaterial]
        if matName:
            aMaterial.MaterialName = matName
        aMaterial.PoissonRatio = bar[RevitModelParser.__TagPoissonMod]
        aMaterial.YoungsModulus = bar[RevitModelParser.__TagYoungsModulus]
        return aMaterial

    def __ParseWall(self, curtainWall):
        """Parses info from Revit analytical curtain wall into internal AnalyticalCurtainWall structure"""
        rmp = RevitModelParser

        wall = AnalyticalCurtainWall()
        wall.Id = curtainWall[rmp.__TagId]
        wall.StartPoint = Point(curtainWall[rmp.__TagStartPoint][0] / rmp.__in2ft, curtainWall[rmp.__TagStartPoint][1] / rmp.__in2ft, curtainWall[rmp.__TagStartPoint][2] / rmp.__in2ft)
        wall.EndPoint = Point(curtainWall[rmp.__TagEndPoint][0] / rmp.__in2ft, curtainWall[rmp.__TagEndPoint][1] / rmp.__in2ft, curtainWall[rmp.__TagEndPoint][2] / rmp.__in2ft)
        wall.Height = float(curtainWall[rmp.__TagHeight]) / rmp.__in2ft

        mullions = curtainWall[rmp.__TagMullions]
        for mullion in mullions:
            m = AnalyticalMullion()
            m.Id = mullion[rmp.__TagId]
            m.StartPoint = Point(mullion[rmp.__TagStartPoint][0] / rmp.__in2ft, mullion[rmp.__TagStartPoint][1] / rmp.__in2ft, mullion[rmp.__TagStartPoint][2] / rmp.__in2ft)
            m.EndPoint = Point(mullion[rmp.__TagEndPoint][0] / rmp.__in2ft, mullion[rmp.__TagEndPoint][1] / rmp.__in2ft, mullion[rmp.__TagEndPoint][2] / rmp.__in2ft)
            m.Width = mullion[rmp.__TagWidth]
            m.Thickness = mullion[rmp.__TagThickness]
            wall.AddMullion(m)

        panels = curtainWall[rmp.__TagPanels]
        for panel in panels:
            corners = panel[rmp.__TagCorners]
            cornersCount = len(corners)

            if cornersCount == 0:
                continue

            p = AnalyticalPanel()
            p.Id = panel[rmp.__TagId]
            p.Thickness = panel[rmp.__TagThickness]

            for corner in corners:
                c = Point(corner[rmp.__TagCorner][0] / rmp.__in2ft, corner[rmp.__TagCorner][1] / rmp.__in2ft, corner[rmp.__TagCorner][2] / rmp.__in2ft);
                p.AddCorner(c)

            panelCorners = p.GetCorners()

            # Find centroid
            p.CenterPoint = Point(sum([c.X for c in panelCorners]) / cornersCount, sum([c.Y for c in panelCorners]) / cornersCount, sum([c.Z for c in panelCorners]) / cornersCount)

            # Get Start and End Points
            basePoint1 = max(panelCorners, key=lambda p: p.Z )
            basePoint2 = basePoint1
            for pnt in panelCorners:
                if pnt.Z < basePoint1.Z:
                    basePoint1, basePoint2 = pnt, basePoint1
                elif pnt.Z < basePoint2.Z:
                    basePoint2 = pnt

            if(self.__GetDistance(wall.StartPoint, basePoint1) < self.__GetDistance(wall.StartPoint, basePoint2)):
                p.StartPoint = basePoint1
                p.EndPoint = basePoint2
            else:
                p.StartPoint = basePoint2
                p.EndPoint = basePoint1

            p.Length = self.__GetDistance(p.EndPoint, p.StartPoint)
            p.Weight = p.Length * 10 # ToDo: get real weight

            wall.AddPanel(p)

        return wall

    def __GetDistance(self, p1, p2):
        """ Returns distance between two points """
        return  math.sqrt( (p2.X - p1.X)**2 + (p2.Y - p1.Y)**2 )

    def __ParseBoundaries(self, placement):
        """ Parses boundaries from points """
        rmp = RevitModelParser

        polygon = []
        points = placement[rmp.__TagPoints]

        for point in points:
            polygon.append(Point(point[rmp.__TagCorner][0] / rmp.__in2ft, point[rmp.__TagCorner][1] / rmp.__in2ft, point[rmp.__TagCorner][2] / rmp.__in2ft))

        return polygon