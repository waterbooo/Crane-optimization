"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

import urllib.request, codecs, sys, logging

from flask import Flask, jsonify
from flask import request

# Install from https://pypi.python.org/pypi/grpcio/1.0.0
# and https://pypi.python.org/pypi/protobuf/3.0.0
import grpc

import time, numpy as np
from threading import Thread
from flask import render_template, session, abort
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from Optimization.Positions.PrefabCranePositionOptimizer import CranePositionOptimizationGA, CraneEvaluator, GetAnimation
from Optimization.Positions.PrefabCranePositionSensitivity import CranePositionSensitivity

from Optimization.DataStructures.SiteData import SiteData
from Optimization.DataStructures.CraneData import CraneData
from Optimization.Order.ConstructionOrdering import ConstructionOrdering
from Optimization.Order.BarDependencyChecker import BarDependencyChecker
from Optimization.Order.PanelDependencyChecker import PanelDependencyChecker

import auth_pb2
import optimization_pb2

from concurrent import futures

from EndpointConstants import EndpointConstants as ec
from EndpointUtils import EndpointUtils as eutils

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

# Uncomment to turn on debug output
#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class OptimizationWithRatesServicer(optimization_pb2.OptimizationWithRatesServicer):
    """Wraps the gRPC methods"""

    def __init__(self):
        pass

    def MobileCranePanelInstallation(self, query, context):
        craneDollarHour = query.installationRates.craneHourlyRate.value
        laborDollarHour = query.installationRates.laborHourlyRate.value
        panelInstallationSeconds = query.installationRates.panelInstallationTime.value
        takeDownTimeSeconds = query.installationRates.takeDownTime.value

        numberOfCranes = query.craneParameters.numberOfCranes

        craneBoomLength = query.craneParameters.boomLength
        craneMovementSpeed = query.craneParameters.movementSpeed
        craneBoomRotationSpeed = query.craneParameters.boomRotationSpeed
        craneBoomExtensionSpeed = query.craneParameters.boomExtensionSpeed
        craneBoomSlewSpeed = query.craneParameters.boomSlewSpeed

        craneMaxCapacity = query.craneParameters.maxCapacity
        
        timeHours, costDollars = CraneEvaluator(craneDollarHour, laborDollarHour, 
            panelInstallationSeconds, takeDownTimeSeconds,
            numberOfCranes, craneBoomLength, craneMovementSpeed,
            craneBoomRotationSpeed, craneBoomExtensionSpeed,
            craneBoomSlewSpeed, craneMaxCapacity)

        tt = optimization_pb2.UnitDouble(unit="Hour", value=timeHours)
        tc = optimization_pb2.UnitDouble(unit="$", value=costDollars)

        return optimization_pb2.ConstructionMetrics(totalTime=tt, totalCost=tc)

# setup GRPC
def setup_grpc():
    print("starting grpc")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    optimization_pb2.add_OptimizationWithRatesServicer_to_server(
        OptimizationWithRatesServicer(), server)

    server.add_insecure_port('[::]:50051')
    server.start()

    return server

gRPCServer = setup_grpc()

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

import os, sys, json
__filePath = os.path.dirname(os.path.abspath(__file__))

# Get dependent module paths in
__CLIPSPath = os.path.join(__filePath, "CLIPSWrapper")
if not __CLIPSPath in sys.path:
    sys.path.insert(1, __CLIPSPath)

__AMPath = os.path.join(__filePath, "Model")
if not __AMPath in sys.path:
    sys.path.insert(1, __AMPath)

__CTPath = os.path.join(__AMPath, "CLIPSTransform")
if not __CTPath in sys.path:
    sys.path.insert(1, __CTPath)

__ParsersPath = os.path.join(__filePath, "Parsers")
if not __ParsersPath in sys.path:
    sys.path.insert(1, __ParsersPath)

__COPath = os.path.join(__filePath, "ConstructionObjects")
if not __COPath in sys.path:
    sys.path.insert(1, __COPath)

__KBLMPath = os.path.join(__filePath, "KBDataManagement")
if not __KBLMPath in sys.path:
    sys.path.insert(1, __KBLMPath)

#=====================      HTTP       ==========================   
#---------------------- OPTIMIZATION ----------------------------
@app.route("/prefab/cranes/optposition", methods=["POST"])
def calc_crane_optimal_position():
    """Runs GA for crane points optimal positions"""
    try:
        # Check if JSON is valid
        if not request.json or not ec.TagCraneOptModelData in request.json or not ec.TagCraneOptCranes in request.json:
            abort(400)

        pm, surroundingPolygons, sitePolygons = eutils.ParseModelFromJson(request)

        # Run optimization process
        res = CranePositionOptimizationGA(pm, request.json[ec.TagCraneOptCranes], surroundingPolygons=surroundingPolygons, sitePolygons=sitePolygons)

        # Return crane position and  point
        numCranes = len(res[ec.OutTagCraneOptBestPositions]) // 4
        retObj = [{ec.OutTagCraneOptCranePos: {ec.OutTagCraneOptX: res[ec.OutTagCraneOptBestPositions][i * 2], 
                                                    ec.OutTagCraneOptY: res[ec.OutTagCraneOptBestPositions][i * 2 + 1]},
                        ec.OutTagCraneOptSupplyPos: {ec.OutTagCraneOptX: res[ec.OutTagCraneOptBestPositions][numCranes * 2 + i * 2],
                                                     ec.OutTagCraneOptY:res[ec.OutTagCraneOptBestPositions][numCranes * 2 + i * 2 + 1]}} for i in range(numCranes)]
        return jsonify( {ec.OutTagCraneOptCranes: retObj, ec.OutTagCraneOptTime: res[ec.OutTagCraneOptTime] }), 200
    except Exception as e:
        print(e)
        abort(500)

