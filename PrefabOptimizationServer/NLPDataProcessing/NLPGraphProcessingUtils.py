import json
from Consts import *

class NLPGraphProcessingUtils(object):
    """Utilities for graph processing"""
    def cmp_to_key(mycmp):
        "Convert a cmp= function into a key= function"
        class K:
            def __init__(self, obj, *args):
                self.obj = obj
            def __lt__(self, other):
                return mycmp(self.obj, other.obj) < 0
            def __gt__(self, other):
                return mycmp(self.obj, other.obj) > 0
            def __eq__(self, other):
                return mycmp(self.obj, other.obj) == 0
            def __le__(self, other):
                return mycmp(self.obj, other.obj) <= 0
            def __ge__(self, other):
                return mycmp(self.obj, other.obj) >= 0
            def __ne__(self, other):
                return mycmp(self.obj, other.obj) != 0
        return K

    def LoadGraphFromContents(graphStrContents):
        """Loads netwokx graph from json string"""
        from networkx.readwrite import json_graph
        # Parse JSON syntax to a dictinary
        jsonDic = json.loads(graphStrContents)

        # Create the graph from the dictionary
        G = json_graph.node_link_graph(jsonDic)

        return G

    def LoadGraphFromDynamoContents(graphStrContents):
        """Loads netwokx graph from json string"""
        from networkx.readwrite import json_graph
        # Parse JSON syntax to a dictinary
        jsonDic = json.loads(graphStrContents)

        # Create the graph from the dictionary
        G = json_graph.node_link_graph(jsonDic["graph"])

        return G

    def LoadGraphFromDynamoContentsJson(graphJsonContents):
        """Loads netwokx graph from json string"""
        from networkx.readwrite import json_graph
        jsonDic = graphJsonContents

        # Create the graph from the dictionary
        G = json_graph.node_link_graph(jsonDic["graph"])

        return G

    def LoadGraphFromFile(filePath):
        """Loads netwokx graph from json string"""
        with open(filePath) as file:
            data = file.read()
        G = NLPGraphProcessingUtils.LoadGraphFromContents(data)

        return G

    def LoadGraphFromDynamoFile(filePath):
        """Loads netwokx graph from json string"""
        with open(filePath) as file:
            data = file.read()
        G = NLPGraphProcessingUtils.LoadGraphFromDynamoContents(data)

        return G



