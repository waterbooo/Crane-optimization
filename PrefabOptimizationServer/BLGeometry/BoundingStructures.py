from .PrefabGeometry import Point
from .GeometryUtils import *
import math, copy
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LinearRing
from shapely import affinity

class BoundingBox:
    def __init__(self, minPoint = Point(), maxPoint = Point()):
        self.minPoint = Point(minPoint.X, minPoint.Y, minPoint.Z)
        self.maxPoint = Point(maxPoint.X, maxPoint.Y, maxPoint.Z)

    def isPointInside2D(self, point):
        return point.X >= self.minPoint.X and point.Y >= self.minPoint.Y and point.X <= self.maxPoint.X and point.Y <= self.maxPoint.Y

    def getNearestPointInside2D(self, point):
        if self.isPointInside2D(point):
            return point
        else:
            result = Point(point.X, point.Y, point.Z)
            dx1 = point.X - self.maxPoint.X
            dx2 = self.minPoint.X - point.X
            dy1 = point.Y - self.maxPoint.Y
            dy2 = self.minPoint.Y - point.Y
            if dx1 > 0.0:
                result.X = self.maxPoint.X
            elif dx2 > 0.0:
                result.X = self.minPoint.X
            if dy1 > 0.0:
                result.Y = self.maxPoint.Y
            elif dy2 > 0.0:
                result.Y = self.minPoint.Y
            return result

    def getNearestPointOutside2D(self, point):
        if not self.isPointInside2D(point):
            return point
        else:
            result = Point(point.X, point.Y, point.Z)
            dx1 =  - point.X + self.maxPoint.X
            dx2 =  - self.minPoint.X + point.X
            dy1 = - point.Y + self.maxPoint.Y
            dy2 = - self.minPoint.Y + point.Y
            if dx1 < dx2:
                result.X = self.maxPoint.X
            else:
                result.X = self.minPoint.X
            if dy1 < dy2:
                result.Y = self.maxPoint.Y
            else:
                result.Y = self.minPoint.Y
            return result

class BoundingBoxPolygon(BoundingBox):

    def __init__(self, contourcollections = [], corrections = (0,0), craneBaseSize=(15,15)):
        import numpy as np
        from shapely.geometry import Polygon
        contours = []
        paths = []
        # for each contour line
        for cc in contourcollections:
            pathpolygones = []
            # for each separate section of the contour line
            for pp in cc.get_paths():
                xy = []
                # for each segment of that section
                for vv in pp.iter_segments():
                    xy.append(vv[0])
                path = np.vstack(xy)
                path = [(p[0], p[1]) for p in path]
                pathpolygones.append(Polygon(path))
            contours.append(paths)
            paths.append(pathpolygones)
        polygons = []
        if paths and paths[0]:
            polygons.append(paths[0][0])
        for p in paths:
            for pp in p:
                includePP = False
                indsToRemove = []
                for i in range(len(polygons)):
                    c = polygons[i]
                    if pp.covers(c):
                        includePP = True
                        indsToRemove.append(i)
                if includePP:
                    indsToRemove.reverse()
                    for i in indsToRemove:
                        polygons.pop(i)
                    polygons.append(pp)
        
        self.polygons = polygons
        minPoint = Point()
        maxPoint = Point()

        for i in range(len(self.polygons)):
            polygon = self.polygons[i]
            sizeX = polygon.bounds[2] - polygon.bounds[0]
            sizeY = polygon.bounds[3] - polygon.bounds[1]
            baseFactorSize = max(craneBaseSize[0], craneBaseSize[1]) / 2 + 1
            xFact = (sizeX + 2 * baseFactorSize) / sizeX
            yFact = (sizeY + 2 * baseFactorSize) / sizeY
            self.polygons[i] = affinity.scale(polygon, xfact=xFact, yfact=yFact, origin="center")
            if not self.polygons[i].is_valid:
                self.polygons[i] = self.polygons[i].buffer(0)
            self.polygons[i] = affinity.translate(self.polygons[i], corrections[0], corrections[1])

        if self.polygons:
            minPoint = Point(np.min([pol.bounds[0] for pol in self.polygons]), np.min([pol.bounds[1] for pol in self.polygons]))
            maxPoint = Point(np.max([pol.bounds[2] for pol in self.polygons]), np.max([pol.bounds[3] for pol in self.polygons]))
            
        self.multiPolygon = MultiPolygon(self.polygons)


        axisRes = GetPolygonRotationAngle(self.multiPolygon)
        self.angle = -axisRes[0]
        self.minAreaMultiPolygon = axisRes[1]
        return super().__init__(minPoint, maxPoint)

    def getNearestPointInside2D(self, point):
        p = GetNearestPointOnAreaBound(point, self.polygons)
        return Point(p[0], p[1])