@app.route("/prefab/cranes/comparedtimepositions", methods=["POST"])
def calc_crane_optimal_position_comparison():
    """Runs GA for optimal positions of passed cranes and proportionally icreased amount of used cranes"""
    try:
        if not request.json or not ec.TagCraneOptModelData in request.json or not ec.TagCraneOptCranes in request.json:
            abort(400)

        minamount = 1
        maxamount = 1
        if ec.ArgCraneOptMinAmount in request.args:
            minamount = int(request.args.get(ec.ArgCraneOptMinAmount, 1))
        if ec.ArgCraneOptMaxAmount in request.args:
            maxamount = int(request.args.get(ec.ArgCraneOptMaxAmount, 1))

        if maxamount < minamount:
            maxamount = minamount
    
        # Surrounding polygons are polygons of buildings which limit crane (not used for now)
        surroundingPolygons = []
        if ec.TagCraneOptSurroundingPolygons in request.json:
            surroundingPolygons = request.json[ec.TagCraneOptSurroundingPolygons]

        # Site polygons are polygons of the site in same coordinate system as bar data
        sitePolygons = []
        if ec.TagCraneOptSitePolygons in request.json:
            sitePolygons = request.json[ec.TagCraneOptSitePolygons]

        # Parse project model
        client = ""
        if ec.ArgCraneOptClient in request.args:
            client = request.args.get(ec.ArgCraneOptClient, ec.ValCommonClientAdvanceSteel)
        parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
        pm = parser.ParseProjectModel(request.json[ec.TagCraneOptModelData])

        # Parse crane data
        origCranes = []
        for crData in request.json[ec.TagCraneOptCranes]:
            crane = eutils.GetCraneByType(crData)
            origCranes.append(crane)

        results = {}
        for j in range(maxamount - minamount + 1):
            cranes = origCranes * (minamount + j)
            # Run optimization process
            res = CranePositionOptimizationGA(pm, cranes, surroundingPolygons=surroundingPolygons, sitePolygons=sitePolygons)

            # Return crane position and supply point
            numCranes = len(res[ec.OutTagCraneOptBestPositions]) // 4
            retObj = [{ec.OutTagCraneOptCranePos: {ec.OutTagCraneOptX: res[ec.OutTagCraneOptBestPositions][i * 2], 
                                                        ec.OutTagCraneOptY: res[ec.OutTagCraneOptBestPositions][i * 2 + 1]},
                            ec.OutTagCraneOptSupplyPos: {ec.OutTagCraneOptX: res[ec.OutTagCraneOptBestPositions][numCranes * 2 + i * 2],
                                                         ec.OutTagCraneOptY:res[ec.OutTagCraneOptBestPositions][numCranes * 2 + i * 2 + 1]}} for i in range(numCranes)]
            results[numCranes] = {ec.OutTagCraneOptCranes: retObj, ec.OutTagCraneOptTime: res[ec.OutTagCraneOptTime] }
        return jsonify(results), 200
    except Exception as e:
        print(e)
        abort(500)

@app.route("/prefab/model/buildorder", methods=["POST"])
def calc_model_buildorder():
    """Generates pre-order for building whole structure"""
    # Check whether model data is in input
    if not request.json or not ec.TagCraneOptModelData in request.json:
        abort(400)

    # Parse project model from JSON
    client = ""
    if ec.ArgCraneOptClient in request.args:
        client = request.args.get(ec.ArgCraneOptClient, ec.ValCommonClientAdvanceSteel)
    parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
    pm = parser.ParseProjectModel(request.json[ec.TagCraneOptModelData])
    modelData = SiteData(pm, [])

    # Build model dependency graph
    BarDependencyChecker.buildDependencyGraph(modelData)
    PanelDependencyChecker.buildDependencyGraph(modelData)

    # Get construction order usin the graph
    res = ConstructionOrdering.getConstructionOrder(modelData.dependencies, modelData.ConstructionObjects.values())

    # Return order
    return jsonify({ec.OutTagConstrOrderOrder: res}), 200

@app.route("/prefab/model/buildordermult_bo", methods=["GET"])
def calc_model_buildordermult_bo():
    """not working"""
    """Generates pre-order for building whole structure with multiple cranes data"""
    import json

    # default installation time 1.5 minutes
    installationTime = 1.5

    # load the base JSON
    baseModel = None
    reader = codecs.getreader("utf-8")
    file_name=os.path.normpath("c:/dev/BuildOptimizer/PrefabOptimizationServer/PrefabOptimizationServer/Tests/model.json")
        
    with open(file_name, encoding='utf-8-sig') as data_file: 
        baseModel = json.loads(data_file.read())
    # Get arguments
    numCranes = 1

    # Parse project model from JSON
    client = ""
    parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
    pm = parser.ParseProjectModel(baseModel[ec.TagCraneOptStructureData])
    modelData = SiteData(pm, [])

    # Build model bars dependency graph
    BarDependencyChecker.buildDependencyGraph(modelData)
    PanelDependencyChecker.buildDependencyGraph(modelData)

    # Get construction order usin the graph
    res = ConstructionOrdering.GetConstructionOrderMult(modelData.dependencies, modelData.ConstructionObjects.values(), numCranes)

    # Return order
    return jsonify({ec.OutTagConstrOrderOrder: res}), 200


