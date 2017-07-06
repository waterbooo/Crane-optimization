import unittest
from shapely import affinity
from shapely.geometry import Polygon, MultiPolygon
import math, os, sys
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(os.path.split(__filePath)[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)
from BLGeometry import GeometryUtils

class Test_test_bounding_polygons(unittest.TestCase):
    def test_simple_rotation(self):
        p1 = Polygon([(0,0), (0,1), (1,1), (1,0), (0,0)])
        p2 = Polygon([(2,0), (2,1), (3,1), (3,0), (2,0)])
        p1rotated = affinity.rotate(p1, -23, origin="centroid")
        angle = GeometryUtils.GetPolygonRotationAngle(p1rotated)[0]
        self.assertAlmostEqual(angle, 23)
        mp = MultiPolygon([p1, p2])
        mprotated = affinity.rotate(mp, 10, origin="centroid")
        mpangle = GeometryUtils.GetPolygonRotationAngle(mprotated)[0]
        self.assertAlmostEqual(mpangle, -10)

if __name__ == "__main__":
    unittest.main()
