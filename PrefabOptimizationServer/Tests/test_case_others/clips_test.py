import unittest
from ctypes import *
import sys, os

filePath = os.path.dirname(os.path.abspath(__file__))

__CLIPSPath = os.path.join(os.path.split(filePath)[0], "CLIPSWrapper")
if not __CLIPSPath in sys.path:
    sys.path.insert(1, __CLIPSPath)

from PrefabCLIPSProcessor import *

class Test_clips_test(unittest.TestCase):
    def test_clips_wrapper_smoke(self):
        clipsProcessor = PrefabCLIPSProcessor()

        cw = clipsProcessor.Wrapper
        cp = clipsProcessor.Parser
        env = cw.CreateEnv()
        cw.EnvClear(env)
        
        cw.EnvLoad(env, (os.path.join(os.path.join(filePath, "CLIPS"), "SteelStructureAnalysis.clp")).encode("utf-8"))
        cw.EnvLoadFacts(env, (os.path.join(os.path.join(filePath, "CLIPS"), "Sample.facts")).encode("utf-8"))
        cw.EnvRun(env)
        evalRes = cw.EnvEval(env, b"(get-connection-result-list)")
        evalMf = cast(evalRes.value, POINTER(multifield)).contents
        for i in range(evalMf.multifieldLength):
            t = cp.GetMFType(evalMf, i + 1)
            v = cp.GetMFValue(evalMf, i + 1)

            if dataTypes[t] == "FACT_ADDRESS":
                id = cp.DOPToString(cw.EnvGetFactSlot(env, v, b"id"))
                check = cp.DOPToString(cw.EnvGetFactSlot(env, v, b"metadata-ok"))
                if id == "513096-510838":
                    self.assertEqual(check, "FALSE")
                else:
                    self.assertEqual(check, "TRUE")
            else:
                self.assertTrue(False, "Wrong EnvEval result")
        
        cw.DestroyEnv(env)

    def test_clips_processor_parsing_eval_res(self):
        clipsProcessor = PrefabCLIPSProcessor()

        cw = clipsProcessor.Wrapper
        cp = clipsProcessor.Parser
        env = cw.CreateEnv()
        cw.EnvClear(env)
        
        cw.EnvLoad(env, (os.path.join(os.path.join(filePath, "CLIPS"), "SteelStructureAnalysis.clp")).encode("utf-8"))
        cw.EnvLoadFacts(env, (os.path.join(os.path.join(filePath, "CLIPS"), "Sample.facts")).encode("utf-8"))
        cw.EnvRun(env)

        evalRes = cw.EnvEval(env, b"(get-beam-result-list)")
        parsedRes = clipsProcessor.GetEvalResultContents(env, evalRes)

        cw.DestroyEnv(env)
        self.assertEqual(len(parsedRes), 12)
        self.assertTrue("beam-result" in parsedRes[0])
        self.assertTrue("size-to-range-valid" in parsedRes[0]["beam-result"])

    def test_clips_processor_get_slot_names(self):
        clipsProcessor = PrefabCLIPSProcessor()

        cw = clipsProcessor.Wrapper
        env = cw.CreateEnv()
        cw.EnvClear(env)
        
        cw.EnvLoad(env, (os.path.join(os.path.join(filePath, "CLIPS"), "SteelStructureAnalysis.clp")).encode("utf-8"))
        names = clipsProcessor.GetDeftemplateSlotNames(env, "connection-data")
        cw.DestroyEnv(env)
        self.assertEqual(names, ["id",
	                            "type",
	                            "beam-id",
	                            "column-id",
	                            "max-beam-size",
	                            "min-beam-size",
	                            "max-beam-linear-weight",
	                            "max-beam-flange-thickness",
	                            "min-beam-flange-thickness",
	                            "min-clear-span-depth-ratio",
	                            "max-column-depth",
	                            "web-to-thickness-ratio-ok-beam",
	                            "web-to-thickness-ratio-ok-column"])
        
    def test_clips_processor_get_fcn_names(self):
        clipsProcessor = PrefabCLIPSProcessor()

        cw = clipsProcessor.Wrapper
        env = cw.CreateEnv()
        cw.EnvClear(env)
        
        cw.EnvLoad(env, (os.path.join(os.path.join(filePath, "CLIPS"), "SteelStructureAnalysis.clp")).encode("utf-8"))
        funcs = clipsProcessor.GetDeffunctionNames(env)
        cw.DestroyEnv(env)

        self.assertEqual(len(funcs), 4)
        self.assertTrue("BLGatherget-model-result-list" in funcs)
        self.assertTrue("get-connection-result-list" in funcs)
        self.assertTrue("BLGatherget-column-result-list" in funcs)
        self.assertTrue("get-beam-result-list" in funcs)


    def test_clips_processor_get_gathering_fcns(self):
        clipsProcessor = PrefabCLIPSProcessor()

        cw = clipsProcessor.Wrapper
        env = cw.CreateEnv()
        cw.EnvClear(env)
        
        cw.EnvLoad(env, (os.path.join(os.path.join(filePath, "CLIPS"), "SteelStructureAnalysis.clp")).encode("utf-8"))
        gatFuncs = clipsProcessor.GetGatheringFunctions(env)
        cw.DestroyEnv(env)

        self.assertEqual(len(gatFuncs), 2)
        self.assertTrue("BLGatherget-model-result-list" in gatFuncs)
        self.assertTrue("BLGatherget-column-result-list" in gatFuncs)
        
    def test_clips_processor_gather_results(self):
        clipsProcessor = PrefabCLIPSProcessor()

        cw = clipsProcessor.Wrapper
        env = cw.CreateEnv()
        cw.EnvClear(env)
        
        cw.EnvLoad(env, (os.path.join(os.path.join(filePath, "CLIPS"), "SteelStructureAnalysis.clp")).encode("utf-8"))
        cw.EnvLoadFacts(env, (os.path.join(os.path.join(filePath, "CLIPS"), "Sample.facts")).encode("utf-8"))
        cw.EnvRun(env)

        gatheringResults = clipsProcessor.GetAllGatheringResults(env)
        self.assertTrue("get-model-result-list" in gatheringResults)
        self.assertEqual(len(gatheringResults["get-model-result-list"]), 1)
        self.assertTrue("get-column-result-list" in gatheringResults)
        self.assertEqual(len(gatheringResults["get-column-result-list"]), 12)

if __name__ == '__main__':
    unittest.main()