@app.route("/prefab/model/buildordermult", methods=["POST"])
def calc_model_buildordermult():
    """Generates pre-order for building whole structure with multiple cranes data"""
    # Check whether model data is in input
    if not request.json or not ec.TagCraneOptModelData in request.json:
        abort(400)
    
    # Get arguments
    numCranes = 1
    if ec.ArgConstrOrderNumFlows in request.args:
        numCranes = int(request.args.get(ec.ArgConstrOrderNumFlows, 1))

    # Parse project model from JSON
    client = ""
    if ec.ArgCraneOptClient in request.args:
        client = request.args.get(ec.ArgCraneOptClient, ec.ValCommonClientAdvanceSteel)
    parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
    pm = parser.ParseProjectModel(request.json[ec.TagCraneOptModelData])
    modelData = SiteData(pm, [])

    # Build model bars dependency graph
    BarDependencyChecker.buildDependencyGraph(modelData)
    PanelDependencyChecker.buildDependencyGraph(modelData)

    # Get construction order usin the graph
    res = ConstructionOrdering.GetConstructionOrderMult(modelData.dependencies, modelData.ConstructionObjects.values(), numCranes)

    # Return order
    return jsonify({ec.OutTagConstrOrderOrder: res}), 200

@app.route("/prefab/model/buildordermultcluster", methods=["POST"])
def calc_model_buildordercluster():
    """Generates pre-order for building whole structure with clustering bars between multiple cranes"""
    # Check whether model data is in input
    if not request.json or not ec.TagCraneOptModelData in request.json or not ec.TagCraneOptCranes in request.json:
        abort(400)

    # Parse project model from JSON
    client = ""
    if ec.ArgCraneOptClient in request.args:
        client = request.args.get(ec.ArgCraneOptClient, ec.ValCommonClientAdvanceSteel)
    parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
    pm = parser.ParseProjectModel(request.json[ec.TagCraneOptModelData])
    cranes = [eutils.GetCraneByType(crane) for crane in request.json[ec.TagCraneOptCranes]]
    modelData = SiteData(pm, cranes)

    # Build model bars dependency graph
    BarDependencyChecker.buildDependencyGraph(modelData)
    PanelDependencyChecker.buildDependencyGraph(modelData)

    # Do bars clustering
    from Optimization.Clustering.KMeansBasedBarsDivision import KMeansBasedBarsDivision
    clusterer = KMeansBasedBarsDivision()
    centers = [np.array([bar.CenterPoint.X, bar.CenterPoint.Y]) for bar in pm.SteelAnalyticalModel.Bars.values()]
    clusterer.ProhibitedRegion = modelData.ModelPolygon
    clusterer.Radiuses = [cr.maxLength for cr in cranes]
    resClustering = clusterer.FindCenters(centers, len(cranes))

    # Get construction order usin the graph
    res = ConstructionOrdering.GetConstructionOrderClustered(modelData.dependencies, list(modelData.ConstructionObjects.values()), resClustering[2])

    # Return order
    return jsonify({ec.OutTagConstrOrderOrder: res}), 200

@app.route("/prefab/model/buildorderanimation", methods=["POST"])
def calc_model_buildorderanimation():
    """Takes model and return animation for it"""
    try:
        # Check if JSON is valid
        if not request.json or not ec.TagCraneOptModelData in request.json or not ec.TagCraneOptCranes in request.json:
            abort(400)

        pm, surroundingPolygons, sitePolygons = eutils.ParseModelFromJson(request)

        RawCranes=[]
        if ec.TagCraneOptCranes in request.json:
            RawCranes = request.json[ec.TagCraneOptCranes]
        cranes=[]
        for c in RawCranes:
            cranes.append(eutils.GetCraneByType(c))

        results = GetAnimation(pm, cranes, surroundingPolygons, sitePolygons)

        return jsonify(results), 200
    except Exception as e:
        print(e)
        abort(500)

#------------------------------- CLIPS --------------------------------
@app.route("/buildlogic/clips/recommendations", methods=["POST"])
def get_clips_recommendations():
    """Takes model, selected trades and client id
       Runs CLIPS engine
       Wraps results from CLIPS engine into output structures
    """
    try:
        # Get arguments
        if not request.json or not ec.TagCraneOptModelData in request.json:
            abort(400)

        client = request.args.get(ec.ArgCLIPSRecommendClient, "")
        trades = None
        if ec.ArgCLIPSRecommendTrades in request.args:
            trades = request.args.get(ec.ArgCLIPSRecommendTrades, [])
            if not isinstance(trades, list):
                trades = trades.split(",")
        
        # Parse model
        model = {}
        from Parsers.RevitModelParser import RevitModelParser
    
        if len(client) == 0 or client.lower() == ec.ArgValCLIPSRecommendRevit:
            parser = RevitModelParser()
            model = parser.ParseProjectModel(request.json[ec.TagCraneOptModelData])
        from PrefabCLIPSProcessor import PrefabCLIPSProcessor
        cp = PrefabCLIPSProcessor()

        # Get rules and pre-defined facts for env
        from KBRulesLoader import KBRulesLoader
        kbrl = KBRulesLoader()
        ruleFiles = kbrl.ListOfRuleFilesForTrades(trades)
        from ModelConstants import ModelConstants
        
        # Get model facts generation options
        from TradesByObjectChecker import TradesByObjectChecker
        checker = TradesByObjectChecker()
        from BLClipsTransformOptions import BLClipsTransformOptions
        stOptions = BLClipsTransformOptions()
        stOptions.Trades = trades
        stOptions.Mappings = checker.GetClipsMappingForTrades(trades)

        # Run Clips and get results
        res = cp.RunCLIPSForModelWithSetOfRuleFacts(model, ruleFiles, stOptions)

        # Delete temp file
        for tmpFile in ruleFiles[ec.TagCLIPSRecommendTmps]:
            os.remove(tmpFile[ec.TagCLIPSRecommendTmp])
        return jsonify({ec.TagCLIPSRecommendResults: res}), 200
    except Exception as e:
        print(e)
        abort(500)

