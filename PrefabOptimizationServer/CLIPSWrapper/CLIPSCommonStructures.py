import ctypes

class dataObject(ctypes.Structure):
    """Generic CLIPS data object returned from EnvEval or any GetFact/GetSlot method"""
    pass

dataObject._fields_ = [("supplementalInfo", ctypes.c_void_p),
                  ("type", ctypes.c_ushort),
                  ("value", ctypes.c_void_p),
                  ("begin", ctypes.c_long),
                  ("end", ctypes.c_long),
                  ("next", ctypes.POINTER(dataObject))]

class field(ctypes.Structure):
    """Part of multifield. Can be anything. Key to decode is 'type' field"""
    _fields_ = [("type", ctypes.c_ushort),
                ("value", ctypes.c_void_p)]

class multifield(ctypes.Structure):
    """Set of fields. 
       Number of fields defined by 'multifieldLength' property.
       Data is stored under 'theFields'.

       Note: 'theFields' is declared as an array of length 1, but it is a pointer 
             with 'multifieldLength' elements under it. To get data cast array to a pointer
             and use indexing. It doesn't work if specify pointer at once.
    """
    pass

multifield._fields_ = [("busyCount", ctypes.c_uint),
                       ("multifieldLength", ctypes.c_long),
                       ("next", ctypes.POINTER(multifield)),
                       ("theFields", field * 1)]

class symbolHashNode(ctypes.Structure):
    """String or Symbol object
       Data is stored under 'contents'
    """
    pass

symbolHashNode._fields_ = [("next", ctypes.POINTER(symbolHashNode)),
                           ("count", ctypes.c_long),
                           ("permanent", ctypes.c_uint, 1),
                           ("markedEphemeral", ctypes.c_uint, 1),
                           ("neededSymbol", ctypes.c_uint, 1),
                           ("bucket", ctypes.c_uint, 29),
                           ("contents", ctypes.c_char_p)
                           ]

class floatHashNode(ctypes.Structure):
    """Float object
       Data is stored under 'contents'
    """
    pass

floatHashNode._fields_ = [("next", ctypes.POINTER(floatHashNode)),
                           ("count", ctypes.c_long),
                           ("permanent", ctypes.c_uint, 1),
                           ("markedEphemeral", ctypes.c_uint, 1),
                           ("neededSymbol", ctypes.c_uint, 1),
                           ("bucket", ctypes.c_uint, 29),
                           ("contents", ctypes.c_double)
                           ]

class integerHashNode(ctypes.Structure):
    """Integer object
       Data is stored under 'contents'
    """
    pass

integerHashNode._fields_ = [("next", ctypes.POINTER(integerHashNode)),
                           ("count", ctypes.c_long),
                           ("permanent", ctypes.c_uint, 1),
                           ("markedEphemeral", ctypes.c_uint, 1),
                           ("neededSymbol", ctypes.c_uint, 1),
                           ("bucket", ctypes.c_uint, 29),
                           ("contents", ctypes.c_longlong)
                           ]


# CLIPS common data types
dataTypes = {
        0: "FLOAT",
        1: "INTEGER",
        2: "SYMBOL",
        3: "STRING",
        4: "MULTIFIELD",
        5: "EXTERNAL_ADDRESS",
        6: "FACT_ADDRESS",
        7: "INSTANCE_ADDRESS",
        8: "INSTANCE_NAME"
    }

# Constants for CLIPS type names
kCLIPSDTFloatStr = "FLOAT"
kCLIPSDTIntegerStr = "INTEGER"
kCLIPSDTSymbolStr = "SYMBOL"
kCLIPSDTStringStr = "STRING"
kCLIPSDTMultifieldStr = "MULTIFIELD"
kCLIPSDTExtAddrStr = "EXTERNAL_ADDRESS"
kCLIPSDTFactAddrStr = "FACT_ADDRESS"
kCLIPSDTInstAddrStr = "INSTANCE_ADDRESS"
kCLIPSDTInstNameStr = "INSTANCE_NAME"

# Constants for CLIPS type int markers
kCLIPSDTFloatNum = 0
kCLIPSDTIntegerNum = 1
kCLIPSDTSymbolNum = 2
kCLIPSDTStringNum = 3
kCLIPSDTMultifieldNum = 4
kCLIPSDTExtAddrNum = 5
kCLIPSDTFactAddrNum = 6
kCLIPSDTInstAddrNum = 7
kCLIPSDTInstNameNum = 8

def CheckForKnownType(type):
    """Checks whether obtained type is among known ones"""
    return type >= 0 and type <= 8

def CheckForCLIPSSymbolType(type):
    """Checks whether type is string"""
    return type in [kCLIPSDTSymbolNum, kCLIPSDTStringNum]
