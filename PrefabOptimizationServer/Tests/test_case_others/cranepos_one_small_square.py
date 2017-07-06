import unittest
import os, sys
from Optimization.Positions.PrefabCranePositionOptimizer import CranePositionOptimizationGA

filePath = os.path.dirname(os.path.abspath(__file__))

__ParsePath = os.path.join(os.path.split(filePath)[0], "Parsers")
if not __ParsePath in sys.path:
    sys.path.insert(1, __ParsePath)

from Parsers.AdvanceSteelModelParser import AdvanceSteelModelParser

class Test_cranepos_one_small_model(unittest.TestCase):
    def test_small_square(self):
        import json
        
        with open(os.path.join(filePath, "small_square_model.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data["modelData"])
            res = CranePositionOptimizationGA(pm, data["cranes"])
            dataFile.close()
            time = res["time"]
            self.assertLessEqual(abs(time - 2.5), 0.3, "Time is out of interval")

    def test_small_rectangle(self):
        import json
        cwd = os.getcwd()
        with open(os.path.join(filePath, "small_rectangle_model.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data["modelData"])
            res = CranePositionOptimizationGA(pm, data["cranes"])
            dataFile.close()
            time = res["time"]
            self.assertLessEqual(abs(time - 6.0), 0.8, "Time is out of interval")

if __name__ == "__main__":
    unittest.main()