@app.route("/buildlogic/clips/trades", methods=["GET"])
def get_available_trades():
    """Takes client and names of objects available in model
       Returns applicable trades and all possible trades lists
    """
    try:
        # Get arguments
        client = request.args.get(ec.ArgCLIPSRecommendClient, "")
        objects = request.args.get(ec.ArgCLIPSRecommendObjects, [])
        if not isinstance(objects, list):
            objects = objects.split(",")
        
        # Get trades for given objects and all available trades
        from TradesByObjectChecker import TradesByObjectChecker
        checker = TradesByObjectChecker()
        trades = checker.GetTradesForClientObjects(objects, client.lower())
        allTrades = checker.GetAllTrades()

        # Return trades to user

        return jsonify({ec.OutTagCLIPSRecommendTrades: trades, ec.OutTagCLIPSRecommendAllTrades: allTrades}), 200
    except Exception as e:
        print(e)
        abort(500)


def mobileCraneOpt(numberOfRun,crane_type,number_of_stop,installMethod,numCrew,workerPerCrew):
    try:
        import json
        from pprint import pprint

        # load the base JSON
        baseModel = None
        reader = codecs.getreader("utf-8")

        if crane_type is 1:
            file_name=os.path.normpath("C:/dev/BuildLogic/BuildOptimizer/PrefabOptimizationServer/PrefabOptimizationServer/Tests/testCase_deck_disney.json")
        elif crane_type is 2:
            file_name=os.path.normpath("C:/dev/BuildLogic/BuildOptimizer/PrefabOptimizationServer/PrefabOptimizationServer/Tests/testCase_truck_disney.json")

        # default installation time 1.5 minutes
        if workerPerCrew ==2:
            installationTime=12
        elif workerPerCrew==4:
            installationTime=6

        Algorithm='GA'

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
        
        RawCranes=[]
        if ec.TagCraneOptCranes in baseModel:
            RawCranes = baseModel[ec.TagCraneOptCranes]
        cranes=[]
        
        for c in RawCranes:
            if not isinstance(c, CraneData):
                cranes.append(eutils.GetCraneByType(c))
            else:
                cranes.append(c)
        
       # model data
        client = ""
        parser = eutils.GetParserByClientType(client, ec.ValCommonClientRevit)
        pm=[]
        if ec.TagCraneOptAnalyticalModel in baseModel:
            pm = parser.ParseProjectModel(baseModel)
            pm_panel=pm.SteelAnalyticalModel.Panels

        # Surrounding polygons are polygons of buildings which limit crane (not used for now)

        surroundingPolygons = []
        if ec.TagCraneOptSurroundingPolygons in baseModel:
            surroundingPolygons = baseModel[ec.TagCraneOptSurroundingPolygons]

        # Site polygons are polygons of the site in same coordinate system as bar data
        sitePolygons = []
        if ec.TagCraneOptSitePolygons in baseModel:
            sitePolygons = baseModel[ec.TagCraneOptSitePolygons]

        # Run optimization process
       
        results=[]
        for iterNum in range(numberOfRun):
            for i in range(len(cranes)):
                res = CranePositionOptimizationGA(iterNum,pm, [cranes[i]], visualize=False, hofUpdateCallback=None,  surroundingPolygons=surroundingPolygons, sitePolygons=sitePolygons,\
                    installationTime=installationTime,Algorithm=Algorithm,number_of_stop=number_of_stop,installMethod=installMethod,\
                    numCrew=numCrew,crane_type=crane_type,worker_per_crew=workerPerCrew)
                results.append(res)
        
        return results

    except Exception as e:
        print(e)
        abort(500)



# the following part is a parametric study:

#crane_type=[1,2]
#number_of_stop=[8,8,4]
#installMethod=[0,1,2]
#numCrew=[1,2]
#workerPerCrew=[2,4]
#numberOfRun=1

# sensitivity
crane_type=[1]
number_of_stop=[4]
installMethod=[0]
numCrew=[1]
workerPerCrew=[2]
numberOfRun=1

results=np.zeros((len(crane_type),len(installMethod),len(numCrew),len(workerPerCrew),numberOfRun))
for ct in range(len(crane_type)):
    for im in range(len(installMethod)):
        for nc in range(len(numCrew)):
            for wpc in range(len(workerPerCrew)):
                res=mobileCraneOpt(numberOfRun,crane_type[ct],[number_of_stop[ct]],installMethod[im],numCrew[nc],workerPerCrew[wpc])
                results[ct][im][nc][wpc][:]=[r['time'] for r in res]