class BoundingEllipse:
    def __init__(self, minPoint = Point(), maxPoint = Point()):
        self.minPoint = Point(minPoint.X, minPoint.Y, minPoint.Z)
        self.maxPoint = Point(maxPoint.X, maxPoint.Y, maxPoint.Z)
        self.radiusX = (maxPoint.X - minPoint.X) / 2.0
        self.radiusY = (maxPoint.Y - minPoint.Y) / 2.0
        self.centerPoint = Point((maxPoint.X + minPoint.X) / 2.0, (maxPoint.Y + minPoint.Y) / 2.0, (maxPoint.Z + minPoint.Z) / 2.0)
        self.tolerance = 0.00000001
          
    def isPointInside2D(self, point):
        return ((point.X - self.centerPoint.X) / self.radiusX)**2 + ((point.Y - self.centerPoint.Y) / self.radiusY)**2 - self.tolerance <= 1

    def getNearestPointInside2D(self, point):
        if self.isPointInside2D(point):
            return point
        else:
            points = LineEllipseIntersection(self.centerPoint.X, self.centerPoint.Y, point.X, point.Y, self.radiusX, self.radiusY, self.centerPoint.X, self.centerPoint.Y, False)
            if point.distanceTo(points[0]) <= point.distanceTo(points[1]):
                return points[0]
            else:
                return points[1]
            

    def isInsideBoundingBox(self, boundingBox):
        return self.minPoint.X >= boundingBox.minPoint.X and self.minPoint.Y >= boundingBox.minPoint.Y and self.maxPoint.X <= boundingBox.maxPoint.X and self.maxPoint.Y <= boundingBox.maxPoint.Y

    def isTouchingBoundingBox(self, boundingBox):
        return abs(self.minPoint.X - boundingBox.minPoint.X) < self.tolerance or abs(self.minPoint.Y - boundingBox.minPoint.Y) < self.tolerance or abs(self.maxPoint.X - boundingBox.maxPoint.X) < self.tolerance or abs(self.maxPoint.Y - boundingBox.maxPoint.Y) < self.tolerance

    def boundingBoxIntersections(self, boundingBox):
        result = []
        if not self.isInsideBoundingBox(boundingBox):
            result
        elif self.isTouchingBoundingBox(boundingBox):
            if abs(self.minPoint.X - boundingBox.minPoint.X) < self.tolerance:
                result.append(Point(boundingBox.minPoint.X, self.centerPoint.Y, 0.0))
            if abs(self.minPoint.Y - boundingBox.minPoint.Y) < self.tolerance:
                result.append(Point(self.centerPoint.X, boundingBox.minPoint.Y, 0.0))
            if abs(self.maxPoint.X - boundingBox.maxPoint.X) < self.tolerance:
                result.append(Point(boundingBox.maxPoint.X, self.centerPoint.Y, 0.0))
            if abs(self.maxPoint.Y - boundingBox.maxPoint.Y) < self.tolerance:
                result.append(Point(self.centerPoint.X, boundingBox.maxPoint.Y, 0.0))
        return result

    #TODO: add nearest outside point calculation
    #def getNearestPointOutside2D(self, point):
    #    if not self.isPointInside2D(point):
    #        return point
    #    else:
    #        # nearest point on ellipse is point on line connected with ellipse center
    #        result = Point(point.X, point.Y, point.Z)
    #        result.X = self.radiusX * (point.X - self.centerPoint.X) / math.sqrt((point.X - self.centerPoint.X)**2 + (point.Y - self.centerPoint.Y)**2)
    #        result.Y = (result.X - point.X) * (point.Y - self.centerPoint.Y) / (point.X - centerPoint.X) + point.Y
    #        return result

class BoundingEllipsePolygon(BoundingEllipse):
    def __init__(self, angle, minPoint = Point(), maxPoint = Point()):

        x0 = (maxPoint.X + minPoint.X) / 2.0
        y0 = (maxPoint.Y + minPoint.Y) / 2.0
        a = (maxPoint.X - minPoint.X) / 2.0
        b = (maxPoint.Y - minPoint.Y) / 2.0
        elCoords = GenerateEllipseCoords(x0, y0, a, b, angle)
        self.polygon = Polygon(elCoords)
        self.angle = angle
        self.a = a
        self.b = b
        self.x0 = x0
        self.y0 = y0
        return super().__init__(Point(self.polygon.bounds[0], self.polygon.bounds[1]), Point(self.polygon.bounds[2], self.polygon.bounds[3]))
        

 
