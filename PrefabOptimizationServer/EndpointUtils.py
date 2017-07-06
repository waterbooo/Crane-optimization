from EndpointConstants import *
ec = EndpointConstants

class EndpointUtils(object):
    """Common methods for server endpoints"""

    def GetParserByClientType(client, defaultClient):
        parser = None
        if not client or client not in ec.ValSetCommonClients:
            client = defaultClient
        if client == ec.ValCommonClientRevit:
            from Parsers.RevitModelParser import RevitModelParser
            parser = RevitModelParser()
        elif client == ec.ValCommonClientTekla:
            from Parsers.TeklaModelParser import TeklaModelParser
            parser = TeklaModelParser()
        elif client == ec.ValCommonClientAdvanceSteel:
            from Parsers.AdvanceSteelModelParser import AdvanceSteelModelParser
            parser = AdvanceSteelModelParser()
        return parser

    def GetCraneByType(c):
        cd = None
        type = c["metadata"]["type"]

        if type == ec.MobileCrane:
            from Optimization.DataStructures.MobileCraneData import MobileCraneData
            cd = MobileCraneData(c)
        elif type == ec.TowerCrane:
            from Optimization.DataStructures.TowerCraneData import TowerCraneData
            cd = TowerCraneData(c)
        else:
            raise Exception("Unknown crane type")

        return cd

    def ParseModelFromJson(request):
        # Surrounding polygons are polygons of buildings which limit crane (not used for now)
        surroundingPolygons = []
        if ec.TagCraneOptSurroundingPolygons in request.json:
            surroundingPolygons = request.json[ec.TagCraneOptSurroundingPolygons]

        # Site polygons are polygons of the site in same coordinate system as construction objects data
        sitePolygons = []
        if ec.TagCraneOptSitePolygons in request.json:
            sitePolygons = request.json[ec.TagCraneOptSitePolygons]

        # Parse project model
        client = ""
        if ec.ArgCraneOptClient in request.args:
            client = request.args.get(ec.ArgCraneOptClient, ec.ValCommonClientAdvanceSteel).lower()
        parser = EndpointUtils.GetParserByClientType(client, ec.ValCommonClientAdvanceSteel)
        pm = parser.ParseProjectModel(request.json[ec.TagCraneOptModelData])

        return pm, surroundingPolygons, sitePolygons