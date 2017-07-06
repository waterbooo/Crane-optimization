from .PrefabGeometry import Point
import math
from shapely.geometry import Polygon, MultiPolygon
import numpy as np

def LineEllipseIntersection(x0, y0, x1, y1, rx, ry, cx, cy, checkInterval):
    """Get intersection points of line and ellipse
    
    Returns an array of intersection points
    If there is no intersections an empty array is returned
    Line equation through two points and classical ellipse equation are used

    Parameters
    ----------
    x0 : float
        x coordinate of the first point for line equation
    y0 : float
        y coordinate of the first point for line equation
    x1 : float
        x coordinate of the second point for line equation
    y1 : float
        y coordinate of the second point for line equation
    rx : float
        x radius of ellipse
    ry : float
        y radius of ellipse
    cx : float
        x coordinate of ellipse center
    cy : float 
        y coordinate of ellipse center
    checkInterval : bool
        indicates whether result points should be on line between the first and the second points

    Returns
    ----------
    intersections : array
        array of intersection points 
        in case of true value of checkInterval contains only points in interval

    """
    tolerance = 0.0000001
    results = []
            
    # Quadratic equation for x: a*x^2 + bx + c = 0
    ax = x1 - x0
    ay = y1 - y0
    rx2 = rx * rx
    ry2 = ry * ry
    ax2 = ax * ax
    ay2 = ay * ay
            
    if abs(ax) > tolerance and abs(ay) > tolerance:
        # a, b and c are got from two equations:
        # Ellipse equation: (x - cx)^2 / rx^2 + (y - cy)^2 / ry^2 = 1
        # line equation: (x - x1) / (x1 - x0) = (y - y1) / (y1 - y0)
        dy = y1 - cy
        a = 1.0 / rx2 + ay2 / (ry2 * ax2)
        b = 2.0 * ((- cx / rx2) + ay * ( - (ay * x1) / ax + dy) / (ax * ry2))
        c = (cx * cx / rx2) + (1.0 / (ax2 * ry2)) * (x1 * x1 * ay2 - 2.0 * ax * ay * dy * x1 + ax2 * dy * dy) - 1.0
            
        D2 = b * b - 4.0 * a * c

        if D2 >= 0:
            D = math.sqrt(D2)
            xres1 = (- b + D) / (2.0 * a)
            yres1 = (xres1 - x1) * ay / ax + y1
            if not checkInterval or (((xres1 <= x0 and xres1 >= x1) or (xres1 <= x1 and xres1 >= x0)) and ((yres1 <= y0 and yres1 >= y1) or (yres1 <= y1 and yres1 >= y0))):
                point1 = Point(xres1, yres1, 0.0)
                results.append(point1)
            if D2 > tolerance:
                xres2 = (- b - D) / (2.0 * a)
                yres2 = (xres2 - x1) * ay / ax + y1
                if not checkInterval or (((xres2 <= x0 and xres2 >= x1) or (xres2 <= x1 and xres2 >= x0)) and ((yres2 <= y0 and yres1 >= y1) or (yres2 <= y1 and yres2 >= y0))):
                    point2 = Point(xres2, yres2, 0.0)
                    results.append(point2)
    elif abs(ax) <= tolerance:
        # x is constant, need just to find y coords
        # Using Ellipse equation: (x - cx)^2 / rx^2 + (y - cy)^2 / ry^2 = 1
        x = x0
        dx = x - cx
        a = 1.0 / ry2
        b = - 2.0 * cy / ry2
        c = (cy * cy) / ry2 + (dx * dx) / rx2 - 1.0
        D2 = b * b - 4.0 * a * c

        if D2 >= 0:
            D = math.sqrt(D2)
            yres1 = (- b + D) / (2.0 * a)
            if not checkInterval or ((yres1 <= y0 and yres1 >= y1) or (yres1 <= y1 and yres1 >= y0)):
                point1 = Point(x, yres1, 0.0)
                results.append(point1)
            if D2 > tolerance:
                yres2 = (- b - D) / (2.0 * a)
                if not checkInterval or ((yres2 <= y0 and yres2 >= y1) or (yres2 <= y1 and yres2 >= y0)):
                    point2 = Point(x, yres2, 0.0)
                    results.append(point2)

    elif abs(ay) <= tolerance:
        # y is constant, need just to find x coords
        # Using Ellipse equation: (x - cx)^2 / rx^2 + (y - cy)^2 / ry^2 = 1
        y = y0
        dy = y - cy
        a = 1.0 / rx2
        b = - 2.0 * cx / rx2
        c = (cx * cx) / rx2 + (dy * dy) / ry2 - 1.0
        D2 = b * b - 4.0 * a * c

        if D2 >= 0:
            D = math.sqrt(D2)
            xres1 = (- b + D) / (2.0 * a)
            if not checkInterval or ((xres1 <= x0 and xres1 >= x1) or (xres1 <= x1 and xres1 >= x0)):
                point1 = Point(xres1, y, 0.0)
                results.append(point1)
            if D2 > tolerance:
                xres2 = (- b - D) / (2.0 * a)
                if not checkInterval or ((xres2 <= x0 and xres2 >= x1) or (xres2 <= x1 and xres2 >= x0)):
                    point2 = Point(xres2, y, 0.0)
                    results.append(point2)

    return results

