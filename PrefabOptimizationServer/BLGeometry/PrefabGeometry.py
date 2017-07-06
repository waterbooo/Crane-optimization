import math

class Point:
    FreeId = 0
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.X = x
        self.Y = y
        self.Z = z
    
    def lateralDistanceTo(self, otherPoint):
        return math.sqrt(math.pow(self.X - otherPoint.X, 2) + math.pow(self.Y - otherPoint.Y, 2))

    def verticalDistanceTo(self, otherPoint):
        return math.fabs(self.Z - otherPoint.Z)

    def distanceTo(self, otherPoint):
        return math.sqrt(math.pow(self.X - otherPoint.X, 2) + math.pow(self.Y - otherPoint.Y, 2) + math.pow(self.Z - otherPoint.Z, 2))

    def vectorTo(self, otherPoint):
        return (otherPoint.X - self.X, otherPoint.Y - self.Y)

    def GetClipsSlots(self, options=None):
        slots = "(Id " + str(Point.FreeId) + ") "
        Point.FreeId += 1
        slots += "(X " + str(self.X) + ") "
        slots += "(Y " + str(self.X) + ") "
        return slots

    def GetClipsFacts(self, options=None):
        fact = "(Point "
        fact += self.GetClipsSlots(options)
        fact += ")"
        return fact
