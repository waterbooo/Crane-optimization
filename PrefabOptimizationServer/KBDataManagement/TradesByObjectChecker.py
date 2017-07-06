import os, sys, json
__filePath = os.path.dirname(os.path.abspath(__file__))

class TradesByObjectChecker(object):
    """Translates input object names into internal terms and gets trades for the list"""

    __TradesToObjectsMappingFile = "TradeToObjects.json"

    # Tags
    __TagClipsFactMappings = "ClipsFactMappings"

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def TranslateObjectNames(self, names, client):
        """Translate input list of string names into internal names
           returns: list of corresponding internal names
        """
        res = []
        filePath = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(filePath, "NameToInternalName.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            namesDict = data[client]
            res = [namesDict[n] for n in names if n in namesDict]
        return res

    def GetTradesForObjects(self, names):
        """Gets list of trades related to passed list of internal names"""
        toc = TradesByObjectChecker
        res = []
        filePath = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(filePath, toc.__TradesToObjectsMappingFile), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            ns = set(names)
            res = [key for (key, value) in data.items() if not ns.isdisjoint(value["Objects"])]
        return res

    def GetTradesForClientObjects(self, names, client):
        """Gets the names of trades for names in terms of client"""
        translatons = self.TranslateObjectNames(names, client)
        trades = self.GetTradesForObjects(translatons)
        return trades

    def GetAllTrades(self):
        """Returns all trades"""
        toc = TradesByObjectChecker
        res = []
        filePath = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(filePath, toc.__TradesToObjectsMappingFile), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])
            res = [key for key in data.keys()]
        return res

    def GetClipsMappingForTrades(self, trades):
        """Forms mapping for trade objects into clips fact templates which should be designed"""
        toc = TradesByObjectChecker
        res = {}
        
        # Open mapping file
        filePath = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(filePath, toc.__TradesToObjectsMappingFile), "r") as dataFile:
            dataFile.seek(0, 0)
            data = json.loads(dataFile.read()[3:])

            # Iterate through the trades
            for trade in trades:

                # Check whether there is data for trade
                if trade in data:
                    tradeData = data[trade]

                    # Check whether we have clips mappings
                    if toc.__TagClipsFactMappings in tradeData:
                        mappings = tradeData[toc.__TagClipsFactMappings]

                        # Walk through mappings and add them into mappings dict
                        for mapping in mappings.items():
                            if not mapping[0] in res:
                                res[mapping[0]] = set()
                            for obj in mapping[1]:
                                res[mapping[0]].add(obj)
        return res