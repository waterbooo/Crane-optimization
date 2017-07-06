import unittest, os, sys, json
filePath = os.path.dirname(os.path.abspath(__file__))

__OptPath = os.path.join(os.path.split(filePath)[0], "Optimization")
if not __OptPath in sys.path:
    sys.path.insert(1, __OptPath)

__ParsePath = os.path.join(os.path.split(filePath)[0], "Parsers")
if not __ParsePath in sys.path:
    sys.path.insert(1, __ParsePath)

from Optimization.DataStructures.SiteData import SiteData
from Optimization.DataStructures.TowerCraneData import TowerCraneData
import networkx as nx
from Parsers.AdvanceSteelModelParser import AdvanceSteelModelParser

from Optimization.Order.BarDependencyChecker import BarDependencyChecker



class Test_cycles_in_depencies_graph(unittest.TestCase):
    def test_simple_square_with_cycle_neighbours(self):
        with open(os.path.join(filePath, "cycle_test1.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            crane = TowerCraneData(data["cranes"][0])
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data["modelData"])
            md = SiteData(pm, [crane])
            cycles = nx.algorithms.cycles.simple_cycles(md.dependencies)
            self.assertEqual(len(list(cycles)), 0, msg = "There are cycles")

    def test_simple_2square_with_cycle_neighbours(self):
        with open(os.path.join(filePath, "cycle_test2.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            crane = TowerCraneData(data["cranes"][0])
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data["modelData"])
            md = SiteData(pm, [crane])
            cycles = nx.algorithms.cycles.simple_cycles(md.dependencies)
            self.assertEqual(len(list(cycles)), 0, msg = "There are cycles")    
        
    def test_simple_2square_full_with_cycle_neighbours(self):
        with open(os.path.join(filePath,"cycle_test3.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            crane = TowerCraneData(data["cranes"][0])
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data["modelData"])
            md = SiteData(pm, [crane])
            cycles = nx.algorithms.cycles.simple_cycles(md.dependencies)
            self.assertEqual(len(list(cycles)), 0, msg = "There are cycles")    

    def test_simple_structure_order(self):
        with open(os.path.join(filePath, "small_square_model_with_bars_and_cols.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            crane = TowerCraneData(data["cranes"][0])
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data["modelData"])
            md = SiteData(pm, [crane])
            BarDependencyChecker.buildDependencyGraph(md)
            cycles = nx.algorithms.cycles.simple_cycles(md.dependencies)
            self.assertEqual(len(list(cycles)), 0, msg = "There are cycles")    
            self.assertTrue(md.dependencies.has_edge("5", "1"))
            self.assertTrue(md.dependencies.has_edge("5", "4"))
            self.assertTrue(md.dependencies.has_edge("7", "3"))
            self.assertTrue(md.dependencies.has_edge("7", "4"))
            self.assertTrue(md.dependencies.has_edge("9", "2"))
            self.assertTrue(md.dependencies.has_edge("9", "3"))
            self.assertTrue(md.dependencies.has_edge("11", "1"))
            self.assertTrue(md.dependencies.has_edge("11", "2"))
            self.assertEqual(md.dependencies.number_of_edges(), 8)


if __name__ == "__main__":
    unittest.main()
