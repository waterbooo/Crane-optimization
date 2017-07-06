import sys, os 
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(os.path.split(os.path.split(__filePath)[0])[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from BLGeometry import GeometryUtils
from BLGeometry.PrefabGeometry import Point
from shapely.geometry import MultiPolygon

class SupplyRegionPosition(object):
    """Optimization functions for supply region definition"""
    pass

