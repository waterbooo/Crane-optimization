import math, operator

from BLGeometry import GeometryUtils
from Optimization.Order.ConstructionOrdering import ConstructionOrdering

class PanelDependencyChecker(object):
    """Set of static helper methods for finding dependencies in the steel structure for Panels"""

    _panelsInRow = []

    def buildDependencyGraph(model):
        """ Builds an oriented graph from model conditions. """

        barLeafs = [x for x in model.dependencies.nodes_iter() if model.dependencies.out_degree(x)==0]
        barRoots = [x for x in model.dependencies.nodes_iter() if model.dependencies.in_degree(x)==0]

        # add all panel nodes to graph
        for panel in model.Panels.values():
            model.dependencies.add_node(panel.Id)

        # add edges for elements in a 
        for wall in model.Walls.values():
            if len(wall.GetPanels()) > 0:
                PanelDependencyChecker.addDependenciesForWall(model, wall)

        panelRoots = [x for x in model.dependencies.nodes_iter() if model.dependencies.in_degree(x)==0 and x not in barRoots]

        for r in panelRoots:
            for l in barLeafs:
                model.dependencies.add_edge(l, r)
       
        # set priorities for nodes
        co = ConstructionOrdering
        co.setOrderPriorities(model.dependencies)
        
    def addDependenciesForWall(model, wall):
        """ Create dependencies between elements in wall. """

        panels = wall.GetPanels()
        # get first panel - closest to wall start point
        firstPanel = PanelDependencyChecker.getClosestPanelToPoint(panels, wall.StartPoint)
        # add dependencies for panels in row
        PanelDependencyChecker.addDependenciesForRow(model, panels, firstPanel, 0)


    def addDependenciesForRow(model, panels, panel, depth):
        """ Create dependencies between elements in row. """

        # apartness from first panel
        nextDepth = depth + 1
        # closet panels to current panel
        relativePanelIds = PanelDependencyChecker.getRelativePanelIds(panels, panel)
        # get Id of a panel which is next in row to current
        nearById = PanelDependencyChecker.getNearByPanel(model, panels, panel, relativePanelIds)
        if not (nearById == None):
            PanelDependencyChecker._panelsInRow.append(nearById)
            relativePanelIds.remove(nearById)
            PanelDependencyChecker.addDependenciesForRow(model, panels, model.Panels[nearById], nextDepth)
        # map of [panelId]:[min distance] used to get panel on top
        idToDistMap = {p.Id:GeometryUtils.GetDistanceBetweenPoints(panel.CenterPoint, p.CenterPoint) for p in [panels[id] for id in relativePanelIds]}
        while len(idToDistMap) > 0:
            topId = min(idToDistMap, key=idToDistMap.get)
            topPanel = panels[topId]

            panelMinZ = min([c.Z for c in panel.GetCorners()])
            topPanelMinZ = min(c.Z for c in topPanel.GetCorners())

            # skip if on the same row or below
            if topPanelMinZ - panelMinZ <= 0.1 :
                idToDistMap.pop(topId)
            else:
                model.dependencies.add_edge(panel.Id, topId)
                # look for dependencies if it is first pannel in a row
                if depth == 0:
                    PanelDependencyChecker._panelsInRow = []
                    PanelDependencyChecker.addDependenciesForRow(model, panels, topPanel, depth)
                break

    def getRelativePanelIds(panels, currentPanel):
        """ Returns closest panels Ids """

        # Checker for neighbourhood
        def isAnyPointInsideBB(panel1, panel2):
            bb1 = panel1.getBBforZCheck()
            bb2 = panel2.getBBforZCheck()
            if (bb2.maxPoint.X < bb1.minPoint.X or bb1.maxPoint.X < bb2.minPoint.X or bb2.maxPoint.Y < bb1.minPoint.Y or bb1.maxPoint.Y < bb2.minPoint.Y or bb2.maxPoint.Z < bb1.minPoint.Z or bb1.maxPoint.Z < bb2.minPoint.Z):
                return False
            else:
                return True

        # get all panels in the neighbourhood
        relativePanelIds = [panel.Id for panel in panels.values() if isAnyPointInsideBB(currentPanel, panel)]
        if currentPanel.Id in relativePanelIds:
            relativePanelIds.remove(currentPanel.Id)

        return relativePanelIds

    def getNearByPanel(model, panels, panel, relativePanelIds):
        """ Returns panel which is next to current """

        closestMap = {}
        for relId in relativePanelIds:
            closestMap[relId] = GeometryUtils.GetDistanceBetweenPoints(panels[relId].CenterPoint, panel.CenterPoint)
        sortedMap = sorted(closestMap.items(), key=operator.itemgetter(1))

        for elem in sortedMap:
            relId = elem[0]
            relPanel = panels[relId]

            if relId in PanelDependencyChecker._panelsInRow:
                continue

            # skip if relation is already established
            if not (model.dependencies.has_edge(panel.Id, relId) or model.dependencies.has_edge(relId, panel.Id)):
                panelMinZ = min([c.Z for c in panel.GetCorners()])
                relPanleMinZ = min(c.Z for c in relPanel.GetCorners())

                if math.fabs(panelMinZ - relPanleMinZ) < 0.1:
                    model.dependencies.add_edge(panel.Id, relId)
                    return relId

        return None


    def getClosestPanelToPoint(panels, point):
        """ Return closest panel to point """

        minDistToStart = -1
        closestPanel = -1

        for panel in panels.values():

            closest = min([GeometryUtils.GetDistanceBetweenPoints(point, p) for p in panel.GetCorners()])

            if minDistToStart == -1:
                minDistToStart = closest
                closestPanel = panel
            elif closest < minDistToStart:
                minDistToStart = closest
                closestPanel = panel

        return closestPanel