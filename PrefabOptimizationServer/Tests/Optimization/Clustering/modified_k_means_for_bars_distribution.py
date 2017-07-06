import unittest, random, os, json
import numpy as np
from Optimization.Clustering.KMeansBasedBarsDivision import KMeansBasedBarsDivision
from Parsers.AdvanceSteelModelParser import AdvanceSteelModelParser
from EndpointConstants import EndpointConstants as ec
from Optimization.DataStructures.SiteData import SiteData
from Optimization.DataStructures.TowerCraneData import TowerCraneData
from Optimization.Order.ConstructionOrdering import ConstructionOrdering
from Optimization.Order.BarDependencyChecker import BarDependencyChecker

def init_board_gauss(N, k):
    n = float(N)/k
    X = []
    for i in range(k):
        c = (random.uniform(-1, 1), random.uniform(-1, 1))
        s = random.uniform(0.05,0.5)
        x = []
        while len(x) < n:
            a, b = np.array([np.random.normal(c[0], s), np.random.normal(c[1], s)])
            # Continue drawing points from the distribution in the range [-1,1]
            if abs(a) < 1 and abs(b) < 1:
                x.append([a,b])
        X.extend(x)
    X = np.array(X)[:N]
    return list(X)

class Test_modified_k_means_for_bars_distribution(unittest.TestCase):
    def test_modified_kmeans_noerror(self):
        c = KMeansBasedBarsDivision()
        filePath = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(os.path.join(os.path.split(os.path.split(os.path.split(os.path.split(filePath)[0])[0])[0])[0], "TestData"), "testModelDataWithOneCrane.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read())
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data[ec.TagCraneOptModelData])
            cranes = [TowerCraneData(data[ec.TagCraneOptCranes][0])] * 3
            sd = SiteData(pm, cranes)
            centers = [np.array([bar.CenterPoint.X, bar.CenterPoint.Y]) for bar in pm.SteelAnalyticalModel.Bars.values()]
            c.ProhibitedRegion = sd.ModelPolygon
            c.Radiuses = [cr.maxLength for cr in cranes]
            res = c.FindCenters(centers, 3)
    
    def test_clustered_ordering_noerror(self):
        c = KMeansBasedBarsDivision()
        filePath = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(os.path.join(os.path.split(os.path.split(os.path.split(os.path.split(filePath)[0])[0])[0])[0], "TestData"), "testModelDataWithOneCrane.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read())
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data[ec.TagCraneOptModelData])
            cranes = [TowerCraneData(data[ec.TagCraneOptCranes][0])] * 3
            sd = SiteData(pm, cranes)
            centers = [np.array([bar.CenterPoint.X, bar.CenterPoint.Y]) for bar in pm.SteelAnalyticalModel.Bars.values()]
            c.ProhibitedRegion = sd.ModelPolygon
            c.Radiuses = [cr.maxLength for cr in cranes]
            res = c.FindCenters(centers, 3)
            # Build model bars dependency graph
            BarDependencyChecker.buildDependencyGraph(sd)
            order = ConstructionOrdering.GetConstructionOrderClustered(sd.dependencies, list(sd.Bars.values()), res[2])

    def test_mult_ordering_noerror(self):
        filePath = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(os.path.join(os.path.split(os.path.split(os.path.split(os.path.split(filePath)[0])[0])[0])[0], "TestData"), "testModelDataWithOneCrane.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read())
            if not "modelData" in data or not "cranes" in data:
                self.fail("Bad json implemented")
            parser = AdvanceSteelModelParser()
            pm = parser.ParseProjectModel(data[ec.TagCraneOptModelData])
            cranes = [TowerCraneData(data[ec.TagCraneOptCranes][0])] * 3
            sd = SiteData(pm, cranes)

            # Build model bars dependency graph
            BarDependencyChecker.buildDependencyGraph(sd)
            order = ConstructionOrdering.GetConstructionOrderMult(sd.dependencies, list(sd.Bars.values()), 3)

if __name__ == '__main__':
    unittest.main()