for ct in range(len(crane_type)):
    for im in range(len(installMethod)):
        for nc in range(len(numCrew)):  
            for wpc in range(len(workerPerCrew)):
                print('crane_type:'+str(ct)+'. installationMethod:'+str(installMethod[im])+'. numberOfCrew:'+str(numCrew[nc])+' .workerPerCrew:'+str(workerPerCrew[wpc]))
                print( results[ct][im][nc][wpc])  
"""   
                

def mobileCraneSens(numberOfRun,crane_type,number_of_stop,installMethod,numCrew,workerPerCrew):
    try:
        import json
        from pprint import pprint

        # load the base JSON
        baseModel = None
        reader = codecs.getreader("utf-8")

        if crane_type is 1:
            file_name=os.path.normpath("C:/dev/BuildLogic/BuildOptimizer/PrefabOptimizationServer/PrefabOptimizationServer/Tests/testCase_deck_disney.json")
        elif crane_type is 2:
            file_name=os.path.normpath("C:/dev/BuildLogic/BuildOptimizer/PrefabOptimizationServer/PrefabOptimizationServer/Tests/testCase_truck_disney.json")

        # default installation time 1.5 minutes
        if workerPerCrew ==2:
            installationTime=12
        elif workerPerCrew==4:
            installationTime=6

        Algorithm='GA'

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
        
        RawCranes=[]
        if ec.TagCraneOptCranes in baseModel:
            RawCranes = baseModel[ec.TagCraneOptCranes]
        cranes=[]
        
        for c in RawCranes:
            if not isinstance(c, CraneData):
                cranes.append(eutils.GetCraneByType(c))
            else:
                cranes.append(c)
        
       # model data
        client = ""
        parser = eutils.GetParserByClientType(client, ec.ValCommonClientRevit)
        pm=[]
        if ec.TagCraneOptAnalyticalModel in baseModel:
            pm = parser.ParseProjectModel(baseModel)
            pm_panel=pm.SteelAnalyticalModel.Panels

        # Surrounding polygons are polygons of buildings which limit crane (not used for now)

        surroundingPolygons = []
        if ec.TagCraneOptSurroundingPolygons in baseModel:
            surroundingPolygons = baseModel[ec.TagCraneOptSurroundingPolygons]

        # Site polygons are polygons of the site in same coordinate system as bar data
        sitePolygons = []
        if ec.TagCraneOptSitePolygons in baseModel:
            sitePolygons = baseModel[ec.TagCraneOptSitePolygons]

        # Run optimization process
       
        results=[]
        for iterNum in range(numberOfRun):
            for i in range(len(cranes)):
                res = CranePositionSensitivity(iterNum,pm, [cranes[i]], visualize=False, hofUpdateCallback=None,  surroundingPolygons=surroundingPolygons, sitePolygons=sitePolygons,\
                    installationTime=installationTime,Algorithm=Algorithm,number_of_stop=number_of_stop,installMethod=installMethod,\
                    numCrew=numCrew,crane_type=crane_type,worker_per_crew=workerPerCrew)
                results.append(res)
        
        return results

    except Exception as e:
        print(e)
        abort(500)

# sensitivity
crane_type=[2]
number_of_stop=[2]
installMethod=[0,1,2]
numCrew=[1,2]
workerPerCrew=[2,4]
numberOfRun=1

results=np.zeros((len(crane_type),len(installMethod),len(numCrew),len(workerPerCrew),numberOfRun))
for ct in range(len(crane_type)):
    for im in range(len(installMethod)):
        for nc in range(len(numCrew)):
            for wpc in range(len(workerPerCrew)):
                res=mobileCraneSens(numberOfRun,crane_type[ct],[number_of_stop[ct]],installMethod[im],numCrew[nc],workerPerCrew[wpc])
                results[ct][im][nc][wpc][:]=res 

print (results)
"""

