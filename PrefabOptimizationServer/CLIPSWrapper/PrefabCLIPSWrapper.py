import os, platform, struct, ctypes, tempfile, uuid
from CLIPSCommonStructures import *

SysNameWindows = "Windows"
SysNameLinux = "Linux"

class PrefabCLIPSWrapper(object):
    """Provides functionality for loading CLIPS library and running analysis"""

    def __init__(self, **kwargs):
        self.__sysName = platform.system()
        self.__pythonPlatform = struct.calcsize("P") * 8
        filePath = os.path.dirname(os.path.realpath(__file__))
        if self.__sysName == SysNameWindows:
            if self.__pythonPlatform == 32:
                self.__clipsLib = ctypes.cdll.LoadLibrary(filePath + "\\..\\Libs\\CLIPS\\CLIPSDynamic32.dll")
            elif self.__pythonPlatform == 64:
                self.__clipsLib = ctypes.cdll.LoadLibrary(filePath + "\\..\\Libs\\CLIPS\\CLIPSDynamic64.dll")
            
            self.__CreateEnv = getattr(self.__clipsLib, "__CreateEnvironment")
            self.__DestroyEnv = getattr(self.__clipsLib, "__DestroyEnvironment")
            self.__EnvClear = getattr(self.__clipsLib, "__EnvClear")
            self.__EnvReset = getattr(self.__clipsLib, "__EnvReset")
            self.__EnvLoad = getattr(self.__clipsLib, "__EnvLoad")
            self.__EnvRun = getattr(self.__clipsLib, "__EnvRun")
            self.__EnvBuild = getattr(self.__clipsLib, "__EnvBuild")

            self.__EnvEval = getattr(self.__clipsLib, "__EnvEval")
            self.__EnvEval.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
            self.__EnvEval.restype = ctypes.c_int

            self.__EnvIncrementFactCount = getattr(self.__clipsLib, "__EnvIncrementFactCount")
            self.__EnvDecrementFactCount = getattr(self.__clipsLib, "__EnvDecrementFactCount")
            self.__EnvIncrementInstanceCount = getattr(self.__clipsLib, "__EnvIncrementInstanceCount")
            self.__EnvDecrementInstanceCount = getattr(self.__clipsLib, "__EnvDecrementInstanceCount")

            self.__EnvGetFactSlot = getattr(self.__clipsLib, "__EnvGetFactSlot")
            self.__EnvGetFactSlot.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
            self.__EnvGetFactSlot.restype = ctypes.c_int

            self.__EnvFactIndex = getattr(self.__clipsLib, "__EnvFactIndex")
            self.__EnvGetInstanceName = getattr(self.__clipsLib, "__EnvGetInstanceName")

        elif self.__sysName == SysNameLinux:
            if self.__pythonPlatform == 32:
                print("Linux 32 bit is not supported")
                return
            elif self.__pythonPlatform == 64:
                self.__clipsLib = ctypes.cdll.LoadLibrary(filePath + "/../Libs/CLIPS/libclips64.so")
            self.__CreateEnv = getattr(self.__clipsLib, "CreateEnvironment")
            self.__DestroyEnv = getattr(self.__clipsLib, "DestroyEnvironment")
            self.__EnvClear = getattr(self.__clipsLib, "EnvClear")
            self.__EnvReset = getattr(self.__clipsLib, "EnvReset")
            self.__EnvLoad = getattr(self.__clipsLib, "EnvLoad")
            self.__EnvRun = getattr(self.__clipsLib, "EnvRun")
            self.__EnvBuild = getattr(self.__clipsLib, "EnvBuild")

            self.__EnvEval = getattr(self.__clipsLib, "EnvEval")
            self.__EnvEval.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(dataObject)]
            self.__EnvEval.restype = ctypes.c_int

            self.__EnvIncrementFactCount = getattr(self.__clipsLib, "EnvIncrementFactCount")
            self.__EnvDecrementFactCount = getattr(self.__clipsLib, "EnvDecrementFactCount")
            self.__EnvIncrementInstanceCount = getattr(self.__clipsLib, "EnvIncrementInstanceCount")
            self.__EnvDecrementInstanceCount = getattr(self.__clipsLib, "EnvDecrementInstanceCount")

            self.__EnvGetFactSlot = getattr(self.__clipsLib, "EnvGetFactSlot")
            self.__EnvGetFactSlot.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(dataObject)]
            self.__EnvGetFactSlot.restype = ctypes.c_int

            self.__EnvFactIndex = getattr(self.__clipsLib, "EnvFactIndex")
            self.__EnvGetInstanceName = getattr(self.__clipsLib, "EnvGetInstanceName")

            # Custom methods for Linux
            self.__EnvLoadFacts = getattr(self.__clipsLib, "EnvLoadFacts")
            self.__EnvLoadFacts.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            self.__EnvLoadFacts.restype = [ctypes.c_int]

        # Set argtypes and restype for common methods
        self.__CreateEnv.restype = ctypes.c_void_p
        
        self.__DestroyEnv.argtypes = [ctypes.c_void_p]

        self.__EnvClear.argtypes = [ctypes.c_void_p]

        self.__EnvReset.argtypes = [ctypes.c_void_p]
            
        self.__EnvLoad.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.__EnvLoad.restype = ctypes.c_int

        self.__EnvRun.argtypes = [ctypes.c_void_p, ctypes.c_longlong]
        self.__EnvRun.restype = ctypes.c_longlong

        self.__EnvBuild.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.__EnvBuild.restype = ctypes.c_int

        self.__EnvIncrementFactCount.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.__EnvDecrementFactCount.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.__EnvIncrementInstanceCount.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.__EnvDecrementInstanceCount.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.__EnvFactIndex.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.__EnvFactIndex.restype = ctypes.c_longlong

        self.__EnvGetInstanceName.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.__EnvGetInstanceName.restype = ctypes.c_char_p
        return super().__init__(**kwargs)

    def __isOnWindows(self):
        return self.__sysName == SysNameWindows

    def __isOnLinux(self):
        return self.__sysName == SysNameLinux

    def CreateEnv(self):
        """Creates CLIPS environment. Should be paired with DestroyEnv method"""
        return self.__CreateEnv()

    def DestroyEnv(self, env):
        """Destroys CLIPS environment"""
        return self.__DestroyEnv(env)

    def EnvLoad(self, env, ruleFile):
        """Loads rules, functions, templates, deffacts etc.
           Note: Does not load fact assertions.
        """
        envLoad = getattr(self.__clipsLib, "__EnvLoad")
        envLoad.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        return envLoad(env, ruleFile)

    def EnvLoadFacts(self, env, factsFile):
        """Loads facts into environment.
           Note: Facts are not kept after EnvReset
        """
        try:
            if self.__isOnWindows():
                # There is no method for loading files in win dll
                # So, read facts text first
                srcFile = open(factsFile, "r")
                facts = srcFile.read()
                srcFile.close()

                # Create a temp file
                tmpFile = tempfile.NamedTemporaryFile("w+t", delete=False)
                
                # Write deffacts construct 
                tmpId = str(uuid.uuid4())
                tmpFile.write("(deffacts " + tmpId + "\n")

                # Write facts
                tmpFile.write(facts)

                # Close deffacts construct
                tmpFile.write("\n)")

                # Close tmp file
                tmpFile.close()

                # Load deffacts construct into environment
                self.__EnvLoad(env, tmpFile.name.encode("UTF-8"))

                # Reset environment to get facts in
                self.__EnvReset(env)

                # Delete temp file
                os.remove(tmpFile.name)
            else:
                # Load facts into environment
                self.__EnvLoadFacts(env, factsFile.encode("UTF-8"))
            return 1
        except Exception as e:
            print(e)
            return 0

    def EnvRun(self, env):
        """Executes CLIPS running rules on existing facts"""
        return self.__EnvRun(env, -1)
 
    def EnvReset(self, env):
        """Resets CLIPS environment
           Reset clears all facts, creates initial fact, recreates facts defined under deffacts.
        """
        return self.__EnvReset(env)

    def EnvClear(self, env):
        """Clears CLIPS environment from all facts, rules and other constructs"""
        return self.__EnvClear(env)

    def EnvBuild(self, env, buildStr):
        """Builds a string into environment.
           e.g. it can contain rule definition
        """
        return self.__EnvBuild(env, buildStr)

    def EnvEval(self, env, evalStr):
        """Runs evaluation expression"""
        outObj = dataObject()
        self.__EnvEval(env, evalStr, ctypes.byref(outObj))
        return outObj

    def EnvGetFactSlot(self, env, fact, slotName):
        """Gets a slot value from a fact"""
        outObj = dataObject()
        self.__EnvGetFactSlot(env, fact, slotName, ctypes.byref(outObj))
        return outObj

    def EnvFactIndex(self, env, fact):
        """Gets index of fact in environment"""
        return self.__EnvFactIndex(env, fact)
    