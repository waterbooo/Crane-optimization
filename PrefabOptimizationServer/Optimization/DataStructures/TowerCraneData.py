import math, os, sys
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(__filePath, "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)
from .CraneData import *
from BLGeometry import GeometryUtils

class TowerCraneData(CraneData):
    """Structure representing crane data:
        - speeds
        - capacities
        - measures
    """
    def __init__(self, craneObject):
        specifications = craneObject["metadata"]["specifications"]

        metadataSpeeds = specifications["speeds"]
        # trolley velocity in feet per minute
        self.trolleyVelocity = metadataSpeeds["trolley"]["speed"] 

        # jib radial velocity in radians per minute
        self.jibRadialVelocity = metadataSpeeds["rotation"]["speed"]

        # maximum crane capacities dependent on distance to supply/demand 
        # distance is the key: feet
        # value is capacity: pounds
        self.maxCapacities = {}
        self.lengths = []
        for length, value in specifications["limitations"]["radius-capacity"].items():
            self.maxCapacities[float(length)] = value # feet to pounds
            self.lengths.append(int(length))
        self.lengths.sort()

        # hook vertical speed dependent on capacity
        # key: capacity, pounds
        # value: speed, feet per minute
        self.capacitySpeeds = {}
        self.capacitiesForSpeed = []
        for capacity, value in metadataSpeeds["hook"]["capacity-speed"].items():
            self.capacitySpeeds[float(capacity)] = value # feet per minute
            self.capacitiesForSpeed.append(float(capacity))
        self.capacitiesForSpeed.sort()

        return super().__init__(craneObject)


    def getMaxLength(self):
        """Returns maximum crane length, ft"""
        return self.lengths[len(self.lengths) - 1]

    def getMinLength(self):
        """Returns minimum crane length, ft"""
        return 0.0

    def getMaxRadius(self):
        """Returns maximum working radius, ft"""
        return self.getMaxLength()

    def getMinRadius(self):
        """Returns minimum working radius, ft"""
        return self.getMinLength()
    
    def getMaxCapacityForRadius(self, length):
        """
        Takes distance, returns maximum possible capacity for it
        
        params:
            length - distance to element, ft

        returns:
            maximum capacity of crane for the given distance, lbs
        """
        found = False
        left = 0
        right = len(self.lengths) - 1
        mid = len(self.lengths) // 2
        while found == False:
            if right - left > 1:
                if length > self.lengths[mid]:
                    left = mid
                else:
                    right = mid
                mid = (right + left) // 2
            elif left == right:
                return self.maxCapacities[self.lengths[left]]
            else:
                dif1 = math.fabs(length - self.lengths[left])
                dif2 = math.fabs(length - self.lengths[right])
                if dif1 < dif2 :
                    return self.maxCapacities[self.lengths[left]]
                else:
                    return self.maxCapacities[self.lengths[right]]

    def getMaxRadiusForCapacity(self, capacity):
        """
        Takes weight of element, returns maximum distance from crane base to work with the weight

        params:
            capacity - weight of the element(group of elements), lbs

        returns:
            maximum length along the jib for particular crane, which allows to lift the element, ft
        """
        import numpy as np
        maxLength = np.max([len for len in self.maxCapacities if self.maxCapacities[len] >= capacity])
        return maxLength

    def getSpeedForCapacity(self, capacity):
        """
        Takes weight of element, returns lifting speed with the capacity

        params:
            capacity - weight of element(group of elements), lbs

        returns:
            lifting speed for the given capacity, ft/min
        """
        found = False
        left = 0
        right = len(self.capacitiesForSpeed) - 1
        mid = len(self.capacitiesForSpeed) // 2
        while found == False:
            if right - left > 1:
                if capacity > self.capacitiesForSpeed[mid]:
                    left = mid
                else:
                    right = mid
                mid = (right + left) // 2
            elif left == right:
                return self.capacitySpeeds[self.capacitiesForSpeed[left]]
            else:
                dif1 = math.fabs(capacity - self.capacitiesForSpeed[left])
                dif2 = math.fabs(capacity - self.capacitiesForSpeed[right])
                if dif1 < dif2 :
                    return self.capacitySpeeds[self.capacitiesForSpeed[left]]
                else:
                    return self.capacitySpeeds[self.capacitiesForSpeed[right]]

    def getSlewVelocity(self):
        """
        returns jib radial velocity, rad/min
        """
        return self.jibRadialVelocity

    def getBoomAngleVelocity(self):
        return 1.0

    def getBoomLengthVelocity(self):
        """
        returns translation speed along the jib, ft/min
        """
        return self.trolleyVelocity