#------------------------  INSTALLATION TIME  ------------------------------
@app.route("/installation-time", methods=["GET"])
def get_installation_time():
    """
    Takes parameters encoded in the URL, and returns the installation time
    """

    print('Request args are ' + str(request.args))

    try:
        # Get arguments
        numCranes = 1
        if ec.ArgNumCranes in request.args:
            numCranes = int(request.args.get(ec.ArgNumCranes, 1))

        craneRotationSpeed = 0.9
        if ec.ArgCraneRotationSpeed in request.args:
            craneRotationSpeed = float(request.args.get(ec.ArgCraneRotationSpeed, 1))

        craneTrolleySpeed = 290
        if ec.ArgCraneTrolleySpeed in request.args:
            craneTrolleySpeed = float(request.args.get(ec.ArgCraneTrolleySpeed, 1))

        craneMaxHookRadius = 164
        if ec.ArgCraneMaxHookRadius in request.args:
            craneMaxHookRadius = float(request.args.get(ec.ArgCraneMaxHookRadius, 1))

        # default installation time 1.5 minutes
        installationTime = 1.5
        if ec.ArgInstallTime in request.args:
            installationTime = float(request.args.get(ec.ArgInstallTime, 1))

        ##############################
        ## BROKEN
        ##############################
        numSteelElements = 1
        if ec.ArgNumSteelElements in request.args:
            numSteelElements = int(request.args.get(ec.ArgNumSteelElements, 1))

        buildingShape = "default"
        if ec.ArgBuildingShape in request.args:
            buildingShape = request.args.get(ec.ArgBuildingShape, 1)

        # TODO: figure out units
        minPerimeterDist = 10
        if ec.ArgMinPerimeterDist in request.args:
            minPerimeterDist = int(request.args.get(ec.ArgMinPerimeterDist, 1))

        # TODO Expose
        supplyPointDist = 200
        if ec.ArgSupplyPointDist in request.args:
            supplyPointDist = int(request.args.get(ec.ArgSupplyPointDist, 1))

        # if there's more than one crane, then the acceptiable region is not calculated or considered

        # load the base JSON
        baseModelText = ""
        baseModel = None
        with urllib.request.urlopen('https://s3-us-west-2.amazonaws.com/cranesimulation-content/optimization_server_input_JSON/testModelDataWithOneCrane2.json') as response:
            reader = codecs.getreader("utf-8")
            baseModel = json.load(reader(response))

        # Surrounding polygons are polygons of buildings which limit crane (not used for now)
        surroundingPolygons = []
        if ec.TagCraneOptSurroundingPolygons in baseModel:
            surroundingPolygons = baseModel[ec.TagCraneOptSurroundingPolygons]

        # Site polygons are polygons of the site in same coordinate system as bar data
        sitePolygons = []
        if ec.TagCraneOptSitePolygons in baseModel:
            sitePolygons = baseModel[ec.TagCraneOptSitePolygons]

        client = ""
        if ec.ArgCraneOptClient in request.args:
            client = request.args.get(ec.ArgCraneOptClient, ec.ValCommonClientAdvanceSteel)
        parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
        pm = parser.ParseProjectModel(baseModel[ec.TagCraneOptModelData])

        cranes = baseModel[ec.TagCraneOptCranes]

        cranes[0]["metadata"]["initIndividualOneCraneations"]["speeds"]["rotation"]["speed"] = craneRotationSpeed
        cranes[0]["metadata"]["specifications"]["speeds"]["trolley"]["speed"] = craneTrolleySpeed

        if craneMaxHookRadius > 164:
            lengthInt = int(craneMaxHookRadius) + 1
            lengthString = str(lengthInt)
            cranes[0]["metadata"]["specifications"]["limitations"]["radius-capacity"][lengthString] = 4850

        for i in range(0, numCranes - 1):
            cranes.append(cranes[0])
        
        # Run optimization process
        res = CranePositionOptimizationGA(pm, cranes, surroundingPolygons=surroundingPolygons, sitePolygons=sitePolygons, installationTime=installationTime)

        # Return crane position and supply point
        numCranes = len(res[ec.OutTagCraneOptBestPositions]) // 4
        retObj = [{ec.OutTagCraneOptCranePos: {ec.OutTagCraneOptX: res[ec.OutTagCraneOptBestPositions][i * 2], 
                                                    ec.OutTagCraneOptY: res[ec.OutTagCraneOptBestPositions][i * 2 + 1]},
                        ec.OutTagCraneOptSupplyPos: {ec.OutTagCraneOptX: res[ec.OutTagCraneOptBestPositions][numCranes * 2 + i * 2],
                                                     ec.OutTagCraneOptY:res[ec.OutTagCraneOptBestPositions][numCranes * 2 + i * 2 + 1]}} for i in range(numCranes)]
        return jsonify( {ec.OutTagCraneOptCranes: retObj, ec.OutTagCraneOptTime: res[ec.OutTagCraneOptTime] }), 200

    except Exception as e:
        print(e)
        abort(500)


#------------------------  TASKS  --------------------------------
@app.route("/pushtasks", methods=["POST"])
def push_tasks():
    # Get arguments
    if not request.json:
        return "Content type is not JSON", 400

    if not "graph" in request.json:
        return "JSON does not contain a graph object", 400

    println("about to make graph", file=sys.stderr)

    from NLPDataProcessing.NLPGraphProcessingUtils import NLPGraphProcessingUtils as nlpUtils
    from Model.Task import Task

    #G = nlpUtils.LoadGraphFromContents(request.json)
    try:
        # Get arguments
        # Project id is now set to 197 as a sample one id.
        # TODO: provide real id for the project
        projectId = "197"
        if ec.ArgTasksProjectId in request.args:
            projectId = request.args.get(ec.ArgTasksProjectId, projectId)

        G = nlpUtils.LoadGraphFromDynamoContentsJson(request.json)
        tasks = Task.ParseTasksFromGraph(G)
        tobjs = [{"name": task.name, "properties": task.properties} for task in tasks]
        Task.SendTasksToAPIServer(projectId, tobjs) 
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        print(e)
        return e, 500

@app.route("/groupordertasks", methods=["POST"])
def get_ordered_tasks():
    # Get arguments
    if not request.json:
        abort(400)

    from NLPDataProcessing.NLPGraphProcessingUtils import NLPGraphProcessingUtils as nlpUtils
    from Model.Task import Task

    # Get arguments
    # Project id is now set to 197 as a sample one id.
    # TODO: provide real id for the project
    projectId = "197"
    if ec.ArgTasksProjectId in request.args:
        projectId = request.args.get(ec.ArgTasksProjectId, "197")

    res = {}
    KBTasks = Task.GetTasksFromAPIServer(projectId)
    if KBTasks:
        MappedTasks = Task.MapFusionToKB(KBTasks, request.json)
    return jsonify({"order": MappedTasks}), 200

