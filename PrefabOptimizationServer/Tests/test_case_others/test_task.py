import unittest, os

import neo4j

from Model.Task import *
from Neo4jTestUtils import Neo4jTestUtils
from NLPDataProcessing.NLPGraphProcessingUtils import *

_dirPath = os.path.dirname(os.path.abspath(__file__)) 

class Test_task(unittest.TestCase):

    def test_parse(self):

        graphPath = os.path.join(_dirPath, "Graphs", "KB_tasks_graph.json")
        G = NLPGraphProcessingUtils.LoadGraphFromDynamoFile(graphPath)

        # Push the graph to neo4j database for visual testing
        try:
            Neo4jTestUtils.PushNxDiGraphToNeo4j(G)
        except neo4j.v1.exceptions.ProtocolError as e:
            if "is the server running?" in e.args[0]:
                # Looks like local neo4j server has not been started
                pass
            else:
                # Let the error propagate (wrong password etc.)
                raise

        tasks = Task.ParseTasksFromGraph(G)

        # Prepare the expected output tasks data
        expTaskNameToAttrsDict = { \
            "c.anchor": { \
                Strings.target: ["frame"],
                Strings.uses: ["method", "perimeter bolting"] },
            "cut": { \
                Strings.actor: ["action", "teeth", "thread"],
                Strings.target: ["band", "extrusion", "gasket", "lubricant", "tolerance"],
                Strings.range: ["hole", "portion"],
                Strings.uses: ["die", "pressure", "tap"] },
            "enlarge": { \
                Strings.target: ["hole"],
                Strings.uses: ["drill bit"] },
            "form": { \
                Strings.actor: ["chip", "thread"],
                Strings.target: ["extrusion", "process"],
                Strings.uses: ["-specific tooling", "press"] },
            "generate": { \
                Strings.target: ["hole"],
                Strings.uses: ["threading"] },
            "handle": { \
                Strings.target: ["frame"],
                Strings.uses: ["care"] },
            "instal": { \
                Strings.actor: ["frame"],
                Strings.target: ["glass"],
                Strings.uses: ["bench mark"] },
            "join": { \
                Strings.actor: ["two extrusion"],
                Strings.target: ["two tube"],
                Strings.uses: ["polypropylene strip"] } }

        # Compare tasks names
        expTasksNames = list(expTaskNameToAttrsDict.keys())
        expTasksNames.sort()
        actTasksNames = [task.name for task in tasks]
        actTasksNames.sort()
        self.assertListEqual(expTasksNames, actTasksNames)

        for task in tasks:

            expAttrs = expTaskNameToAttrsDict[task.name]
            actAttrs = task.properties["attributes"]

            # Compare task attributes keys
            expAttrsKeys = list(expAttrs.keys())
            expAttrsKeys.sort()
            actAttrsKeys = list(actAttrs.keys())
            actAttrsKeys.sort()
            self.assertListEqual(expAttrsKeys, actAttrsKeys)

            # Compare task attributes values
            for attrKey in expAttrsKeys:
                expAttrValues = expAttrs[attrKey]
                expAttrValues.sort()
                actAttrValues = actAttrs[attrKey]
                actAttrValues.sort()
                self.assertListEqual(expAttrValues, actAttrValues)


if __name__ == "__main__":
    unittest.main()
