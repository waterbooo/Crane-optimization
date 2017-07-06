class EndpointConstants(object):
    """Constant values used in endpoints"""
    #
    #   Prefix endpoint arguments with Arg
    #   Prefix endpoint arg values with ArgVal
    #   Prefix endpoint header names with Header
    #   Prefix input JSON/XML tags with Tag
    #   Prefix output JSON/XML tags with OutTag
    #   After prefix write endpoint name e.g. CraneOpt for crane optimization
    #   After endpoint name put const name

    # ========================= HTTP ===============================
    # Common
    ValCommonClientRevit = "revit"
    ValCommonClientTekla = "tekla"
    ValCommonClientAdvanceSteel = "advancesteel"
    ValSetCommonClients = ["revit", "tekla", "advancesteel"]

    # Crane common
    MobileCrane = "MobileCrane"
    TowerCrane = "TowerCrane"

    # Crane optimization
    TagCraneOptSurroundingPolygons = "surroundingPolygons"
    TagCraneOptSitePolygons = "sitePolygons"
    TagCraneOptModelData = "modelData"
    TagCraneOptAnalyticalModel="AnalyticalModel"
    TagCraneOptCranes = "cranes"
    OutTagCraneOptBestPositions = "bestPositions"
    OutTagCraneOptCranePos = "cranePos"
    OutTagCraneOptX = "X"
    OutTagCraneOptY = "Y"
    OutTagCraneOptZ = "Z"
    OutTagCraneOptSupplyPos = "supplyPos"
    OutTagCraneOptCranes = "cranes"
    OutTagCraneOptTime = "time"
    ArgCraneOptMinAmount = "minamount"
    ArgCraneOptMaxAmount = "maxamount"
    ArgCraneOptClient = "client"

    # Construction order
    ArgConstrOrderNumClusters = "nclusters"
    ArgConstrOrderNumFlows = "nflows"
    OutTagConstrOrderOrder = "order"

    # Installation Time Args
    ArgNumCranes = "num-cranes"
    ArgNumSteelElements = "num-steel-elements"
    ArgBuildingShape = "building-shape"
    ArgMinPerimeterDist = "min-perimeter-dist"
    ArgSupplyPointDist = "supply-point-dist"
    ArgCraneLength = "crane-length"
    ArgCraneRotationSpeed = "crane-rotation-speed"
    ArgCraneTrolleySpeed = "crane-trolley-speed"
    ArgCraneMaxHookRadius = "crane-max-hook-radius"
    ArgInstallTime = "install-time"

    # CLIPS recommendations
    TagCLIPSRecommendRooms = "Rooms"
    ArgCLIPSRecommendClient = "client"
    ArgCLIPSRecommendTrades = "trades"
    ArgCLIPSRecommendObjects = "objects"
    ArgValCLIPSRecommendRevit = "revit"
    TagCLIPSRecommendTmp = "tmp"
    TagCLIPSRecommendTmps = "tmps"
    TagCLIPSRecommendResults = "results"
    OutTagCLIPSRecommendTrades = "trades"
    OutTagCLIPSRecommendAllTrades = "allTrades"

    # Tasks
    ArgTasksProjectId = "projectid"

    # ========================= SOCKETS.IO =============================
    # M - Message
    # Prefix message fields with MArg
    # Prefix response ids with MOut
    # Prefix response literal codes with MRespC
    # S - Session
    # Prefix session args with SArg
    # Prefix event names with Event

    # Events
    EventJoin = "join"
    EventConnect = "connect"
    EventLeave = "leave"
    EventCloseRoom = "close room"
    EventDisconnect = "disconnect"
    EventDisconnectRequest = "disconnect request"
    EventOneCraneOptimalPosition = "one crane opt position"

    # Namespaces
    NamespaceCranes = "/cranes"

    # Crane position optimization
    MArgRoom = "room"
    MArgCranesModelData = "modelData"
    MArgCranesCranes = "cranes"
    SArgReceivedCount = "receive_count"
    MOutPrefabResponse = "prefab response"
    MOutOneCraneOptPositionResponse = "one crane opt response"
    MOutArgData = "data"
    MOutArgCount = "count"
    MOutTagCode = "code"
    MOutTagStatus = "status"
    MOutTagError = "error"
    MOutTagCraneOptDrawingData = "drawData"
    MOutTagCraneOptModelBB = "modelBoundingBox"
    MOutTagCraneOptCraneBEl = "craneBoundingEllipse"
    MOutTagCraneOptBarCenters = "barCenters"
    MOutTagCraneOptSizes = "sizes"
    MOutTagCraneOptTime = "time"
    MOutTagCraneOptCranePoints = "cranePoints"
    MOutTagCraneOptSupplyPoints = "supplyPoints"

    MOutValCraneOptError = "ERROR"
    MOutValCraneOptGotModelInfo = "GOT MODEL INFO"
    MOutValCraneOptGAInProgress = "GA IN PROGRESS"
    MOutValCraneOptFinished = "FINISHED"
    MOutValCraneOptStarted = "STARTED"
    MRespCCranesConnected = "Connected"