import os, sys
__filePath = os.path.dirname(os.path.realpath(__file__))

__GeomPath = os.path.join(os.path.split(__filePath)[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from Model import ProjectModel, BarType

import copy, math
from BLGeometry import GeometryUtils
from BLGeometry.PrefabGeometry import Point
from BLGeometry.BoundingStructures import BoundingBox, BoundingBoxPolygon, BoundingEllipsePolygon
import networkx as nx
from Optimization.Order.ConstructionOrdering import ConstructionOrdering
from shapely.geometry import MultiPoint,MultiPolygon, Polygon
from shapely import affinity

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
import numpy as np

class SiteData:
    """Data about site: 
            Model - model to be constructed
            SitePolygon - polygon of site measures
            ModelPolygon - bounding polygon for a model
    """
    def __init__(self, projectModel, craneData=[], surroundingPolygons=[], sitePolygons=[], *args, **kwargs):
        """
            arguments:
                projectModel: pre-parsed ProjectModel structure from one of the client packages
                craneData: pre-parsed CraneData structures array. May be empty.
                surroundingPolygons: an array of regions where crane could not rotate (e.g. surrounding skyscrapers)
                        format is [[{'X':0.0 'Y':0.0 'Z':0.0}, {'X':0.0 'Y':0.0 'Z':0.0}, ...], ...]
                sitePolygons: an array of regions describing site contours
                        format is [[{'X':0.0 'Y':0.0 'Z':0.0}, {'X':0.0 'Y':0.0 'Z':0.0}, ...], ...]
        """
        # TODO: Propertize class
        # Model data should be pre-parsed
        # TODO: think about parsing it just from here
        self._model = projectModel if projectModel else ProjectModel.ProjectModel()
        self._cranes = craneData
        
        
        # TODO: fill new bounding structures
        self._modelPolygon = None
        self._sitePolygon = None

        # Fill often used values
        structualObjects = self.ConstructionObjects.values()
        # TODO: move to properties
        self.maxSiteDataObjectLength = 0.0
        self.maxSiteDataObjectLength = np.max([obj.Length for obj in structualObjects])
        self.maxSiteDataObjectWeight = np.max([obj.Weight for obj in structualObjects])

        # Fill demand points as center of each bar
        # TODO: move to properties
        self.demandPoints = [obj.CenterPoint for obj in structualObjects]

        # Crane should be able to be placed and rotate, that's why we need to define a buffer of extra size on model BB
        # TODO: modify to be used just in calculations or to dict of BBs
        craneDeltaX = 0.0
        craneDeltaY = 0.0
        if len(craneData) > 0:
            craneDeltaX = np.max([c.baseSizeX for c in craneData]) / 2.0
            craneDeltaY = np.max([c.baseSizeY for c in craneData]) / 2.0
        
        # Define model bounding box
        self.boundingBox = BoundingBox()
        self.boundingBox.maxPoint.X = np.max([np.max([obj.CenterPoint.X, obj.StartPoint.X, obj.EndPoint.X]) for obj in structualObjects]) + craneDeltaX
        self.boundingBox.maxPoint.Y = np.max([np.max([obj.CenterPoint.Y, obj.StartPoint.Y, obj.EndPoint.Y]) for obj in structualObjects]) + craneDeltaY
        self.boundingBox.minPoint.X = np.min([np.min([obj.CenterPoint.X, obj.StartPoint.X, obj.EndPoint.X]) for obj in structualObjects]) - craneDeltaX
        self.boundingBox.minPoint.Y = np.min([np.min([obj.CenterPoint.Y, obj.StartPoint.Y, obj.EndPoint.Y]) for obj in structualObjects]) - craneDeltaY

        # Calculation tolerance
        # TODO: move to constants
        self.tolerance = 0.00000001

        # Create an empty dependencies graph
        self.dependencies = nx.DiGraph()

        # Calculate model bounding polygon 
        # not sure what's this about....
        modelContour = self.getModelContour()
        self.boundingPolygon = BoundingBoxPolygon(modelContour[0].collections, corrections=modelContour[1])
        bounds = self.boundingPolygon.minAreaMultiPolygon.bounds
        self._modelPolygon = self.boundingPolygon.multiPolygon

        """
        if len(craneData) > 0:
            maxAvailableLengths = [c.getMaxRadiusForCapacity(self.maxSiteDataObjectWeight) for c in craneData]
            dX = maxAvailableLengths[0] - (bounds[2] - bounds[0])
            dY = maxAvailableLengths[0] - (bounds[3] - bounds[1])
        """
        if len(craneData) > 0:
            maxAvailableLengths = [c.getMaxRadiusForCapacity(self.maxSiteDataObjectWeight) for c in craneData]
            dX =  (bounds[2] - bounds[0])*0.5
            dY =  (bounds[3] - bounds[1])*0.5

        # Acceptable region for crane
        # TODO: parallelize for multiple cranes and bar clusters
        if len(craneData) == 1:
            self.craneEllipsePolygon = BoundingEllipsePolygon(self.boundingPolygon.angle, Point(bounds[0] - dX, bounds[1] - dY), Point(bounds[2] + dX, bounds[3] + dY))
            #extension = 300
            #P1=Point(bounds[0] - extension, bounds[1] - extension,0)
            #P2=Point(bounds[2] + extension, bounds[1] - extension,0)
            #P3=Point(bounds[2] + extension, bounds[3] + extension,0)
            #P4=Point(bounds[0] - extension, bounds[3] + extension,0)
            #self.craneEllipsePolygon = Polygon([(P1.X,P1.Y),(P2.X,P2.Y),(P3.X,P3.Y),(P4.X,P4.Y)])
            craneData[0].accessingCircleForModel = GeometryUtils.CreateEllipsePolygon(0, 0, maxAvailableLengths[0], maxAvailableLengths[0], 0)
        else:
            self.craneEllipsePolygon = None

        # Proceed surrounding polygons
        self.surroundingPolygons = []
        try:
            for sp in surroundingPolygons:
                coords = [(c["X"], c["Y"]) for c in sp]
                try:
                    pol = Polygon(coords)
                    self.surroundingPolygons.append(pol)
                except:
                    pass
        except:
            pass

        if self.surroundingPolygons:
            self.surroundingPolygons = MultiPolygon(self.surroundingPolygons)

        # Proceed site polygons
        self.sitePolygons = []
        try:
            for sp in sitePolygons:
                coords = [(c["X"], c["Y"]) for c in sp]
                try:
                    pol = Polygon(coords)
                    self.sitePolygons.append(pol)
                except:
                    pass
        except:
            pass

        if self.sitePolygons:
            self.sitePolygons = MultiPolygon(self.sitePolygons)

        self.acceptableRegionForMaterials = GeometryUtils.pointsToMultiPolygon(projectModel.SteelAnalyticalModel.GetMaterialDropoffRegions())
        self.acceptableRegionForCranes = GeometryUtils.pointsToMultiPolygon(projectModel.SteelAnalyticalModel.GetCranePlacementRegions())

        from shapely.geometry import Point as ShPoint
        if self.acceptableRegionForCranes:
            maxDistance = np.max([self.acceptableRegionForCranes.distance(ShPoint(obj.CenterPoint.X, obj.CenterPoint.Y)) for obj in structualObjects])
            if maxDistance > np.max([c.getMaxRadius() for c in craneData]):
                raise ValueError("None of cranes can reach structural object")
        
        wallPolygon = self.wallsToPolygon()

        if self.surroundingPolygons:
            self.prohibitedRegion = MultiPolygon([wallPolygon] + self.surroundingPolygons + self.boundingPolygon.multiPolygon.geoms)
        else:
            #self.prohibitedRegion = MultiPolygon([wallPolygon] + self.boundingPolygon.polygons)
            self.prohibitedRegion = wallPolygon

        sizeX = self.prohibitedRegion.bounds[2] - self.prohibitedRegion.bounds[0]
        sizeY = self.prohibitedRegion.bounds[3] - self.prohibitedRegion.bounds[1]

        baseFactorSize = max(craneData[0].baseSizeX, craneData[0].baseSizeY) / 2 + 1
        xFact = (sizeX +  0.8*baseFactorSize) / sizeX
        yFact = (sizeY +  0.8*baseFactorSize) / sizeY
        self.prohibitedRegion = affinity.scale(self.prohibitedRegion, xfact=xFact, yfact=yFact, origin="center")
           
        
        # Leave supply points empty for the first time
        self.supplyPoints = []

        
        from matplotlib import pyplot as plt
        fig = plt.figure(5, figsize=(5,5), dpi=90)
        plt.subplot(111)
        x1,y1=self.prohibitedRegion.exterior.xy

       
    def wallsToPolygon(self):
        wallPoints = [(self.Walls[i].StartPoint.X, self.Walls[i].StartPoint.Y) for i in self.Walls] + [(self.Walls[i].EndPoint.X, self.Walls[i].EndPoint.Y) for i in self.Walls]
   
        return MultiPoint(wallPoints).convex_hull

    @property
    def Model(self):
        """Project model"""
        return self._model

    @Model.setter
    def Model(self, value):
        self._model = value

    @Model.deleter
    def Model(self):
        del self._model

    @property
    def Bars(self):
        """Bar id to instance mapping for model"""
        return self._model.SteelAnalyticalModel.Bars

    @property
    def Walls(self):
        """Wall id to instance mapping for model"""
        return self._model.SteelAnalyticalModel.Walls

    @property
    def Panels(self):
        """Panel id to instance mapping for model"""
        return self._model.SteelAnalyticalModel.Panels

    @property
    def ConstructionObjects(self):
        """Construction Object instances for model"""
        return self._model.SteelAnalyticalModel.ConstructionObjects

    @property
    def ModelPolygon(self):
        """MultiPolygon bounding project model"""
        return self._modelPolygon

    @property
    def SitePolygon(self):
        """MultiPolygon bounding site"""
        return self._sitePolygon

    def getModelContour(self):
        """Gets contour polygon for a model"""
        import matplotlib
        matplotlib.use('Agg')

        import matplotlib.pyplot as plt
        from PIL import Image, ImageDraw
        from scipy import misc
        import uuid, copy

        # create canvas with the size of bounding box + buffer
        image = Image.new("RGB", (int(self.boundingBox.maxPoint.X - self.boundingBox.minPoint.X + 20), int(self.boundingBox.maxPoint.Y - self.boundingBox.minPoint.Y + 20)), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        correctionX = self.boundingBox.minPoint.X - 10
        correctionY = self.boundingBox.minPoint.Y - 10

        # draw all construction objects lines
        for obj in self.ConstructionObjects.values():
            draw.line([(obj.StartPoint.X - correctionX, obj.StartPoint.Y - correctionY), (obj.EndPoint.X - correctionX, obj.EndPoint.Y - correctionY)], fill=(0,0,0), width=1)

        # save temp image
        id = str(uuid.uuid1())
        image.save(id + ".png")
        
        # read an image and delete temp file
        face = misc.imread(id + ".png")
        os.remove(id + ".png")

        # convert into b&w
        face = (0.21 * face[:,:,0] + 0.71 * face[:,:,1] + 0.07 * face[:,:,2]).astype("uint8")
        plt.imshow(face, cmap=plt.cm.gray)

        # get contour
        cn = plt.contour(face)
        return (cn, (correctionX, correctionY))

    def isAcceptableCranePoint(self, location):
        """checks whether crane point candidate is an acceptable one"""
        from shapely.geometry import Point as ShPoint
        p = ShPoint((location.X, location.Y))
        return p.within(self.acceptableRegionForCranes)

    def getDistanceToAcceptableCraneRegion(self, location):
        """Gets shortest distance to acceptable region for crane"""
        from shapely.geometry import Point as ShPoint
        p = ShPoint((location.X, location.Y))
        if p.within(self.acceptableRegionForCranes):
            return 0.0
        return GeometryUtils.GetDistanceToAreaBound(p, [self.acceptableRegionForCranes])

    def isAcceptableSupplyPoint(self, location, cx, cy, craneData):
        """Checks whether supply point candidate is acceptable"""
        circle = affinity.translate(craneData.accessingCircleForModel, cx, cy)
        tmp = circle.difference(self.prohibitedRegion)
        reg = tmp.intersection(self.acceptableRegionForMaterials)
        from shapely.geometry import Point as ShPoint
        p = ShPoint((location.X, location.Y))
        return p.within(reg)

    def getDistanceToAcceptableSupplyRegion(self, location, cx, cy, craneData):
        """Gets shortest distance to acceptable region for supply point"""
        circle = affinity.translate(craneData.accessingCircleForModel, cx, cy)
        tmp = circle.difference(self.prohibitedRegion)
        reg = tmp.intersection(self.acceptableRegionForMaterials)
        from shapely.geometry import Point as ShPoint
        p = ShPoint((location.X, location.Y))
        if p.within(reg):
            return 0.0
        return GeometryUtils.GetDistanceToAreaBound(p, [reg])
    
    def getNearestCraneAcceptablePoint2D(self, location):
        """Gets acceptable crane point candidate as a nearest acceptable point for passed location"""
        from shapely.geometry import Point as ShPoint
        p = ShPoint((location.X, location.Y))
        if not p.within(self.acceptableRegionForCranes):
            coords = GeometryUtils.GetNearestPointOnAreaBound(p, self.acceptableRegionForCranes.geoms)
            p = ShPoint(coords)
        result = Point(p.x, p.y, location.Z)
        return result

    def getNearestAcceptableSupplyPoint2D(self, location, cx, cy, craneData):
        """Gets acceptable supply point candidate as a nearest acceptable point for passed location"""
        circle = affinity.translate(craneData.accessingCircleForModel, cx, cy)
        tmp = circle.difference(self.prohibitedRegion)
        reg = tmp.intersection(self.acceptableRegionForMaterials)
        from shapely.geometry import Point as ShPoint
        p = ShPoint((location.X + cx, location.Y + cy))
        if not p.within(reg):
            pols = [reg]
            if isinstance(reg, MultiPolygon):
                pols = reg.geoms
            coords = GeometryUtils.GetNearestPointOnAreaBound(p, pols)
            p = ShPoint(coords)
        result = Point(p.x - cx, p.y - cy, location.Z)
        return result

    def getBoundingPolygonCoords(self, jsonFormat=False):
        """Returns array of arrays with bounding polygons points coords"""
        from shapely.geometry import Polygon, Point as ShPoint, LinearRing, GeometryCollection, MultiPolygon
        coords = []
        pols = GeometryUtils.GetPurePolygonsFromMixedArray(self.boundingPolygon.polygons)

        for poly in pols:
            if jsonFormat:
                coords.append([{"X":coord[0], "Y":coord[1], "Z": 0.0} for coord in poly.exterior.coords])
            else:
                coords.append([Point(coord[0], coord[1]) for coord in poly.exterior.coords])

        return coords



    def GetBarRelatedElements(self, barId):
        """Returns object with ids of connected bars, attached and non-attacher, but related elements"""
        return self.Model.SteelAnalyticalModel.GetBarToElementRelationships(barId)

    def ClosestAppliableSupplyPointToModelCenter(self):
        """Gets acceptable supply point as a nearest acceptable point for model center"""
        from shapely.geometry import Point as ShPoint
        # Get model bounding polygon from site data
        bp = self.boundingPolygon.multiPolygon
        region = bp

        # Get site polygons from site data, if there are any
        sp = []
        if not isinstance(self.sitePolygons, list):
            sp = self.sitePolygons
            region = sp.difference(bp)
        elif isinstance(self.acceptableRegionForMaterials, MultiPolygon):
            sp = self.acceptableRegionForMaterials
            region = sp.difference(bp)

        # Take a model polygon centroid point as the location for supply point
        p = bp.centroid
        
        # Check whether p in region polygon
        pInRegion = p.within(region)

        # If polygon is model bounds and p in it
        # or polygon is difference of site borders to model bounds and p isn't in it
        # do a projection on polygon bound
        if (isinstance(sp, list) and pInRegion) or (not isinstance(sp, list) and not pInRegion):
            pols = [region]
            if isinstance(region, MultiPolygon):
                pols = region.geoms
            coords = GeometryUtils.GetNearestPointOnAreaBound(p, pols)
            p = ShPoint(coords)

        # return Build Logic Point structure
        result = Point(p.x, p.y)
        return result

    def GetSupplyPoints(self):
        """If supply points are already defined, just return
           calculate othervise
        """
        if len(self.supplyPoints) == 0:
            sp = self.ClosestAppliableSupplyPointToModelCenter()
            self.supplyPoints.append(sp)
        return self.supplyPoints

