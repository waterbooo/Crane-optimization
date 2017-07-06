import math, os, sys
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(__filePath, "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)
from BLGeometry import GeometryUtils

class CraneData:
    """Structure representing base crane data"""

    def __init__(self, craneObject):
        specifications = craneObject["metadata"]["specifications"]
        if "base-size" not in specifications:
            # Base rectangle measurements, feet
            self.baseSizeX = 10.0
            self.baseSizeY = 10.0
        else:
            self.baseSizeX = specifications["base-size"]["X"]
            self.baseSizeY = specifications["base-size"]["Y"]

        # jib simultaneous movement parameter (alpha) - constant, coefficient
        self.alpha = 0.25

        # hook simultaneous movement parameter (beta) - constant = 1.0, coefficient
        self.beta = 1.0

        self.maxLength = self.getMaxLength() # max length of jib, ft
        self.accessingCircle = GeometryUtils.CreateEllipsePolygon(0, 0, self.maxLength, self.maxLength, 0)
        self.accessingCircleForModel = GeometryUtils.CreateEllipsePolygon(0, 0, self.maxLength, self.maxLength, 0)

        return super().__init__()

    def getMaxLength(self):
        pass

    def getMinLength(self):
        pass

    def getMaxRadius(self):
        pass

    def getMinRadius(self):
        pass

    def getMaxCapacityForRadius(self, length):
        pass

    def getMaxRadiusForCapacity(self, capacity):
        pass

    def getSpeedForCapacity(self, capacity):
        pass

    def getSlewVelocity(self):
        pass

    def getBoomAngleVelocity(self):
        pass

    def getBoomLengthVelocity(self):
        pass
