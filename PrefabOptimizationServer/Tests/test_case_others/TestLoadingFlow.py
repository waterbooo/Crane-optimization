import unittest
import sys, os

filePath = os.path.dirname(os.path.abspath(__file__))

__KBDataManagementPath = os.path.join(os.path.split(filePath)[0], "KBDataManagement")
if not __KBDataManagementPath in sys.path:
    sys.path.insert(1, __KBDataManagementPath)

from TradesByObjectChecker import *

class Test_TestLoadingFlow(unittest.TestCase):
    def test_mapping_of_names(self):
        checker = TradesByObjectChecker()
        names = checker.TranslateObjectNames(["Room", "AnalyticalModel"], "revit")
        self.assertTrue("Room" in names)
        self.assertTrue("Steel Analytical Model" in names)

    def test_get_trades_smoke(self):
        checker = TradesByObjectChecker()
        trades = checker.GetTradesForClientObjects(["Room"], "revit")
        self.assertTrue("Carpeting" in trades)
        self.assertEqual(len(trades), 1)

if __name__ == '__main__':
    unittest.main()
