import unittest
from ctypes import *
import sys, os

filePath = os.path.dirname(os.path.abspath(__file__))

__clipsWrapperPath = os.path.join(os.path.split(filePath)[0], "CLIPSWrapper")
if not __clipsWrapperPath in sys.path:
    sys.path.insert(1, __clipsWrapperPath)
__nlpResProcessingPath = os.path.join(os.path.split(filePath)[0], "NLPDataProcessing")
if not __nlpResProcessingPath in sys.path:
    sys.path.insert(1, __nlpResProcessingPath)

from PrefabCLIPSProcessor import *
from NLPDataProcessing.NLPResultGraphParser import *
from NLPDataProcessing.NLPGraphConstants import NLPGraphConstants as gc

from Consts import *

import networkx

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

def CreateTestCarpetingGraph():

    G = networkx.DiGraph()
        
    # Determine pre-defined nodes
    G.add_node("Requirement")
    G.add_node("Optional Requirement")

    # Determine flow
    G.add_node(Strings.ndProcess)
    G.node[Strings.ndProcess][Strings.attrGather] = True
    G.add_node("Carpeting")
    G.add_edge("Carpeting", Strings.ndProcess, Dicts.relIs)

    G.add_node(Strings.ndStep)
    G.node[Strings.ndStep][Strings.attrGather] = True
    G.add_edge(Strings.ndStep, Strings.ndProcess, Dicts.relPart)
    G.node[Strings.ndStep][Strings.ExtraFields] = [Strings.after]
    G.add_node("Number")
    G.add_edge(Strings.ndStep, "Number", Dicts.relHas)

    G.add_node("\"Choose a pattern\"")
    G.add_edge("\"Choose a pattern\"", "Carpeting", Dicts.relIn)
    G.add_edge("\"Choose a pattern\"", Strings.ndStep, Dicts.relIs)
    G.add_edge("\"Choose a pattern\"", "Number", {Strings.val: 1})

    G.add_node("\"Clear space\"")
    G.add_edge("\"Clear space\"", "Carpeting", Dicts.relIn)
    G.add_edge("\"Clear space\"", "\"Choose a pattern\"", Dicts.relAfter)
    G.add_edge("\"Clear space\"", Strings.ndStep, Dicts.relIs)
    G.add_edge("\"Clear space\"", "Number", {Strings.val: 2})

    G.add_node("\"Clean and inspect the existing floor\"")
    G.add_edge("\"Clean and inspect the existing floor\"", "Carpeting", Dicts.relIn)
    G.add_edge("\"Clean and inspect the existing floor\"", "\"Clear space\"", Dicts.relAfter)
    G.add_edge("\"Clean and inspect the existing floor\"", Strings.ndStep, Dicts.relIs)
    G.add_edge("\"Clean and inspect the existing floor\"", "Number", {Strings.val: 3})

    G.add_node("\"Gather tools\"")
    G.add_edge("\"Gather tools\"", "Carpeting", {Strings.rel: Strings.in_, gc.EnumerateRequirements: True})
    G.add_edge("\"Gather tools\"", "\"Clean and inspect the existing floor\"", Dicts.relAfter)
    G.add_edge("\"Gather tools\"", Strings.ndStep, Dicts.relIs)
    G.add_edge("\"Gather tools\"", "Number", {Strings.val: 4})
    
    G.add_node("\"Determine the center of your room\"")
    G.add_edge("\"Determine the center of your room\"", "Carpeting", Dicts.relIn)
    G.add_edge("\"Determine the center of your room\"", "\"Gather tools\"", Dicts.relAfter)
    G.add_edge("\"Determine the center of your room\"", Strings.ndStep, Dicts.relIs)
    G.add_edge("\"Determine the center of your room\"", "Number", {Strings.val: 5})

    G.add_node("\"Lay the tiles\"")
    G.add_edge("\"Lay the tiles\"", "Carpeting", Dicts.relIn)
    G.add_edge("\"Lay the tiles\"", "\"Determine the center of your room\"", Dicts.relAfter)
    G.add_edge("\"Lay the tiles\"", Strings.ndStep, Dicts.relIs)
    G.add_edge("\"Lay the tiles\"", "Number", {Strings.val: 6})

    G.add_node("\"Adhere the tiles\"")
    G.add_edge("\"Adhere the tiles\"", "Carpeting", Dicts.relIn)
    G.add_edge("\"Adhere the tiles\"", "\"Lay the tiles\"", Dicts.relAfter)
    G.add_edge("\"Adhere the tiles\"", Strings.ndStep, Dicts.relIs)
    G.add_edge("\"Adhere the tiles\"", "Number", {Strings.val: 7})

    # Determine tools
    G.add_node(Strings.ndTool)

    G.add_node("\"Measuring tape\"")
    G.add_edge("\"Measuring tape\"", Strings.ndTool, Dicts.relIs)

    G.add_node("\"Carpenter’s square\"")
    G.add_edge("\"Carpenter’s square\"", Strings.ndTool, Dicts.relIs)

    G.add_node("\"Chalk line\"")
    G.add_edge("\"Chalk line\"", Strings.ndTool, Dicts.relIs)

    G.add_node("\"Utility knife with a heavy-duty blade\"")
    G.add_edge("\"Utility knife with a heavy-duty blade\"", Strings.ndTool, Dicts.relIs)

    G.add_node("Adhesive")
    G.add_edge("Adhesive", Strings.ndTool, Dicts.relIs)

    G.add_node("\"Peel-and-stick Rightbac tape\"")
    G.add_edge("\"Peel-and-stick Rightbac tape\"", "Adhesive", Dicts.relIs)

    G.add_node("\"Dri-tac glue\"")
    G.add_edge("\"Dri-tac glue\"", "Adhesive", Dicts.relIs)

    G.add_node("\"U-notch trowel\"")
    G.add_edge("\"U-notch trowel\"", Strings.ndTool, Dicts.relIs)

    # Gather tools step
    G.add_edge("\"Measuring tape\"", "\"Gather tools\"", {Strings.rel: Strings.tool})
    G.add_edge("\"Carpenter's square\"", "\"Gather tools\"", {Strings.rel: Strings.tool})
    G.add_edge("\"Chalk line\"", "\"Gather tools\"", {Strings.rel: Strings.tool})
    G.add_edge("\"Utility knife with a heavy-duty blade\"", "\"Gather tools\"", {Strings.rel: Strings.tool})
    G.add_edge("Adhesive", "\"Gather tools\"", {Strings.rel: Strings.tool})
    G.add_edge("\"U-notch trowel\"", "\"Gather tools\"", {Strings.rel: Strings.tool})

    G.add_edge("\"Measuring tape\"", "Carpeting", Dicts.relReq)
    G.add_edge("\"Carpenter’s square\"", "Carpeting", Dicts.relReq)
    G.add_edge("\"Chalk line\"", "Carpeting", Dicts.relReq)
    G.add_edge("\"Utility knife with a heavy-duty blade\"", "Carpeting", Dicts.relReq)
    G.add_edge("Adhesive", "Carpeting", Dicts.relReq)
    G.add_edge("\"U-notch trowel\"", "Carpeting", Dicts.relReq)

    # Determine room (not from carpeting but metadata for rectangular room)
    G.add_node("Point")
    G.add_node("X")
    G.add_node("Y")
    G.add_edge("Point", "X", Dicts.relHas)
    G.add_edge("Point", "Y", Dicts.relHas)
    
    G.add_node("Room")
    #G.add_node("Length")
    #G.add_edge("Room", "Length", Dicts.relHas)
    #G.add_node("Width")
    #G.add_edge("Room", "Width", Dicts.relHas)
    G.add_node("Center")
    G.add_edge("Center", "Point", Dicts.relIs)
    G.add_edge("Room", "Center", Dicts.relHas)
    G.add_node("Id")
    G.add_edge("Room", "Id", Dicts.relHas)


    #G.add_node("Walls")
    G.add_node("Wall")
    G.add_node("Floor")

    #G.add_node("Wall1")
    #G.add_edge("Wall1", "Wall", Dicts.relIs)
    #G.add_edge("Walls", "Wall1", Dicts.relHas)

    #G.add_node("Wall2")
    #G.add_edge("Wall2", "Wall", Dicts.relIs)
    #G.add_edge("Walls", "Wall2", Dicts.relHas)

    #G.add_node("Wall3")
    #G.add_edge("Wall3", "Wall", Dicts.relIs)
    #G.add_edge("Walls", "Wall3", Dicts.relHas)

    #G.add_node("Wall4")
    #G.add_edge("Wall4", "Wall", Dicts.relIs)
    #G.add_edge("Walls", "Wall4", Dicts.relHas)


    G.add_node("Start")
    G.add_edge("Start", "Point", Dicts.relIs)
    G.add_edge("Wall", "Start", Dicts.relHas)

    G.add_node("End")
    G.add_edge("End", "Point", Dicts.relIs)
    G.add_edge("Wall", "End", Dicts.relHas)

    G.add_edge("Wall", "Center", Dicts.relHas)

    G.add_node("Opposite")
    G.add_edge("Wall", "Opposite", Dicts.relHas)

    # Carpeting patterns
    G.add_node("CarpetingPattern")
    G.add_node("RotationAngle")
    G.add_edge("CarpetingPattern", "RotationAngle", Dicts.relHas)
    G.add_node("ShiftDirection")
    G.add_edge("CarpetingPattern", "ShiftDirection", Dicts.relHas)
    G.add_node("ShiftRatio")
    G.add_edge("CarpetingPattern", "ShiftRatio", Dicts.relHas)
        
    G.add_node("Monolithic")
    G.add_node("Broadloom")
    G.add_node("Quarter Turn")
    G.add_node("Checker Board")
    G.add_node("Ashlar")
    G.add_node("Brick")

    G.add_edge("Monolithic", "CarpetingPattern", Dicts.relIs)
    G.add_edge("Broadloom", "CarpetingPattern", Dicts.relIs)
    G.add_edge("Quarter Turn", "CarpetingPattern", Dicts.relIs)
    G.add_edge("Checker Board", "CarpetingPattern", Dicts.relIs)
    G.add_edge("Ashlar", "CarpetingPattern", Dicts.relIs)
    G.add_edge("Brick", "CarpetingPattern", Dicts.relIs)

    G.add_edge("Monolithic", "RotationAngle", {Strings.val: 0.0})
    G.add_edge("Monolithic", "ShiftDirection", {Strings.val: "None"})
    G.add_edge("Monolithic", "ShiftRatio", {Strings.val: 0.0})

    G.add_edge("Broadloom", "RotationAngle", {Strings.val: 0.0})
    G.add_edge("Broadloom", "ShiftDirection", {Strings.val: "None"})
    G.add_edge("Broadloom", "ShiftRatio", {Strings.val: 0.0})

    G.add_edge("Quarter Turn", "RotationAngle", {Strings.val: 90.0})
    G.add_edge("Quarter Turn", "ShiftDirection", {Strings.val: "None"})
    G.add_edge("Quarter Turn", "ShiftRatio", {Strings.val: 0.0})

    G.add_edge("Checker Board", "RotationAngle", {Strings.val: 90.0})
    G.add_edge("Checker Board", "ShiftDirection", {Strings.val: "None"})
    G.add_edge("Checker Board", "ShiftRatio", {Strings.val: 0.0})

    G.add_edge("Ashlar", "RotationAngle", {Strings.val: 0.0})
    G.add_edge("Ashlar", "ShiftDirection", {Strings.val: "Length"})
    G.add_edge("Ashlar", "ShiftRatio", {Strings.val: 0.5})

    G.add_edge("Brick", "RotationAngle", {Strings.val: 0.0})
    G.add_edge("Brick", "ShiftDirection", {Strings.val: "Width"})
    G.add_edge("Brick", "ShiftRatio", {Strings.val: 0.5})

    # Carpet tile properties
    G.add_node("CarpetTile")
    G.add_node("Back")
    G.add_edge("CarpetTile", "Back", Dicts.relHas)

    G.add_node("\"Peel-and-stick\"")
    G.add_edge("\"Peel-and-stick\"", "CarpetTile", Dicts.relIs)
    G.add_edge("\"Peel-and-stick\"", "Back", {Strings.val: "\"adhesive back\""})

    G.add_node("Standard")
    G.add_edge("Standard", "CarpetTile", Dicts.relIs)
    G.add_edge("Standard", "Back", {Strings.val: "\"dry back\""})


    # Steps detailing

    G.add_node("ProcessSubStep")
    G.add_edge("ProcessSubStep", Strings.ndStep, Dicts.relPart)
    G.add_node("Instruction")
    G.add_edge("ProcessSubStep", "Instruction", Dicts.relHas)
    G.add_node("StepNumber")
    G.add_edge("ProcessSubStep", "StepNumber", Dicts.relHas)
    G.add_node("ProcessName")
    G.add_edge("ProcessSubStep", "ProcessName", Dicts.relHas)
    G.add_node("ElementId")
    G.add_edge("ProcessSubStep", "ElementId", Dicts.relHas)
    G.add_node("Pattern")
    G.add_edge("ProcessSubStep", "Pattern", Dicts.relHas)
    G.node["ProcessSubStep"][Strings.attrGather] = True


    # Lay carpet steps

    # Node for step
    G.add_node("LayCarpetSubStep1", Dicts.ndRuleOutTrue)

    # Connection for iheritance and membership
    G.add_edge("LayCarpetSubStep1", "ProcessSubStep", Dicts.relIs)
    G.add_edge("LayCarpetSubStep1", "\"Lay the tiles\"", Dicts.relIn)

    # Connections to input structures
    G.add_edge("LayCarpetSubStep1", "CarpetingPattern", Dicts.relInput)
    G.add_edge("LayCarpetSubStep1", "Room", Dicts.relInput)

    # Capturing connections
    G.add_edge("LayCarpetSubStep1", "X", {Strings.capture: "cx", Strings.captureFrom: "Room->Center"})
    G.add_edge("LayCarpetSubStep1", "Y", {Strings.capture: "cy", Strings.captureFrom: "Room->Center"})
    G.add_edge("LayCarpetSubStep1", "RotationAngle", {Strings.capture: "angle", Strings.captureFrom: "CarpetingPattern"})
    G.add_edge("LayCarpetSubStep1", "ShiftDirection", {Strings.capture: "sd", Strings.captureFrom: "CarpetingPattern"})
    G.add_edge("LayCarpetSubStep1", "ShiftRatio", {Strings.capture: "ratio", Strings.captureFrom: "CarpetingPattern"})
    G.add_edge("LayCarpetSubStep1", "Id", {Strings.captures: {
                                                            "name": {Strings.captureFrom: "CarpetingPattern"},
                                                            "id": {Strings.captureFrom: "Room"}
                                                         }})

    # Resulting attributes
    G.node["LayCarpetSubStep1"]["StepNumber"] = 1
    G.node["LayCarpetSubStep1"]["Instruction"] = "\"Put plus mark at (%?cx %?cy) it is a center of the room\""
    G.node["LayCarpetSubStep1"]["ProcessName"] = "Carpeting"
    G.node["LayCarpetSubStep1"]["ProcessStepId"] = "\"Lay the tiles\""
    G.node["LayCarpetSubStep1"]["ElementId"] = "%?id"
    G.node["LayCarpetSubStep1"]["Pattern"] = "%?name"

    # Next up connections
    G.add_edge("LayCarpetSubStep1", "LayCarpetSubStep2", Dicts.relLeadsTo)

    G.add_node("LayCarpetSubStep2", Dicts.ndRuleOutTrue)
    G.add_edge("LayCarpetSubStep2", "ProcessSubStep", Dicts.relIs)
    G.add_edge("LayCarpetSubStep2", "\"Lay the tiles\"", Dicts.relIn)
    G.add_edge("LayCarpetSubStep2", "CarpetingPattern", Dicts.relInput)
    G.add_edge("LayCarpetSubStep2", "Room", Dicts.relInput)
    G.add_edge("LayCarpetSubStep2", "Id", {Strings.captures: {
                                                            "name": {Strings.captureFrom: "CarpetingPattern"},
                                                            "id": {Strings.captureFrom: "Room"}
                                                         }})
    G.add_edge("LayCarpetSubStep2", "RotationAngle", {Strings.capture: "angle", Strings.captureFrom: "CarpetingPattern"})
    G.node["LayCarpetSubStep2"]["StepNumber"] = 2
    G.node["LayCarpetSubStep2"]["Instruction"] = "\"Place your first tile right in the center of the plus mark and work out from there\""
    G.node["LayCarpetSubStep2"]["ProcessName"] = "Carpeting"
    G.node["LayCarpetSubStep2"]["ProcessStepId"] = "\"Lay the tiles\""
    G.node["LayCarpetSubStep2"]["ElementId"] = "%?id"
    G.node["LayCarpetSubStep2"]["Pattern"] = "%?name"

    G.add_node("LayCarpetSubStep3", Dicts.ndRuleOutTrue)
    G.add_edge("LayCarpetSubStep3", "ProcessSubStep", Dicts.relIs)
    G.add_edge("LayCarpetSubStep3", "\"Lay the tiles\"", Dicts.relIn)
    G.add_edge("LayCarpetSubStep3", "CarpetingPattern", Dicts.relInput)
    G.add_edge("LayCarpetSubStep3", "Room", Dicts.relInput)
    G.add_edge("LayCarpetSubStep3", "Id", {Strings.captures: {
                                                            "name": {Strings.captureFrom: "CarpetingPattern"},
                                                            "id": {Strings.captureFrom: "Room"}
                                                         }})
    G.add_edge("LayCarpetSubStep3", "RotationAngle", {Strings.capture: "angle", Strings.captureFrom: "CarpetingPattern"})
    G.node["LayCarpetSubStep3"]["StepNumber"] = 3
    G.node["LayCarpetSubStep3"]["Instruction"] = "\"Point all tiles in the same direction\""
    G.node["LayCarpetSubStep3"]["ProcessName"] = "Carpeting"
    G.node["LayCarpetSubStep3"]["ProcessStepId"] = "\"Lay the tiles\""
    G.node["LayCarpetSubStep3"]["ElementId"] = "%?id"
    G.node["LayCarpetSubStep3"]["Pattern"] = "%?name"
    G.node["LayCarpetSubStep3"][Strings.attrResultingCondition] = "%?angle == 0.0"

    G.add_node("LayCarpetSubStep4", Dicts.ndRuleOutTrue)
    G.add_edge("LayCarpetSubStep4", "ProcessSubStep", Dicts.relIs)
    G.add_edge("LayCarpetSubStep4", "\"Lay the tiles\"", Dicts.relIn)
    G.add_edge("LayCarpetSubStep4", "CarpetingPattern", Dicts.relInput)
    G.add_edge("LayCarpetSubStep4", "Room", Dicts.relInput)
    G.add_edge("LayCarpetSubStep4", "Id", {Strings.captures: {
                                                            "name": {Strings.captureFrom: "CarpetingPattern"},
                                                            "id": {Strings.captureFrom: "Room"}
                                                         }})
    G.add_edge("LayCarpetSubStep4", "RotationAngle", {Strings.capture: "angle", Strings.captureFrom: "CarpetingPattern"})
    G.node["LayCarpetSubStep4"]["StepNumber"] = 3
    G.node["LayCarpetSubStep4"]["Instruction"] = "\"Turn tiles %?angle degrees from one another\""
    G.node["LayCarpetSubStep4"]["ProcessName"] = "Carpeting"
    G.node["LayCarpetSubStep4"]["ProcessStepId"] = "\"Lay the tiles\""
    G.node["LayCarpetSubStep4"]["ElementId"] = "%?id"
    G.node["LayCarpetSubStep4"]["Pattern"] = "%?name"
    G.node["LayCarpetSubStep4"][Strings.attrResultingCondition] = "%?angle != 0.0"

    G.add_node("LayCarpetSubStep5", Dicts.ndRuleOutTrue)
    G.add_edge("LayCarpetSubStep5", "ProcessSubStep", Dicts.relIs)
    G.add_edge("LayCarpetSubStep5", "\"Lay the tiles\"", Dicts.relIn)
    G.add_edge("LayCarpetSubStep5", "CarpetingPattern", Dicts.relInput)
    G.add_edge("LayCarpetSubStep5", "Room", Dicts.relInput)
    G.add_edge("LayCarpetSubStep5", "Id", {Strings.captures: {
                                                            "name": {Strings.captureFrom: "CarpetingPattern"},
                                                            "id": {Strings.captureFrom: "Room"}
                                                         }})
    G.add_edge("LayCarpetSubStep5", "ShiftRatio", {Strings.capture: "ratio", Strings.captureFrom: "CarpetingPattern"})
    G.add_edge("LayCarpetSubStep5", "ShiftDirection", {Strings.capture: "sd", Strings.captureFrom: "CarpetingPattern"})
    G.node["LayCarpetSubStep5"]["StepNumber"] = 4
    G.node["LayCarpetSubStep5"]["Instruction"] = "\"Offset tiles by %?ratio of a tile along the %?sd\""
    G.node["LayCarpetSubStep5"]["ProcessName"] = "Carpeting"
    G.node["LayCarpetSubStep5"]["ProcessStepId"] = "\"Lay the tiles\""
    G.node["LayCarpetSubStep5"]["ElementId"] = "%?id"
    G.node["LayCarpetSubStep5"]["Pattern"] = "%?name"
    G.node["LayCarpetSubStep5"][Strings.attrResultingCondition] = "%?ratio != 0.0"

    G.add_node("LayCarpetSubStep6", Dicts.ndRuleOutTrue)
    G.add_edge("LayCarpetSubStep6", "ProcessSubStep", Dicts.relIs)
    G.add_edge("LayCarpetSubStep6", "\"Lay the tiles\"", Dicts.relIn)
    G.add_edge("LayCarpetSubStep6", "CarpetingPattern", Dicts.relInput)
    G.add_edge("LayCarpetSubStep6", "Room", Dicts.relInput)
    G.add_edge("LayCarpetSubStep6", "Id", {Strings.captures: {
                                                            "name": {Strings.captureFrom: "CarpetingPattern"},
                                                            "id": {Strings.captureFrom: "Room"}
                                                         }})
    G.add_edge("LayCarpetSubStep6", "ShiftRatio", {Strings.capture: "ratio", Strings.captureFrom: "CarpetingPattern"})
    G.node["LayCarpetSubStep6"]["StepNumber"] = "%?ratio == 0.0 ? 4 : 5"
    G.node["LayCarpetSubStep6"]["Instruction"] = "\"Form the carpet row by row\""
    G.node["LayCarpetSubStep6"]["ProcessName"] = "Carpeting"
    G.node["LayCarpetSubStep6"]["ProcessStepId"] = "\"Lay the tiles\""
    G.node["LayCarpetSubStep6"]["ElementId"] = "%?id"
    G.node["LayCarpetSubStep6"]["Pattern"] = "%?name"

    G.add_node("LayCarpetSubStep7", Dicts.ndRuleOutTrue)
    G.add_edge("LayCarpetSubStep7", "ProcessSubStep", Dicts.relIs)
    G.add_edge("LayCarpetSubStep7", "\"Lay the tiles\"", Dicts.relIn)
    G.add_edge("LayCarpetSubStep7", "CarpetingPattern", Dicts.relInput)
    G.add_edge("LayCarpetSubStep7", "Room", Dicts.relInput)
    G.add_edge("LayCarpetSubStep7", "Id", {Strings.captures: {
                                                            "name": {Strings.captureFrom: "CarpetingPattern"},
                                                            "id": {Strings.captureFrom: "Room"}
                                                         }})
    G.add_edge("LayCarpetSubStep7", "ShiftRatio", {Strings.capture: "ratio", Strings.captureFrom: "CarpetingPattern"})
    G.node["LayCarpetSubStep7"]["StepNumber"] = "%?ratio == 0.0 ? 5 : 6"
    G.node["LayCarpetSubStep7"]["Instruction"] = "\"Cut tiles to fit around corners or in small areas\""
    G.node["LayCarpetSubStep7"]["ProcessName"] = "Carpeting"
    G.node["LayCarpetSubStep7"]["ProcessStepId"] = "\"Lay the tiles\""
    G.node["LayCarpetSubStep7"]["ElementId"] = "%?id"
    G.node["LayCarpetSubStep7"]["Pattern"] = "%?name"

    G.add_node("AdhereTilesSubStep1", Dicts.ndRuleOutTrue)
    G.add_edge("AdhereTilesSubStep1", "ProcessSubStep", Dicts.relIs)
    G.add_edge("AdhereTilesSubStep1", "\"Adhere the tiles\"", Dicts.relIn)
    G.add_edge("AdhereTilesSubStep1", "CarpetTile", Dicts.relInput)
    G.add_edge("AdhereTilesSubStep1", "Back", {Strings.capture: "back", Strings.captureFrom: "CarpetTile"})
    G.node["AdhereTilesSubStep1"]["StepNumber"] = 1
    G.node["AdhereTilesSubStep1"]["Instruction"] = "\"Peel the protective coating to reveal the sticky part\""
    G.node["AdhereTilesSubStep1"]["ProcessName"] = "Carpeting"
    G.node["AdhereTilesSubStep1"]["ProcessStepId"] = "\"Adhere the tiles\""
    G.node["AdhereTilesSubStep1"][Strings.attrResultingCondition] = "%?back == \"adhesive back\""
    G.node["AdhereTilesSubStep1"]["Pattern"] = "%?back"

    G.add_node("AdhereTilesSubStep2", Dicts.ndRuleOutTrue)
    G.add_edge("AdhereTilesSubStep2", "ProcessSubStep", Dicts.relIs)
    G.add_edge("AdhereTilesSubStep2", "\"Adhere the tiles\"", Dicts.relIn)
    G.add_edge("AdhereTilesSubStep2", "CarpetTile", Dicts.relInput)
    G.add_edge("AdhereTilesSubStep2", "Back", {Strings.capture: "back", Strings.captureFrom: "CarpetTile"})
    G.node["AdhereTilesSubStep2"]["StepNumber"] = 2
    G.node["AdhereTilesSubStep2"]["Instruction"] = "\"Press the tile into the floor\""
    G.node["AdhereTilesSubStep2"]["ProcessName"] = "Carpeting"
    G.node["AdhereTilesSubStep2"]["ProcessStepId"] = "\"Adhere the tiles\""
    G.node["AdhereTilesSubStep2"][Strings.attrResultingCondition] = "%?back == \"adhesive back\""
    G.node["AdhereTilesSubStep2"]["Pattern"] = "%?back"

    G.add_node("AdhereTilesSubStep3", Dicts.ndRuleOutTrue)
    G.add_edge("AdhereTilesSubStep3", "ProcessSubStep", Dicts.relIs)
    G.add_edge("AdhereTilesSubStep3", "\"Adhere the tiles\"", Dicts.relIn)
    G.add_edge("AdhereTilesSubStep3", "CarpetTile", Dicts.relInput)
    G.add_edge("AdhereTilesSubStep3", "Back", {Strings.capture: "back", Strings.captureFrom: "CarpetTile"})
    G.node["AdhereTilesSubStep3"]["StepNumber"] = 1
    G.node["AdhereTilesSubStep3"]["Instruction"] = "\" Swipe the glue on the floor where your carpet tile will go\""
    G.node["AdhereTilesSubStep3"]["ProcessName"] = "Carpeting"
    G.node["AdhereTilesSubStep3"]["ProcessStepId"] = "\"Adhere the tiles\""
    G.node["AdhereTilesSubStep3"][Strings.attrResultingCondition] = "%?back == \"dry back\""
    G.node["AdhereTilesSubStep3"]["Pattern"] = "%?back"

    G.add_node("AdhereTilesSubStep4", Dicts.ndRuleOutTrue)
    G.add_edge("AdhereTilesSubStep4", "ProcessSubStep", Dicts.relIs)
    G.add_edge("AdhereTilesSubStep4", "\"Adhere the tiles\"", Dicts.relIn)
    G.add_edge("AdhereTilesSubStep4", "CarpetTile", Dicts.relInput)
    G.add_edge("AdhereTilesSubStep4", "Back", {Strings.capture: "back", Strings.captureFrom: "CarpetTile"})
    G.node["AdhereTilesSubStep4"]["StepNumber"] = 2
    G.node["AdhereTilesSubStep4"]["Instruction"] = "\"spread an even coating over the surface where your carpet tile will go\""
    G.node["AdhereTilesSubStep4"]["ProcessName"] = "Carpeting"
    G.node["AdhereTilesSubStep4"]["ProcessStepId"] = "\"Adhere the tiles\""
    G.node["AdhereTilesSubStep4"][Strings.attrResultingCondition] = "%?back == \"dry back\""
    G.node["AdhereTilesSubStep4"]["Pattern"] = "%?back"

    return G

