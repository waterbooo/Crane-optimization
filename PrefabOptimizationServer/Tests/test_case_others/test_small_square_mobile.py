import unittest
import os, sys

from EndpointConstants import EndpointConstants as ec
from EndpointUtils import EndpointUtils as eutils

from Optimization.Positions.PrefabCranePositionOptimizer import CranePositionOptimizationGA

from Optimization.DataStructures.SiteData import SiteData
from Optimization.DataStructures.CraneData import CraneData
from Optimization.Order.ConstructionOrdering import ConstructionOrdering
from Optimization.Order.BarDependencyChecker import BarDependencyChecker

filePath = os.path.dirname(os.path.abspath(__file__))

__ParsePath = os.path.join(os.path.split(filePath)[0], "Parsers")
if not __ParsePath in sys.path:
    sys.path.insert(1, __ParsePath)

from Parsers.AdvanceSteelModelParser import AdvanceSteelModelParser

class Test_mobile_cranepos_one_small_model(unittest.TestCase):

    def test_small_rectangle_mobile_optimization(self):
        import json
        import codecs
        from pprint import pprint
        from Optimization.DataStructures.MobileCraneData import MobileCraneData

        # default installation time 1.5 minutes
        installationTime = 1.5

         # load the base JSON
        baseModel = None
        reader = codecs.getreader("utf-8")
        file_name=os.path.normpath("c:/dev/BuildOptimizer/PrefabOptimizationServer/PrefabOptimizationServer/Tests/small_square_model_with_bars_and_cols_mobile.json")
        with open(file_name, encoding='utf-8-sig') as data_file: 
            baseModel = json.loads(data_file.read())
 
        # Surrounding polygons are polygons of buildings which limit crane (not used for now)
        surroundingPolygons = []
        if ec.TagCraneOptSurroundingPolygons in baseModel:
            surroundingPolygons = baseModel[ec.TagCraneOptSurroundingPolygons]

        # Site polygons are polygons of the site in same coordinate system as bar data
        sitePolygons = []
        if ec.TagCraneOptSitePolygons in baseModel:
            sitePolygons = baseModel[ec.TagCraneOptSitePolygons]
        
        RawCranes = baseModel[ec.TagCraneOptCranes]
        cranes=[]
        
        for c in RawCranes:
            if not isinstance(c,MobileCraneData):
                cranes.append(MobileCraneData(c))
            else:
                cranes.append(c)

       # model data
        client = ""
        parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
        pm = parser.ParseProjectModel(baseModel[ec.TagCraneOptModelData])

        # Surrounding polygons are polygons of buildings which limit crane (not used for now)
        surroundingPolygons = []
        if ec.TagCraneOptSurroundingPolygons in baseModel:
            surroundingPolygons = baseModel[ec.TagCraneOptSurroundingPolygons]

        # Site polygons are polygons of the site in same coordinate system as bar data
        sitePolygons = []
        if ec.TagCraneOptSitePolygons in baseModel:
            sitePolygons = baseModel[ec.TagCraneOptSitePolygons]
        
        # Run optimization process
        res = CranePositionOptimizationGA(pm, cranes, visualize=False, hofUpdateCallback=None,  surroundingPolygons=surroundingPolygons, sitePolygons=sitePolygons, installationTime=installationTime)

        self.assertLessEqual(1, 0.8, "Time is out of interval")

if __name__ == "__main__":
    unittest.main()