#------------------------  GENERAL  ------------------------------
@app.route("/")
def hello():
    """Renders a sample page."""
    return "Prefab optimization server"

#===================    WEB-SOCKETS.IO    ===========================
@socketio.on(ec.EventConnect, namespace=ec.NamespaceCranes)
def cranes_connect():
    """Listener for connection to cranes namespace"""
    emit(ec.MOutPrefabResponse, {ec.MOutArgData: ec.MRespCCranesConnected, ec.MOutArgCount: 0})

@socketio.on(ec.EventJoin, namespace=ec.NamespaceCranes)
def join(message):
    """Listener for socket room joining"""
    join_room(message[ec.MArgRoom])
    session[ec.SArgReceivedCount] = session.get(ec.SArgReceivedCount, 0) + 1
    emit(ec.MOutPrefabResponse,
         {ec.MOutArgData: "In rooms: " + ", ".join(rooms()),
          ec.MOutArgCount: session[ec.SArgReceivedCount]})

@socketio.on(ec.EventLeave, namespace=ec.NamespaceCranes)
def leave(message):
    """Listener for socket room leaving"""
    leave_room(message[ec.MArgRoom])
    session[ec.SArgReceivedCount] = session.get(ec.SArgReceivedCount, 0) + 1
    emit(ec.MOutPrefabResponse,
         {ec.MOutArgData: "In rooms: " + ", ".join(rooms()),
          ec.MOutArgCount: session[ec.SArgReceivedCount]})

@socketio.on(ec.EventCloseRoom, namespace=ec.NamespaceCranes)
def close(message):
    """Listener for socket room closing event"""
    session[ec.SArgReceivedCount] = session.get(ec.SArgReceivedCount, 0) + 1
    emit(ec.MOutPrefabResponse, {ec.MOutArgData: "Room " + message[ec.MArgRoom] + " is closing.",
                         ec.MOutArgCount: session[ec.SArgReceivedCount]},
         room=message[ec.MArgRoom])
    close_room(message[ec.MArgRoom])

@socketio.on(ec.EventDisconnect, namespace=ec.NamespaceCranes)
def cranes_disconnect():
    """Handler for client disconnection"""
    print("Client disconnected", request.sid)

@socketio.on(ec.EventDisconnectRequest, namespace=ec.NamespaceCranes)
def disconnect_request():
    """Listener for disconnection request"""
    session[ec.SArgReceivedCount] = session.get(ec.SArgReceivedCount, 0) + 1
    emit(ec.MOutPrefabResponse,
         {ec.MOutArgData: "Disconnected!", ec.MOutArgCount: session[ec.SArgReceivedCount]})
    disconnect()

