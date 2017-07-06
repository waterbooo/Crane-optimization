import math, os, sys
import numpy as np
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(__filePath, "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from .CraneData import *
from BLGeometry import GeometryUtils

class MobileCraneData(CraneData):
    """Structure representing crane data:
        - speeds
        - capacities
        - measures
    """
    """
    The unit is min and inch
    """
    def __init__(self, craneObject):
        specifications = craneObject["metadata"]["specifications"]

        metadataSpeeds = specifications["speeds"]
        metadataMovement=specifications["movement"]

        # crane moving speed
        self.movingSpeed=metadataMovement["speed"]

        # time for the crane to settle down the supports when move to a new place
        self.settleDownTime=metadataMovement["settleDownTime"]

        # time for the crane to take down supports when it moves
        self.takeDownTime=metadataMovement["takeDownTime"]

        # Boom Length velocity in feet per minute
        self.boomLengthVelocity = metadataSpeeds["boomLength"]["speed"] 

        # Boom Angle velocity in radians per minute
        self.boomAngleVelocity = metadataSpeeds["boomAngle"]["speed"]

        # Slew velocity in radians per minute
        self.slewVelocity = metadataSpeeds["slew"]["speed"]

        # Slew velocity in radians per minute
        self.hookVelocity = metadataSpeeds["hook"]["speed"]
        
        # boom configuration and capacity
        self.boomConfig=specifications["limitations"]["boomConfig-capacity"]
        self.boomConfig={float(key):value for key, value in self.boomConfig.items()}
        
        self.boomLength=None
        self.maxLength=self.getMaxLength()
        self.maxRadius=self.getMaxRadius()

        return super().__init__(craneObject)
    
    # Inherited methods
    def getMaxLength(self):
        """find the max boom length"""
        maxBoomLength=np.max(list(self.boomConfig.keys()))
        return maxBoomLength

    def getMinLength(self):
        return 0.0

    def getMaxRadius(self):
        """find the max working radius"""
        maxBoomLength=np.max(list(self.boomConfig.keys()))
        return np.max(self.boomConfig[maxBoomLength]["workingRadius"])

    def getMinRadius(self):
        """Takes weight of bar, and given the length of boom, find the minimum working radius for the crane"""
        """assuming at current boom length"""
        craneData=self.boomConfig[self.getRoundBoomLength()]
        minRadius = np.min(craneData["workingRadius"])
        return minRadius

    def getMaxCapacityForRadius(self, radius):
        """For the crane we are using now, the capacity is enough for lifting the panels"""
        """assume that boom length has been fixed"""
        return 5000;

    def getMaxRadiusForCapacity(self, capacity):
        """Takes weight of bar, and given the length of boom, find the maximum working radius for the crane"""
        """assuming at current boom length"""
        craneData=self.boomConfig[self.getRoundBoomLength()]

        maxRadius=np.max([craneData["workingRadius"][i] for i in range(len(craneData["workingRadius"])) if craneData["capacity"][i]>capacity])
        return maxRadius

    def getSpeedForCapacity(self,capacity):
        """ units: m/s, current value is the best guess for rotation speed """
        return 5

    def getSlewVelocity(self):
        return self.slewVelocity

    def getBoomAngleVelocity(self):
        return self.boomAngleVelocity

    def getBoomLengthVelocity(self):
        return self.boomLengthVelocity

    # Mobile crane specific methods
    def setBoomLength(self,boomLength=None): 
        """set boom length"""
        if boomLength is None:
            self.boomLength=self.maxLength
        else:
            self.boomLength=boomLength
        return

    def setBoomAngle(self,boomAngle): 
        """set boom Angle"""
        self.boomAngle=boomAngle
        return

    def getRoundBoomLength(self):
        if self.boomLength is not None:
             return np.min([len for len in self.boomConfig.keys() if len >= self.boomLength])
        else:
             print ("boom Length is not set or it is illegal, it is set as the longest boom length by default")
             return np.max(list(self.boomConfig.keys()))

    def getMovingTime(self, distance):
        t= float(distance)/self.movingSpeed + self.takeDownTime + self.settleDownTime
        return t