def GetBoundingBoxIntersectionsWithEllipse(boundingBox, rx, ry, cx, cy, checkInterval):
    intersections = []
    intersections += LineEllipseIntersection(boundingBox.minPoint.X, boundingBox.minPoint.Y, boundingBox.minPoint.X, boundingBox.maxPoint.Y, rx, ry, cx, cy, checkInterval)
    intersections += LineEllipseIntersection(boundingBox.maxPoint.X, boundingBox.minPoint.Y, boundingBox.maxPoint.X, boundingBox.maxPoint.Y, rx, ry, cx, cy, checkInterval)
    intersections += LineEllipseIntersection(boundingBox.minPoint.X, boundingBox.minPoint.Y, boundingBox.maxPoint.X, boundingBox.minPoint.Y, rx, ry, cx, cy, checkInterval)
    intersections += LineEllipseIntersection(boundingBox.minPoint.X, boundingBox.maxPoint.Y, boundingBox.maxPoint.X, boundingBox.maxPoint.Y, rx, ry, cx, cy, checkInterval)
    return intersections

def GetPolygonRotationAngle(polygon):
    import copy
    from shapely import affinity
    def bbArea(bounds):
        return (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])

    curBoundArea = bbArea(polygon.bounds)
    bestBoundArea = curBoundArea

    pl = copy.deepcopy(polygon)
    bestAngle = 0
    bestPl = pl

    for angle in range(91):
        curPl = affinity.rotate(pl, angle - 45, origin="centroid")
        area = bbArea(curPl.bounds)
        if area < bestBoundArea:
            bestBoundArea = area
            bestAngle = angle - 45
            bestPl = curPl
    return (bestAngle, bestPl)

def GetNearestPointOnAreaBound(point, polygons):
    """Gets a projection of shapely.geometry.Point on a set of shapely.geometry.Polygon
       returns nearest point on polygons border
    """
    from shapely.geometry import LinearRing
    pols = GetPurePolygonsFromMixedArray(polygons)

    bestPolyRing = None
    bestDist = np.inf
    for poly in pols:
        pol_ext = LinearRing(poly.exterior.coords)
        d = pol_ext.project(point)
        if d < bestDist:
            bestDist = d
            bestPolyRing = pol_ext
    p = bestPolyRing.interpolate(bestDist)
    closest_point_coords = list(p.coords)[0]
    return closest_point_coords

def GetDistanceToAreaBound(point, polygons):
    from shapely.geometry import LinearRing
    pols = GetPurePolygonsFromMixedArray(polygons)

    bestDist = np.inf
    for poly in pols:
        pol_ext = LinearRing(poly.exterior.coords)
        d = pol_ext.project(point)
        if d < bestDist:
            bestDist = d
    
    return bestDist

def GetPurePolygonsFromMixedArray(polygons):
    from shapely.geometry import Polygon, GeometryCollection, MultiPolygon
    pols = []
    combined = []
    for obj in polygons:
        if isinstance(obj, Polygon):
            pols.append(obj)
        elif isinstance(obj, MultiPolygon) or isinstance(obj, GeometryCollection):
            combined.append(obj)

    while combined:
        for obj in combined[0].geoms:
            if isinstance(obj, Polygon):
                pols.append(obj)
            elif isinstance(obj, MultiPolygon) or isinstance(obj, GeometryCollection):
                combined.append(obj)
        combined.pop(0)
    return pols

def GenerateEllipseCoords(x0, y0, a, b, angle, n=100):
    import numpy as np
    t = np.linspace(0, 2*np.pi, n, endpoint=False)
    st = np.sin(t)
    ct = np.cos(t)
    result = []
    angler = np.deg2rad(angle)
    sa = np.sin(angler)
    ca = np.cos(angler)
    p = np.empty((n, 2))
    p[:, 0] = x0 + a * ca * ct - b * sa * st
    p[:, 1] = y0 + a * sa * ct + b * ca * st
    result = p
    result = [(el[0], el[1]) for el in result]
    return result

