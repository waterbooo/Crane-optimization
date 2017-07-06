import unittest
import sys, os, json, tempfile
filePath = os.path.dirname(os.path.abspath(__file__))
__parsersPath = os.path.join(os.path.split(filePath)[0], "Parsers")

if not __parsersPath in sys.path:
    sys.path.insert(1, __parsersPath)

class Test_tekla_parse_test(unittest.TestCase):
    def test_tekla_parse_smoke(self):

        from Parsers.TeklaModelParser import TeklaModelParser
        parser = TeklaModelParser()
        with open(os.path.join(os.path.join(filePath, "Parsers"), "analyticalmodel.json")) as data_file:
            data = json.load(data_file)
            model = parser.ParseProjectModel(data)
            print("Passed")

    def test_tekla_clips_conversion_smoke(self):
        sys.path.insert(1, os.path.join(os.path.split(filePath)[0], "CLIPSWrapper"))

        from Parsers.TeklaModelParser import TeklaModelParser
        from PrefabCLIPSWrapper import PrefabCLIPSWrapper
        cw = PrefabCLIPSWrapper()
        parser = TeklaModelParser()

        with open(os.path.join(os.path.join(filePath, "Parsers"), "analyticalmodel.json")) as data_file:
            data = json.load(data_file)
            model = parser.ParseProjectModel(data)
            facts = model.GetClipsFacts()
            env = cw.CreateEnv()
            rulesPath = os.path.join(os.path.join(os.path.join(os.path.split(filePath)[0], "CLIPSWrapper"), "..", "..", "..", "KnowledgeDatabase", "Rules"), "AnalyticalModelDeftemplates.clp")
            cw.EnvLoad(env, rulesPath.encode("utf-8"))
            # Create a temp file
            tmpFile = tempfile.NamedTemporaryFile("w+t", delete=False)
                
            # Write facts
            tmpFile.write(facts)
            tmpFile.close()

            cw.EnvLoadFacts(env, tmpFile.name.encode("utf-8"))

            cw.EnvClear(env)
            cw.DestroyEnv(env)

            self.assertNotEqual(facts, "", "Empty facts result")

if __name__ == '__main__':
    unittest.main()