@socketio.on(ec.EventOneCraneOptimalPosition, namespace=ec.NamespaceCranes)
def get_one_crane_opt_position(data):
    """Listener for one crane optimization request"""
    if not data or not ec.MArgCranesModelData in data or not ec.MArgCranesCranes in data or not ec.MArgRoom in data:
        emit(ec.MOutOneCraneOptPositionResponse, {ec.MOutTagCode: "400", ec.MOutTagStatus:ec.MOutValCraneOptError, ec.MOutTagError:"Data is missing"}, namespace=ec.NamespaceCranes)
        return

    def optFcn(data):
        #TODO: move this all to separate file
        room = data[ec.MArgRoom]
        namespace = ec.NamespaceCranes
        try:
            # Surrounding polygons are polygons of buildings which limit crane (not used for now)
            surroundingPolygons = []
            if ec.TagCraneOptSurroundingPolygons in data:
                surroundingPolygons = data[ec.TagCraneOptSurroundingPolygons]

            # Site polygons are polygons of the site in same coordinate system as bar data
            sitePolygons = []
            if ec.TagCraneOptSitePolygons in data:
                sitePolygons = data[ec.TagCraneOptSitePolygons]

            # Parse site data
            cranes = [eutils.GetCraneByType(c) for c in data[ec.TagCraneOptCranes]]
            client = ""
            if ec.ArgCraneOptClient in data:
                client = data[ec.ArgCraneOptClient]
            parser = eutils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
            pm = parser.ParseProjectModel(data[ec.TagCraneOptModelData])
            modelData = SiteData(pm, cranes, surroundingPolygons=surroundingPolygons, sitePolygons=sitePolygons)

            # Define data structure for drawing data
            drawData = {
                ec.MOutTagCraneOptModelBB:{}, 
                ec.MOutTagCraneOptCraneBEl:{}, 
                ec.MOutTagCraneOptBarCenters:[], 
                ec.MOutTagCraneOptSizes:{}}

            # Calculate scaling factors and offsets
            bp = modelData.boundingPolygon
            ep = modelData.craneEllipsePolygon
            xScalingFactor = np.max([bp.maxPoint.X - bp.minPoint.X, ep.maxPoint.X - ep.minPoint.X + 2 * cranes[0].maxLength])
            yScalingFactor = np.max([bp.maxPoint.Y - bp.minPoint.Y, ep.maxPoint.Y - ep.minPoint.Y + 2 * cranes[0].maxLength])
            xOffset = np.min([bp.minPoint.X, ep.minPoint.X - cranes[0].maxLength])
            yOffset = np.min([bp.minPoint.Y, ep.minPoint.Y - cranes[0].maxLength])
            if xScalingFactor > yScalingFactor:
                yOffset -= (xScalingFactor - yScalingFactor) / 2
            else:
                xOffset -= (yScalingFactor - xScalingFactor) / 2
            
            # Fill drawing data
            drawData[ec.MOutTagCraneOptModelBB] = {
                                            "min":{"X":modelData.boundingBox.minPoint.X, "Y":modelData.boundingBox.minPoint.Y, "Z":modelData.boundingBox.minPoint.Z},
                                            "max":{"X":modelData.boundingBox.maxPoint.X, "Y":modelData.boundingBox.maxPoint.Y, "Z":modelData.boundingBox.maxPoint.Z},
                                            "polygons":modelData.getBoundingPolygonCoords(jsonFormat=True)
                                            }
            drawData[ec.MOutTagCraneOptCraneBEl] = {
                                            #"center":{"X":modelData.craneEllipsePolygon.centerPoint.X, "Y":modelData.craneEllipsePolygon.centerPoint.Y, "Z":modelData.craneEllipsePolygon.centerPoint.Z},
                                            #"Rx":modelData.craneEllipsePolygon.radiusX,
                                            #"Ry":modelData.craneEllipsePolygon.radiusY,
                                            #"angle":modelData.craneEllipsePolygon.angle
                                            }
            for bar in modelData.Bars.values():
                drawData[ec.MOutTagCraneOptBarCenters].append({"X":bar.CenterPoint.X, "Y":bar.CenterPoint.Y, "Z":bar.CenterPoint.Z})

            drawData[ec.MOutTagCraneOptSizes] = {
                                    "squareSize": np.max([xScalingFactor, yScalingFactor]),
                                    "yOffset": -yOffset,
                                    "xOffset": -xOffset
                                }
        
            # Send drawing data once it is filled
            socketio.emit(ec.MOutOneCraneOptPositionResponse, {ec.MOutTagCode: 200, 
                                                               ec.MOutTagStatus: ec.MOutValCraneOptGotModelInfo, 
                                                               ec.MOutTagCraneOptDrawingData:drawData}, room=room, namespace=ec.NamespaceCranes)
            
            # Define update callback for GA hall of fame
            def hofUpdateCallback(item):
                supplyPoints = []
                cranePoints = []
                numCranes = len(item[0]) // 4
                for i in range(numCranes):
                    cranePoints.append({"X":item[0][i * 2], "Y":item[0][i * 2 + 1], "Z":0.0})
                    supplyPoints.append({"X":item[0][numCranes * 2 + i * 2], "Y":item[0][numCranes * 2 + i * 2 + 1], "Z":0.0})
                socketio.emit(ec.MOutOneCraneOptPositionResponse, {ec.MOutTagCode: 200, 
                                                                   ec.MOutTagStatus: ec.MOutValCraneOptGAInProgress, 
                                                                   ec.MOutTagCraneOptTime: item.fitness.values[0], 
                                                                   ec.MOutTagCraneOptCranePoints:cranePoints, 
                                                                   ec.MOutTagCraneOptSupplyPoints:supplyPoints}, room=room, namespace=ec.NamespaceCranes)

            # Do GA optimization
            res = CranePositionOptimizationGA(modelData, cranes, hofUpdateCallback=hofUpdateCallback)
            
            # Send final result with finished state
            supplyPoints = []
            cranePoints = []
            bp = res[ec.OutTagCraneOptBestPositions]
            numCranes = len(bp) // 4
            for i in range(numCranes):
                cranePoints.append({"X":bp[i * 2], "Y":bp[i * 2 + 1], "Z":0.0})
                supplyPoints.append({"X":bp[numCranes * 2 + i * 2], "Y":bp[numCranes * 2 + i * 2 + 1], "Z":0.0})
            socketio.emit(ec.MOutOneCraneOptPositionResponse, {ec.MOutTagCode: 200, 
                                                               ec.MOutTagStatus: ec.MOutValCraneOptFinished, 
                                                               ec.MOutTagCraneOptCranePoints:cranePoints, 
                                                               ec.MOutTagCraneOptSupplyPoints:supplyPoints}, room=room, namespace=namespace)
        except Exception as e:
            print(e)
            socketio.emit(ec.MOutOneCraneOptPositionResponse, {ec.MOutTagCode:500, 
                                                               ec.MOutTagStatus:ec.MOutValCraneOptError, 
                                                               ec.MOutTagError:"Internal error"}, room=room, namespace=namespace)
            return
    
    try:
        # Start calculations thread
        thread = Thread(target=optFcn, args=([data]))
        thread.start()

        # Send a message about process was started
        emit(ec.MOutOneCraneOptPositionResponse, {ec.MOutTagCode: 200, ec.MOutTagStatus: ec.MOutValCraneOptStarted}, room=data[ec.MArgRoom], namespace=ec.NamespaceCranes)
    except:
        socketio.emit(ec.MOutOneCraneOptPositionResponse, {ec.MOutTagCode:500, ec.MOutTagStatus:ec.MOutValCraneOptError, ec.MOutTagError:"Internal error"}, room=data[ec.MArgRoom], namespace=ec.NamespaceCranes)
        return

if __name__ == "__main__":
    import os
    HOST = os.environ.get("SERVER_HOST", "localhost")
    try:
        PORT = int(os.environ.get("SERVER_PORT", "5555"))
    except ValueError:
        PORT = 5555
    socketio.run(app, host=HOST, port=PORT)