class Test_test_CLIPS_graph_parse(unittest.TestCase):
    def test_clips_graph_parse_smoke(self):
        """Checks number of deftemplates and facts in whole graph"""
        G = CreateTestCarpetingGraph()
        
        nlpGraphProcessor = NLPResultGraphParser()
        res = nlpGraphProcessor.ParseGraph(G)

        self.assertEqual(len(res.Deftemplates), 12)
        self.assertEqual(len(res.Deffacts), 23)
        self.assertEqual(len(res.Defrules), 12)
        self.assertEqual(len(res.GatheringFunctions), 3)

    def test_clips_deftemplate_parse_smoke(self):
        """Checks deftemplate parsed structures"""
        G = CreateTestCarpetingGraph()
        
        nlpGraphProcessor = NLPResultGraphParser()
        res = BLNlpClipsRuleBase()
        seen = []
        nlpGraphProcessor.ParseObject(G, Strings.ndStep, seen, res)
        nlpGraphProcessor.ParseObject(G, "CarpetingPattern", seen, res)
        nlpGraphProcessor.ParseObject(G, "ProcessSubStep", seen, res)

        # Deftemplate with part relation and extra fields
        template = next(t for t in res.Deftemplates if t.TemplateName == Strings.ndStep)
        self.assertTrue(template != None)
        self.assertEqual(len(template.Slots), 4)
        self.assertTrue(next(s for s in template.Slots if s.Name == "Id") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == "ProcessId") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == Strings.after) != None)

        # Deftemplate with several has relations
        template = next(t for t in res.Deftemplates if t.TemplateName == "CarpetingPattern")
        self.assertTrue(template != None)
        self.assertEqual(len(template.Slots), 4)
        self.assertTrue(next(s for s in template.Slots if s.Name == "Id") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == "RotationAngle") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == "ShiftDirection") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == "ShiftRatio") != None)

        # Deftemplate with in relation
        template = next(t for t in res.Deftemplates if t.TemplateName == "ProcessSubStep")
        self.assertTrue(template != None)
        self.assertEqual(len(template.Slots), 7)
        self.assertTrue(next(s for s in template.Slots if s.Name == "Id") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == "Instruction") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == "ProcessStepId") != None)
        self.assertTrue(next(s for s in template.Slots if s.Name == "StepNumber") != None)

    def test_clips_deffacts_parse_smoke(self):
        """Checks deffacts parsed structures"""
        G = CreateTestCarpetingGraph()
        
        nlpGraphProcessor = NLPResultGraphParser()
        res = BLNlpClipsRuleBase()
        seen = []
        nlpGraphProcessor.ParseObject(G, "\"Clear space\"", seen, res)
        nlpGraphProcessor.ParseObject(G, "Brick", seen, res)

        # Deffact with part relation and extra fields
        fact = next(df for df in res.Deffacts if df.HasFact("\"Clear space\""))
        self.assertTrue(fact != None)
        fact = fact.GetFact("\"Clear space\"")
        self.assertTrue("Id" in fact.SlotValues)
        self.assertTrue("ProcessId" in fact.SlotValues)
        self.assertTrue(Strings.after in fact.SlotValues)
        self.assertTrue(fact.Template.TemplateName == Strings.ndStep)
        self.assertTrue(fact.SlotValues["Id"] == "\"Clear space\"")
        self.assertTrue(fact.SlotValues["ProcessId"] == "Carpeting")
        self.assertTrue(fact.SlotValues[Strings.after] == "\"Choose a pattern\"")

        # Deffact with several has relations
        fact = next(df for df in res.Deffacts if df.HasFact("Brick"))
        self.assertTrue(fact != None)
        fact = fact.GetFact("Brick")
        self.assertTrue("Id" in fact.SlotValues)
        self.assertTrue("RotationAngle" in fact.SlotValues)
        self.assertTrue("ShiftDirection" in fact.SlotValues)
        self.assertTrue("ShiftRatio" in fact.SlotValues)
        self.assertTrue(fact.Template.TemplateName == "CarpetingPattern")
        self.assertTrue(fact.SlotValues["Id"] == "Brick")
        self.assertTrue(fact.SlotValues["RotationAngle"] == 0.0)
        self.assertTrue(fact.SlotValues["ShiftDirection"] == "Width")        
        self.assertTrue(fact.SlotValues["ShiftRatio"] == 0.5)   
        
    def test_clips_deftemplate_parse_text(self):
        """Checks deftemplate texts prodused during parsing"""
        G = CreateTestCarpetingGraph()
        
        nlpGraphProcessor = NLPResultGraphParser()
        res = BLNlpClipsRuleBase()
        seen = []
        nlpGraphProcessor.ParseObject(G, Strings.ndStep, seen, res)
        nlpGraphProcessor.ParseObject(G, "CarpetingPattern", seen, res)
        nlpGraphProcessor.ParseObject(G, "ProcessSubStep", seen, res)

        template = next(t for t in res.Deftemplates if t.TemplateName == Strings.ndStep)
        self.assertTrue(template != None)
        clipsText = template.ClipsConstruct()
        expTextLines = ["(deftemplate ProcessStep\n", "(slot Id)\n", "(slot ProcessId)\n", "(slot After)\n", "\n)"]
        for expLine in expTextLines:
            self.assertTrue(expLine in clipsText)

        template = next(t for t in res.Deftemplates if t.TemplateName == "CarpetingPattern")
        self.assertTrue(template != None)
        clipsText = template.ClipsConstruct()
        expTextLines = ["(deftemplate CarpetingPattern\n", "(slot RotationAngle)\n", "(slot ShiftRatio)\n", "(slot ShiftDirection)\n", "(slot Id)", "\n)"]
        for expLine in expTextLines:
            self.assertTrue(expLine in clipsText)

        template = next(t for t in res.Deftemplates if t.TemplateName == "ProcessSubStep")
        self.assertTrue(template != None)
        clipsText = template.ClipsConstruct()
        expTextLines = ["(deftemplate ProcessSubStep\n", "(slot StepNumber)\n", "(slot Instruction)\n", "(slot Id)\n", "(slot ProcessStepId)", "\n)"]
        for expLine in expTextLines:
            self.assertTrue(expLine in clipsText)

    def test_clips_deffacts_parse_text(self):
        """Checks deffacts texts prodused during parsing"""
        G = CreateTestCarpetingGraph()
        
        nlpGraphProcessor = NLPResultGraphParser()
        res = BLNlpClipsRuleBase()
        seen = []
        nlpGraphProcessor.ParseObject(G, "\"Clear space\"", seen, res)
        nlpGraphProcessor.ParseObject(G, "Brick", seen, res)

        fact = next(df for df in res.Deffacts if df.HasFact("\"Clear space\""))
        self.assertTrue(fact != None)
        clipsText = fact.ClipsConstruct()
        expTextLines = ["(deffacts ", "(ProcessStep ", "(ProcessId Carpeting ) ", "(Id \"Clear space\" ) ", "(after \"Choose a pattern\" ) ",")\n)"]
        for expLine in expTextLines:
            self.assertTrue(expLine in clipsText)

        fact = next(df for df in res.Deffacts if df.HasFact("Brick"))
        self.assertTrue(fact != None)
        clipsText = fact.ClipsConstruct()
        expTextLines = ["(deffacts", "(CarpetingPattern ", "(RotationAngle 0.0 ) ", "(ShiftDirection Width ) ", "(ShiftRatio 0.5 ) ", "(Id Brick ) ", ")\n)"]
        for expLine in expTextLines:
            self.assertTrue(expLine in clipsText)

    def test_clips_defrules_parse_smoke(self):
        """Checks defrules parsed structures"""
        G = CreateTestCarpetingGraph()
        
        nlpGraphProcessor = NLPResultGraphParser()
        res = BLNlpClipsRuleBase()
        seen = []

        nlpGraphProcessor.ParseObject(G, "LayCarpetSubStep5", seen, res)
        nlpGraphProcessor.ParseObject(G, "LayCarpetSubStep6", seen, res)

        for defrule in res.Defrules:
            if defrule.Name == "LayCarpetSubStep5":
                self.assertEqual(len(defrule.Conditions), 2)
                self.assertEqual(defrule.Name, "LayCarpetSubStep5")
                self.assertEqual(defrule.WholeOutputCondition, "(neq ?ratio 0.0)")
                self.assertEqual(len(defrule.ResolutionBinds), 0)
                self.assertEqual(len(defrule.OutputFacts), 1)
                
            elif defrule.Name == "LayCarpetSubStep6":
                self.assertEqual(len(defrule.Conditions), 2)
                self.assertEqual(defrule.Name, "LayCarpetSubStep6")
                self.assertEqual(defrule.WholeOutputCondition, "")
                self.assertEqual(len(defrule.ResolutionBinds), 2)
                self.assertEqual(len(defrule.OutputFacts), 1)

    def test_clips_defrules_parse_text(self):
        """Checks defrules texts produced from parsed structures"""
        G = CreateTestCarpetingGraph()
        
        nlpGraphProcessor = NLPResultGraphParser()
        res = BLNlpClipsRuleBase()
        seen = []

        nlpGraphProcessor.ParseObject(G, "LayCarpetSubStep5", seen, res)
        nlpGraphProcessor.ParseObject(G, "LayCarpetSubStep6", seen, res)

        for defrule in res.Defrules:
            text = defrule.ClipsConstruct()
            if defrule.Name == "LayCarpetSubStep5":
                self.assertTrue("(defrule LayCarpetSubStep5" in text)
                self.assertTrue("(Room (Id ?id) )" in text)
                self.assertTrue("(CarpetingPattern " in text)
                self.assertTrue("(ShiftRatio ?ratio) " in text)
                self.assertTrue("(ShiftDirection ?sd) " in text)
                self.assertTrue("(Id ?name) " in text)
                self.assertTrue("(if (neq ?ratio 0.0)" in text)
                self.assertTrue("(assert (ProcessSubStep " in text)
                self.assertTrue("(Instruction (str-cat (str-cat (str-cat \"Offset tiles by \" ?ratio ) \" of a tile along the \" ) ?sd )  ) " in text)
                self.assertTrue("(Pattern ?name ) " in text)
                self.assertTrue("(ProcessName Carpeting ) " in text)
                self.assertTrue("(StepNumber 4 ) " in text)
                self.assertTrue("(ElementId ?id ) " in text)
                self.assertTrue("(ProcessStepId \"Lay the tiles\" ) " in text)
                
            elif defrule.Name == "LayCarpetSubStep6":
                self.assertTrue("(defrule LayCarpetSubStep6" in text)
                self.assertTrue("(Room (Id ?id) )" in text)
                self.assertTrue("(CarpetingPattern " in text)
                self.assertTrue("(ShiftRatio ?ratio) " in text)
                self.assertTrue("(Id ?name) " in text)
                self.assertTrue("=>" in text)
                self.assertTrue("(bind ?BindedVariable1  5)" in text)
                self.assertTrue("(if (eq ?ratio 0.0 )" in text)
                self.assertTrue("(bind ?BindedVariable1  4 ))" in text)                
                self.assertTrue("(assert (ProcessSubStep " in text)
                self.assertTrue("(Instruction \"Form the carpet row by row\" ) " in text)
                self.assertTrue("(Pattern ?name ) " in text)
                self.assertTrue("(ProcessName Carpeting ) " in text)
                self.assertTrue("(StepNumber ?BindedVariable1 ) " in text)
                self.assertTrue("(ElementId ?id ) " in text)
                self.assertTrue("(ProcessStepId \"Lay the tiles\" ) " in text)


if __name__ == '__main__':
    unittest.main()
