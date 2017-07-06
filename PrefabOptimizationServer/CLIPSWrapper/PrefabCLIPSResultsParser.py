from CLIPSCommonStructures import *
from ctypes import *

class PrefabCLIPSDataObjectsParser(object):
    """Provides functionality for parsing of different CLIPS returned objects"""

    def GetMFValue(self, mfObject, index):
        """Gets index-th value pointer from CLIPS multifield object

           Returns: ctypes.c_void_p pointer to a data. Use type to get info from the pointer
        """
        target = mfObject
        if not isinstance(target, multifield):
            target = ctypes.cast(target, multifield)
        return ctypes.cast(target.theFields, ctypes.POINTER(field))[index - 1].value

    def GetMFType(self, mfObject, index):
        """Gets index-th type for CLIPS multifield object

           Returns: ctypes.c_ushort value. Use dataTypes object to get type value
        """
        target = mfObject
        if not isinstance(target, multifield):
            target = ctypes.cast(target, multifield)
        return ctypes.cast(target.theFields, ctypes.POINTER(field))[index - 1].type

    def DOPToString(self, target):
        """Gets string value from a void pointer"""

        return self.GetStringValue(target.value)

    def DOPToDouble(self, target):
        """Gets float value from a void pointer"""
        return self.GetFloatValue(target.value)
    
    def DOPToFloat(self, target):
        """Gets float value from a void pointer"""
        return self.GetFloatValue(target.value)    

    def DOPToLong(self, target):
        """Gets long value from a void pointer"""
        return self.GetLongValue(target.value)    

    def DOPToInteger(self, target):
        """Gets int value from a pointer to dataObject"""
        return self.GetIntegerValue(target.value)

    def GetIntegerValue(self, value):
        """Gets int value from void pointer"""
        return int(ctypes.cast(value, ctypes.POINTER(integerHashNode)).contents.contents)

    def GetLongValue(self, value):
        """Gets long value from void pointer"""
        return ctypes.cast(value, ctypes.POINTER(integerHashNode)).contents.contents

    def GetFloatValue(self, value):
        """Gets float value from void pointer"""
        return ctypes.cast(value, ctypes.POINTER(floatHashNode)).contents.contents

    def GetStringValue(self, value):
        """Gets string value from void pointer"""
        return ctypes.cast(value, ctypes.POINTER(symbolHashNode)).contents.contents.decode("utf-8")

    def GetMultifieldValue(self, value):
        """Gets an object under multifield value as an array of objects
           returns: array of (object, type) values
        """
        # Get multifield object from pointer
        mfRes = cast(value, POINTER(multifield)).contents
        resObjects = []

        # Parse each field object
        for i in range(mfRes.multifieldLength):
            t = self.GetMFType(mfRes, i + 1)
            v = self.GetMFValue(mfRes, i + 1)
            if CheckForCLIPSSymbolType(t):
                resObjects.append((self.GetStringValue(v), t))
            elif t == kCLIPSDTFloatNum:
                resObjects.append((self.GetFloatValue(v), t))
            elif t == kCLIPSDTIntegerNum:
                resObjects.append((self.GetLongValue(v), t))
            else:
                resObjects.append((v, t))    
        return resObjects
