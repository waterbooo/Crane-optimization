from PrefabCLIPSResultsParser import *
from PrefabCLIPSWrapper import *
from ctypes import *

class PrefabCLIPSProcessor(object):
    """Combines functionality of wrapper and parser for higher level procedures"""
    def __init__(self, **kwargs):
        self._wrapper = PrefabCLIPSWrapper()
        self._parser = PrefabCLIPSDataObjectsParser()
        self.__BLGatheringFunctionsPrefix = "BLGather"
        return super().__init__(**kwargs)

    @property
    def Wrapper(self):
        """Provides wrapped CLIPS c library interface"""
        return self._wrapper

    @Wrapper.deleter
    def Wrapper(self):
        del self._wrapper

    @property
    def Parser(self):
        """Provides set of methods for getting data from CLIPS returned pointers"""
        return self._parser

    @Parser.deleter
    def Parser(self):
        del self._parser

    @property
    def GatheringFcnPrefix(self):
        """Prefix identifying all fact gathering functions in CLIPS environment"""
        return self.__BLGatheringFunctionsPrefix

    @GatheringFcnPrefix.deleter
    def GatheringFcnPrefix(self):
        del self.__BLGatheringFunctionsPrefix

    def GetDeftemplateSlotNames(self, env, deftemplateName):
        """Gets all slot names for a given deftemplate name"""
        # Get raw values for slot names from environment
        evalRes = self._wrapper.EnvEval(env, ("(deftemplate-slot-names " + deftemplateName + ")").encode("utf-8"))

        # Check for valid answer
        if (CheckForKnownType(evalRes.type) and evalRes.type == kCLIPSDTMultifieldNum):
            names = []

            # Cast result to a multifield value
            mfRes = cast(evalRes.value, POINTER(multifield)).contents

            # Get list of names
            for i in range(mfRes.multifieldLength):
                t = self._parser.GetMFType(mfRes, i + 1)
                v = self._parser.GetMFValue(mfRes, i + 1)
                if t in [kCLIPSDTStringNum, kCLIPSDTSymbolNum]:
                    names.append(self._parser.GetStringValue(v))
            return names
        else:
            return []

    def GetFactContents(self, env, factPtr):
        """Parses fact data from a ponter
            returns: Python object like
                    { 
                        "templateName" : 
                            { 
                                "slotname1" : slotdata1,
                                "slotname2" : slotdata2
                                ...
                                "slotnameN" : slotdataN
                            }
                    }
        """
        # Create result object
        factContents = {}
        
        # Get number of fact from environment
        factNum = self._wrapper.EnvFactIndex(env, factPtr)

        # Get name of fact deftemplate
        evalRes = self._wrapper.EnvEval(env, ("(fact-relation " + str(factNum) + ")").encode("utf-8"))
        templateName = self._parser.DOPToString(evalRes)

        # Get slot names of the template
        slotNames = self.GetDeftemplateSlotNames(env, templateName)

        # Get value for each slot
        slotsContent = {}
        for slotName in slotNames:
            slot = self._wrapper.EnvGetFactSlot(env, factPtr, slotName.encode("utf-8"))
            if slot.type in [kCLIPSDTFloatNum, kCLIPSDTIntegerNum, kCLIPSDTSymbolNum, kCLIPSDTStringNum]:
                slotsContent[slotName] = self.GetSimpleStructureContents(env, slot)["value"]
            elif slot.type == kCLIPSDTMultifieldNum:
                slotsContent[slotName] = self.GetMultifieldContents(env, slot.value)
        
        # Fill the result object
        factContents[templateName] = slotsContent
        return factContents

    def GetMultifieldContents(self, env, multifieldPtr):
        """Gets data from a multifield value"""
        vals = []
        
        # Convert multifield to a set of pairs (value/pointer, type)
        rawVals = self._parser.GetMultifieldValue(multifieldPtr)

        # Get each value contents
        for valPair in rawVals:
            # Built-in types
            if valPair[1] in [kCLIPSDTFloatNum, kCLIPSDTIntegerNum, kCLIPSDTStringNum, kCLIPSDTSymbolNum]:
                vals.append(valPair[0])

            # Fact
            elif valPair[1] == kCLIPSDTFactAddrNum:
                vals.append(self.GetFactContents(env, valPair[0]))

            # Nested multifield value
            elif valPair[1] == kCLIPSDTMultifieldNum:
                vals.append(self.GetMultifieldContents(env, valPair[0]))

        return vals

    def GetSimpleStructureContents(self, env, obj):
        """Gets value for built-in types result"""
        result = {}

        # Float value
        if obj.type == kCLIPSDTFloatNum:
            result["value"] = self._parser.DOPToFloat(obj)
        
        # Long value    
        elif obj.type == kCLIPSDTIntegerNum:
            result["value"] = self._parser.DOPToLong(obj)
        
        # String value    
        elif CheckForCLIPSSymbolType(obj.type):
            result["value"] = self._parser.DOPToString(obj)
        
        return result

    def GetEvalResultContents(self, env, evalRes):
        """Gets contents of CLIPS evaluation result"""
        result = {}

        # Built-in types
        if evalRes.type in [kCLIPSDTFloatNum, kCLIPSDTIntegerNum, kCLIPSDTStringNum, kCLIPSDTSymbolNum]:
            result = self.GetSimpleStructureContents(env, evalRes)
        
        # Facts    
        elif evalRes.type == kCLIPSDTFactAddrNum:
            result = self.GetFactContents(env, evalRes.value)

        # Multifields
        elif evalRes.type == kCLIPSDTMultifieldNum:
            result = self.GetMultifieldContents(env, evalRes.value)

        return result

    def GetDeffunctionNames(self, env):
        """Gets list of all deffunction names defined in CLIPS environment"""
        result = {}

        # Get names list
        evalRes = self._wrapper.EnvEval(env, b"(get-deffunction-list)")

        # Parse names list
        result = self.GetEvalResultContents(env, evalRes)
        return result

    def GetGatheringFunctions(self, env):
        """Gets list of dynamically defined gathering functions"""
        
        # Get all functions
        funcs = self.GetDeffunctionNames(env)

        # Select just ones needed for gathering
        result = [fcn for fcn in funcs if fcn.startswith(self.__BLGatheringFunctionsPrefix)]
        return result

    def GetAllGatheringResults(self, env):
        """Gets all the results from gathering functions into one object"""
        # Create result object
        result = {}

        # Get all gathering function names
        gatheringFuncs = self.GetGatheringFunctions(env)

        # Do evaluation for each function
        for gatheringFunc in gatheringFuncs:
            evalRes = self._wrapper.EnvEval(env, ("(" + gatheringFunc + ")").encode("utf-8"))

            # Parse result
            parsedRes = self.GetEvalResultContents(env, evalRes)

            # Add result to the output
            result[gatheringFunc[len(self.__BLGatheringFunctionsPrefix):]] = parsedRes

        return result

    def PassFactsIntoEnv(self, env, facts):
        """Passes facts from string to env. Facts should be line-end separated"""
        res = {} 
        # Create a temp file
        tmpFile = tempfile.NamedTemporaryFile("w+t", delete=False)
        try:        
            # Write facts
            tmpFile.write(facts)

            # Close tmp file
            tmpFile.close()

            res = self.Wrapper.EnvLoadFacts(env, tmpFile.name)

        finally:
            # Delete temp file
            os.remove(tmpFile.name)

        return res

    def GetAllAvailableRulesIntoEnv(self, env):
        """Gets all available rules for model"""
        # Get path to rules
        filePath = os.path.dirname(os.path.abspath(__file__))
        rulesPath = os.path.join(filePath, "..", "..", "..", "KnowledgeDatabase", "Rules")
        rulesOrderFilePath = os.path.join(rulesPath, "LoadOrder.txt")

        # Read the order
        rulesOrderFile = open(rulesOrderFilePath, "r")
        order = rulesOrderFile.read()
        rulesOrderFile.close()
        
        # Get list of files
        ruleFiles = order.split("\n")

        # Load each file into environment
        for ruleFile in ruleFiles:
            self.Wrapper.EnvLoad(env, (os.path.join(rulesPath, ruleFile)).encode("utf-8"))

        self.Wrapper.EnvReset(env)

    def GetRulesFromFilesIntoEnv(self, env, files):
        """Loads files into environment"""
        # Load each file into environment
        for ruleFile in files:
            self.Wrapper.EnvLoad(env, ruleFile.encode("utf-8"))

        self.Wrapper.EnvReset(env)

    def RunCLIPSForModel(self, model, options=None):
        """Gets all rules and facts for model and runs engine"""
        res = {}
        # Create CLIPS environment
        env = self.Wrapper.CreateEnv()
        try:
            # Load rules
            self.GetAllAvailableRulesIntoEnv(env)

            # Reset environment to load deffact constructs
            self.Wrapper.EnvReset(env)

            # Create and load facts
            facts = model.GetClipsFacts(options)
            self.PassFactsIntoEnv(env, facts)

            # Run environment engine
            self.Wrapper.EnvRun(env)

            # Get results
            res = self.GetAllGatheringResults(env)
        except Exception as e:
            print(e)
        
        finally:
            # Destroy environment
            self.Wrapper.DestroyEnv(env)

        return res

    def RunCLIPSForModelWithSetOfRuleFacts(self, model, ruleFiles, options=None):
        """Gets all rules and facts from list of files for model and runs engine"""
        res = {}
        # Create CLIPS environment
        env = self.Wrapper.CreateEnv()
        try:
            # Load rules
            self.GetRulesFromFilesIntoEnv(env, ruleFiles["files"])

            # Reset environment to load deffact constructs
            self.Wrapper.EnvReset(env)

            # Create and load facts
            facts = model.GetClipsFacts(options)
            self.PassFactsIntoEnv(env, facts)

            # Run environment engine
            self.Wrapper.EnvRun(env)

            # Get results
            res = self.GetAllGatheringResults(env)
        except Exception as e:
            print(e)
        
        finally:
            # Destroy environment
            self.Wrapper.DestroyEnv(env)

        return res
