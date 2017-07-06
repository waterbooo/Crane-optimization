import os, sys, json
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(os.path.split(os.path.split(__filePath)[0])[0], "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from BLGeometry.PrefabGeometry import Point

class UtilsModelParse(object):
    """Utilities for parsing models from JSON"""
    __KeyPointX = "X"
    __KeyPointx = "x"
    __KeyPointY = "Y"
    __KeyPointy = "y"
    __KeyPointZ = "Z"
    __KeyPointz = "z"

    def GetCheckExist(json, key, default=None):
        """Checks whether key exists in json object and returns value for it if exists
           otherwise 'default' is returned
        """
        if key in json:
            return json[key]
        else:
            return default

    def GetCheckExistNested(json, keys, default=None):
        """Checks whether key exists in json object and returns value for it if exists
           otherwise 'default' is returned
        """
        if not isinstance(keys, list):
            if keys in json:
                return json[keys]
            else:
                return default
        else:
            nestedJSON = json
            for key in keys:
                if key in nestedJSON:
                    nestedJSON = json[key]
                else:
                    return default
            return nestedJSON

    
    def GetCheckExistStructure(json, key, getter, default):
        """Checks whether key exists in json object and applies custom getter to it if exists
           otherwise calls 'default()'
        """
        if key in json:
            return getter(json[key])
        else:
            return default()

    def PointFromArray(pointJSON):
        """Loads point structure from JSON array"""
        x = 0.0
        y = 0.0
        z = 0.0
        if len(pointJSON) > 0:
            x = pointJSON[0]
        if len(pointJSON) > 1:
            y = pointJSON[1]
        if len(pointJSON) > 2:
            z = pointJSON[2]
        return Point(x, y, z)

    def PointFromXYZ(pointJSON):
        """Loads point structure from XYZ JSON structure"""
        ump = UtilsModelParse
        x = 0.0
        y = 0.0
        z = 0.0
        x = ump.GetCheckExist(pointJSON, ump.__KeyPointX, 0.0)
        if x == 0.0:
            x = ump.GetCheckExist(pointJSON, ump.__KeyPointx, 0.0)
        y = ump.GetCheckExist(pointJSON, ump.__KeyPointY, 0.0)
        if y == 0.0:
            y = ump.GetCheckExist(pointJSON, ump.__KeyPointy, 0.0)
        z = ump.GetCheckExist(pointJSON, ump.__KeyPointZ, 0.0)
        if z == 0.0:
            z = ump.GetCheckExist(pointJSON, ump.__KeyPointz, 0.0)
        return Point(x, y, z)