def NthPointOnEllipse(x0, y0, a, b, angle, n, total, shift=0):
    import numpy as np
    t = n * ((2 * np.pi) / total) + np.deg2rad(shift)
    st = np.sin(t)
    ct = np.cos(t)
    result = []
    angler = np.deg2rad(angle)
    sa = np.sin(angler)
    ca = np.cos(angler)
    result = (x0 + a * ca * ct - b * sa * st, y0 + a * sa * ct + b * ca * st)
    return result

def CreateEllipsePolygon(x0, y0, a, b, angle, n=100):
    coords = GenerateEllipseCoords(x0, y0, a, b, angle, n)
    return Polygon(coords)

def unitVector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angleBetween(v1, v2):
    """ Returns the angle in radians between vectors "v1" and "v2"::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unitVector(v1)
    v2_u = unitVector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle

def pointsToMultiPolygon(regs):
    """
    Returns polygon from set of points
    params:
    regs - list of points
    """

    region = []
    for reg in regs:
        coords = [(pnt.X, pnt.Y) for pnt in reg]
        try:
            pol = Polygon(coords)
            region.append(pol)
        except:
            pass

    return MultiPolygon(region) if len(region) > 0 else None

def GetDistanceBetweenPoints(p1, p2):
        """ 
        Returns distance between two points 
        params:
        p1 - first point
        p2 - second point
        """
        a = np.array((p1.X ,p1.Y, p1.Z))
        b = np.array((p2.X ,p2.Y, p2.Z))
        return np.linalg.norm(a-b)


def MakeCircle(points):
    """
    Returns the smallest circle that encloses all the given points. A circle is a triple of floats (center x, center y, radius)
    params:
    points - set of given points
    """
    c = None
    for (i, p) in enumerate(points):
        if c is None or not _isInCircle(c, p):
            c = _makeCircleOnePoint(points[0 : i + 1], p)
    return c


def _makeCircleOnePoint(points, p):
    """ 
    Makes circle based on one point 
    params:
    points - set of given points
    p - point
    """
    c = (p[0], p[1], 0.0)
    for (i, q) in enumerate(points):
        if not _isInCircle(c, q):
            if c[2] == 0.0:
                c = _makeDiameter(p, q)
            else:
                c = _makeCircleTwoPoints(points[0 : i + 1], p, q)
    return c


def _makeCircleTwoPoints(points, p, q):
    """
    Makes circle based on two points
    params:
    points - set of given points
    p - first point
    q - second point
    """
    diameter = _makeDiameter(p, q)
    if all(_isInCircle(diameter, r) for r in points):
        return diameter
    
    left = None
    right = None
    for r in points:
        cross = _crossProduct(p[0], p[1], q[0], q[1], r[0], r[1])
        c = _makeCircumcircle(p, q, r)
        if c is None:
            continue
        elif cross > 0.0 and (left is None or _crossProduct(p[0], p[1], q[0], q[1], c[0], c[1]) > _crossProduct(p[0], p[1], q[0], q[1], left[0], left[1])):
            left = c
        elif cross < 0.0 and (right is None or _crossProduct(p[0], p[1], q[0], q[1], c[0], c[1]) < _crossProduct(p[0], p[1], q[0], q[1], right[0], right[1])):
            right = c
    return left if (right is None or (left is not None and left[2] <= right[2])) else right


def _makeCircumcircle(p0, p1, p2):
    """
    Mathematical algorithm from Wikipedia: Circumscribed circle
    Makes circle based on three points
    params:
    p0 - first point
    p1 - second point
    p2 - third point
    """
    ax = p0[0]; ay = p0[1]
    bx = p1[0]; by = p1[1]
    cx = p2[0]; cy = p2[1]
    d = (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) * 2.0
    if d == 0.0:
        return None
    x = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    y = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (x, y, math.hypot(x - ax, y - ay))


def _makeDiameter(p0, p1):
    """
    Makes diameter based on two points
    params:
    p0 - first point
    p1 - second point
    """
    return ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, math.hypot(p0[0] - p1[0], p0[1] - p1[1]) / 2.0)


_EPSILON = 1e-12

def _isInCircle(c, p):
    """
    Checks if point is in circle
    params:
    c - circle
    p - point
    """
    return c is not None and math.hypot(p[0] - c[0], p[1] - c[1]) < c[2] + _EPSILON

def _crossProduct(x0, y0, x1, y1, x2, y2):
    """
    Returns twice the signed area of the triangle defined by (x0, y0), (x1, y1), (x2, y2)
    params:
    x0, y0, x1, y1, x2, y2: three pairs of points
    """
    return (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)