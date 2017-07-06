import os, json, networkx as nx, tempfile
from networkx.readwrite import json_graph

from AppendPathsOS import AppendPathsOS
AppendPathsOS()

from NLPResultGraphParser import *

from KnowledgeDatabase import KnowledgeDatabase

class KBRulesLoader(object):
    """Helper for loading CLIPS rules from different sources in the right order"""
    __CommonRuleFilesLocation = os.path.join(os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "CLIPSWrapper"), "..", "..", "..", "KnowledgeDatabase", "Rules")

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def __ReadJSONGraphFile(self, filename):
        """Reads graph from json serialization"""
        with open(filename) as f:
            js_graph = json.load(f)
        return json_graph.node_link_graph(js_graph)

    def ListOfRuleFilesForTrades(self, trades):
        """Gets list of files to be loaded for the given list of trades"""
        rl = KBRulesLoader
        resFiles = {"files": [], "tmps": []}
        filePath = os.path.dirname(os.path.abspath(__file__))
        graphParser = NLPResultGraphParser()
        dependencies = {}
        with open(os.path.join(rl.__CommonRuleFilesLocation, "Dependencies.json"), "r") as depFile:
            depFile.seek(0, 0)
            dependencies = json.loads(depFile.read()[3:])

        # Open json with info for all the trades (DB is needed here)
        with open(os.path.join(filePath, "TradeToObjects.json"), "r") as dataFile:
            dataFile.seek(0, 0)
            tradesData = json.loads(dataFile.read()[3:])
            files = []
            
            # Load rules which should persist always
            for name in dependencies["AlwaysLoad"]:
                if not name in files:
                    files.append(name)

            # Get sources for trades
            for trade in trades:
                if trade in tradesData:
                    for source in tradesData[trade]["Sources"]:
                        self.GetDependenciesList(dependencies, source["Name"], files)

            # Go through obtained list

            # Split all the files into JSON files and other files
            # Split all the files into JSON files and other files
            jsonFiles = []
            for file in files:
                if file.endswith(".json"):
                    jsonFiles.append(file)
                else:
                    # Just add file to List with its dependencies
                    resFiles["files"].append(os.path.join(rl.__CommonRuleFilesLocation,file))

            # Read all selected trades into a single knowledge graph.
            # Resolve all collisions between node names for different trades.
            graph = KnowledgeDatabase.FetchTrades(jsonFiles);

            # Parse graph into CLIPS rules and store in tmp file
            res = graphParser.ParseGraph(graph)
            rules = res.ClipsConstruct()
            tmpFile = tempfile.NamedTemporaryFile("w+t", delete=False)
            try:
                # Write rules
                tmpFile.write(rules)

                # Close tmp file
                tmpFile.close()
                resFiles["files"].append(tmpFile.name)
                resFiles["tmps"].append({"orig": file, "tmp": tmpFile.name})
            except Exception as e:
                print(e)

        return resFiles

    def GetDependenciesList(self, dependencies, filename, res):
        """Gets a list of dependencies for a given filename"""
        dep = []
        if filename in dependencies:
            dep = dependencies[filename]
        for d in dep:
            if not d in res:
                self.GetDependenciesList(dependencies, d, res)
        if not filename in res:
            res.append(filename)