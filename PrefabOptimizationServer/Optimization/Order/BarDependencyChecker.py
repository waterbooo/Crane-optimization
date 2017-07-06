import math, random, os, sys
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(__filePath, "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

__AMPath = os.path.join(__filePath, "Model")
if not __AMPath in sys.path:
    sys.path.insert(1, __AMPath)

from BLGeometry.PrefabGeometry import Point
import networkx as nx
from Model import BarType

class BarDependencyChecker(object):
    """Set of static helper methods for finding dependencies in the steel structure for Bars"""
    def addGroupedObjectDependencies(model, id):
        curBar = model.Bars[id]
        curBarRelEls = model.GetBarRelatedElements(id)
        bb = curBar.getBBforZCheck()

        def isAnyPointInsideBB(bar):
            bb1 = bar.getBBforZCheck()
            if (bb1.maxPoint.X < bb.minPoint.X or bb.maxPoint.X < bb1.minPoint.X or bb1.maxPoint.Y < bb.minPoint.Y or bb.maxPoint.Y < bb1.minPoint.Y or bb1.maxPoint.Z < bb.minPoint.Z or bb.maxPoint.Z < bb1.minPoint.Z):
                return False
            else:
                return True

        for obj in curBarRelEls.RelatedNonAttachedElements:
            if (model.Model.SteelAnalyticalModel.GetSupportingObject(obj) and model.Model.SteelAnalyticalModel.GetSupportingObject(obj).Type == "Plate") or obj in model.Bars:

                cond = lambda barId: obj in model.GetBarRelatedElements(barId).AttachedElements
                ownerBar = None
                for bar in curBarRelEls.Connections:
                    if obj in model.GetBarRelatedElements(bar).AttachedElements:
                        ownerBar = model.Bars[bar]
                        break

                ownerBars = []
                if not ownerBar:
                    for bar in curBarRelEls.Connections:
                        if obj in model.GetBarRelatedElements(bar).RelatedNonAttachedElements:
                            ownerBars.append(model.Bars[bar])
                else:
                    ownerBars.append(ownerBar)
                for ownerBar in ownerBars:
                    if ownerBar.Id in curBarRelEls.Connections and isAnyPointInsideBB(ownerBar):
                        if not model.dependencies.has_edge(ownerBar.Id, curBar.Id) and not model.dependencies.has_edge(curBar.Id, ownerBar.Id):
                            if curBar.BarType == BarType.Column and ownerBar.BarType != BarType.Column:
                                model.dependencies.add_edge(curBar.Id, ownerBar.Id, {"ZBased":False})
                            else:
                                model.dependencies.add_edge(ownerBar.Id, curBar.Id, {"ZBased":False})
                            if obj in model.Bars:
                                bar = model.GetBarRelatedElements(obj)
                                bar.IsAttached = True
                        elif model.dependencies.has_edge(ownerBar.Id, curBar.Id) and ownerBar.BarType != BarType.Column:
                            model.dependencies.remove_edge(ownerBar.Id, curBar.Id)
                            model.dependencies.add_edge(curBar.Id, ownerBar.Id, {"ZBased":False})
                            if obj in model.Bars:
                                bar = model.GetBarRelatedElements(obj)
                                bar.IsAttached = True

    def checkForColumnDependencies(model, beam):
        for dependency in beam.connections:
            bar = model.Bars[dependency]
            if bar.BarType == BarType.Column and bar.StartPoint.Z < min(beam.StartPoint.Z, beam.EndPoint.Z):
                return True
        return False

    def addDependencyWithCheck(model, id1, id2):
        """Checks whether it should be a dependency between two bars and adds it if true"""
        # Add dependency only in case if there is no dependency between two bars yet
        if not (model.dependencies.has_edge(id1, id2) or model.dependencies.has_edge(id2, id1)):
            # Get bars
            bar1 = model.Bars[id1]
            bar2 = model.Bars[id2]

            bar1MinZ = min(bar1.StartPoint.Z, bar1.EndPoint.Z)
            bar2MinZ = min(bar2.StartPoint.Z, bar2.EndPoint.Z)
            bar1MaxZ = max(bar1.StartPoint.Z, bar1.EndPoint.Z)
            bar2MaxZ = max(bar2.StartPoint.Z, bar2.EndPoint.Z)

            # For other bar types check whether bar has column dependency
            dependsOnCol1 = BarDependencyChecker.checkForColumnDependencies(model, bar1)
            dependsOnCol2 = BarDependencyChecker.checkForColumnDependencies(model, bar2)
            
            # Defferent cases for bars of the same type and different types
            if bar1.BarType != bar2.BarType:
                
                # column is top priority type.
                # everything depends on column if its start point is below any point of beam or edge
                # otherwise column depends on bar or beam
                if bar1.BarType == BarType.Column or abs(bar2MaxZ - bar2MinZ) > model.tolerance:
                    if bar1MinZ < bar2MinZ:
                        model.dependencies.add_edge(id1, id2, {"ZBased":True})
                    else:
                        model.dependencies.add_edge(id2, id1, {"ZBased":True})
                elif bar2.BarType == BarType.Column or abs(bar1MaxZ - bar1MinZ) > model.tolerance:
                    if bar2MinZ < bar1MinZ:
                        model.dependencies.add_edge(id2, id1, {"ZBased":True})
                    else:
                        model.dependencies.add_edge(id1, id2, {"ZBased":True})
                # bar is the lowest priority type and we are assuming it depends on all the other types
                # here is the case of beam dependency
                elif bar1.BarType == BarType.Bar:
                    model.dependencies.add_edge(id2, id1, {"ZBased":True})
                elif bar2.BarType == BarType.Bar:
                    model.dependencies.add_edge(id1, id2, {"ZBased":True})
            else:
                # If both bars are columns the one with minimum z start point coordinate should go first
                if bar1.BarType == BarType.Column:
                    if bar1MinZ < bar2MinZ:
                        model.dependencies.add_edge(id1, id2, {"ZBased":True})
                    elif bar1MinZ > bar2MinZ:
                        model.dependencies.add_edge(id2, id1, {"ZBased":True})
                else:
                    # if only one has column dependency then it goes first
                    if dependsOnCol1 != dependsOnCol2 and abs(bar1MinZ - bar2MinZ) <= model.tolerance:
                        if dependsOnCol1:
                            model.dependencies.add_edge(id1, id2, {"ZBased":True})
                        else:
                            model.dependencies.add_edge(id2, id1, {"ZBased":True})
                    # if both do not have dependency on column
                    elif not dependsOnCol1:
                        # look at minimum z coordinate
                        if abs(bar1MinZ - bar2MinZ) <= model.tolerance:
                            # in the case of equal z check assembly numbers
                            if bar1.assemblyNumber < bar2.assemblyNumber and bar1.assemblyNumber != -1:
                                model.dependencies.add_edge(id1, id2, {"ZBased":True})
                            elif bar1.assemblyNumber > bar2.assemblyNumber and bar2.assemblyNumber != -1:
                                model.dependencies.add_edge(id2, id1, {"ZBased":True})
                            else:
                                # in case of equal or not defined assembly numbers simply add edge avoiding cycles
                                model.dependencies.add_edge(id1, id2, {"ZBased":True})
                                cycles = nx.algorithms.cycles.simple_cycles(model.dependencies)
                                if len(list(cycles)) > 0:
                                    model.dependencies.remove_edge(id1, id2)
                                    model.dependencies.add_edge(id2, id1, {"ZBased":True})
                        elif bar1MinZ < bar2MinZ:
                            model.dependencies.add_edge(id1, id2, {"ZBased":True})
                        else:
                            model.dependencies.add_edge(id2, id1, {"ZBased":True})

    def addZLevelDependencies(model, id):
        """Check for bars which are in neighbourhood of input one and are lower than it.
           Them should be placed before it
        """
        curBar = model.Bars[id]
        bb = curBar.getBBforZCheck()

        # Checker for neighbourhood
        def isAnyPointInsideBB(bar):
            bb1 = bar.getBBforZCheck()
            if (bb1.maxPoint.X < bb.minPoint.X or bb.maxPoint.X < bb1.minPoint.X or bb1.maxPoint.Y < bb.minPoint.Y or bb.maxPoint.Y < bb1.minPoint.Y or bb1.maxPoint.Z < bb.minPoint.Z or bb.maxPoint.Z < bb1.minPoint.Z):
                return False
            else:
                return True
            
        # get all bars in the neighbourhood
        relativeBarIds = [bar.Id for bar in model.Bars.values() if isAnyPointInsideBB(bar)]
        if id in relativeBarIds:
            relativeBarIds.remove(id)

        # select columns from bars in the neighbourhood and if thr list isn't empty reduce it to just cols
        cols = [b for b in relativeBarIds if model.Bars[b].BarType == BarType.Column]
        if len(cols) != 0:
            relativeBarIds = cols

        # if there is no dependency between bars yet, add it
        for relId in relativeBarIds:
            relBar = model.Bars[relId]
            if not (model.dependencies.has_edge(id, relId) or model.dependencies.has_edge(relId, id)):
                barMinZ = min(curBar.StartPoint.Z, curBar.EndPoint.Z)
                relBarMinZ = min(relBar.StartPoint.Z, relBar.EndPoint.Z)
                if barMinZ < relBarMinZ: #or (abs(barMinZ - relBarMinZ) <= self.tolerance and relBar.BarType == BarType.Column):
                    model.dependencies.add_edge(id, relId, {"ZBased":True})
                elif barMinZ > relBarMinZ:
                    model.dependencies.add_edge(relId, id, {"ZBased":True})
                
    def checkColumnDependency(model, id):
        """Check whether bar is dependent on any column"""
        G = model.dependencies
        rootNode = id
        nodeStack = [(rootNode, iter(G.predecessors(rootNode)))]
        rootNodes = set()
        visited = set()
        while nodeStack:
            child,parents = nodeStack[-1]
            try:
                parent = next(parents)
                if model.Bars[parent].BarType == BarType.Column:
                    return True
                if parent not in visited:
                    nodeStack.append((parent, iter(G.predecessors(parent))))
                    visited.add(parent)
            except StopIteration:
                nodeStack.pop()  
        return False

    def buildDependencyGraph(model):
        """Builds an oriented graph from model conditions.
           If there is a connection id1 to id2 it means id1 is dependent on id2
           If element has no dependencies it has no outgoing connections.
        """
        bdc = BarDependencyChecker
        # add all bar nodes to graph
        for bar in model.Bars.values():
            model.dependencies.add_node(bar.Id)

        # add dependencies from the structure (by plates)
        for bar in model.Bars.values():
            bdc.addGroupedObjectDependencies(model, bar.Id)

        # remove non-bar in fact objects
        for bar in model.Bars.values():
            if model.GetBarRelatedElements(bar.Id).IsAttached:
                model.dependencies.remove_node(bar.Id)
        
        barsForAdditionalProcessing = []
        for bar in model.Bars.values():
            if (not model.GetBarRelatedElements(bar.Id).IsAttached) and (not bar.BarType == BarType.Column) and (not BarDependencyChecker.checkColumnDependency(model, bar.Id)):
                barsForAdditionalProcessing.append(bar.Id)

        # reverse dependencies if this brinds column dependency
        for barId in barsForAdditionalProcessing:
            succ = model.dependencies.successors(barId)
            pred = model.dependencies.predecessors(barId)
            for s in succ:
                if bdc.checkColumnDependency(model, s):
                    zbased = model.dependencies[barId][s]["ZBased"]
                    model.dependencies.remove_edge(barId, s)
                    model.dependencies.add_edge(s, barId, {"ZBased":zbased})

        # do z level dependencies marks for nodes without any info
        barsForAdditionalProcessing = []
        for bar in model.Bars.values():
            if (not model.GetBarRelatedElements(bar.Id).IsAttached) and (((not bar.BarType == BarType.Column) and (not BarDependencyChecker.checkColumnDependency(model, bar.Id))) or len(model.GetBarRelatedElements(bar.Id).Connections) == 0):
                barsForAdditionalProcessing.append(bar.Id)
            
        for barId in barsForAdditionalProcessing:
            bdc.addZLevelDependencies(model, barId)

        bdc.deCycleDepencies(model)


    def deCycleDepencies(model):
        """Removes extra dependencies from graph to make it acyclic"""
        # find and remove cycles
        cycles = list(nx.algorithms.cycles.simple_cycles(model.dependencies))

        # produced by z levels
        j = 0
        while cycles and j < len(cycles):
            for i in range(len(cycles[j]) - 1):
                if model.dependencies[cycles[j][i]][cycles[j][i+1]]["ZBased"]:
                    model.dependencies.remove_edge(cycles[j][i], cycles[j][i+1])
                    BarDependencyChecker.removeEdgeFromCycleList(model, cycles, cycles[j][i], cycles[j][i+1])
                    j = 0
                    break
            if len(cycles) > 0 and model.dependencies[cycles[j][len(cycles[j]) - 1]][cycles[j][0]]["ZBased"]:
                model.dependencies.remove_edge(cycles[j][len(cycles[j]) - 1], cycles[j][0])
                BarDependencyChecker.removeEdgeFromCycleList(model, cycles, cycles[j][len(cycles[j]) - 1], cycles[j][0])
                j = 0
            else:
                j += 1

        # other ones
        if j != 0:
            while cycles and j < len(cycles):
                cycle = cycles[j]
                preds = [len(model.dependencies.predecessors(bar)) for bar in cycle]
                succs = [len(model.dependencies.successors(bar)) for bar in cycle]
                
                for i in range(len(cycle) - 1):
                    if succ[i] > 1 and pred[i + 1] > 1:
                        model.dependencies.remove_edge(cycles[j][i], cycles[j][i+1])
                        BarDependencyChecker.removeEdgeFromCycleList(model, cycles, cycles[j][i], cycles[j][i+1])
                        j = 0
                        break
                if len(cycles) > 0 and succ[len(cycle - 1)] > 1 and pred[0] > 1:
                    model.dependencies.remove_edge(cycles[j][len(cycles[j]) - 1], cycles[j][0])
                    BarDependencyChecker.removeEdgeFromCycleList(model, cycles, cycles[j][len(cycles[j]) - 1], cycles[j][0])
                    j = 0
                else:
                    zcoords = [min(model.Bars[bar].StartPoint.Z,model.Bars[bar].EndPoint.Z) for bar in cycle ]
                    maxz = max(zcoords)
                    maxzind = 0
                    for i in range (len(cycle)):
                        if abs(zcoords[i] - maxz) < model.tolerance:
                            maxzind = i
                            break
                    predind = maxzind - 1
                    if predind < 0:
                        predind = len(cycle) - 1
                    nextind = maxzind + 1
                    if nextind == len(cycle):
                        nextind = 0
                    if zcoords[nextind] > zcoords[predind]:
                        model.dependencies.remove_edge(cycle[maxzind], cycle[nextind])
                        BarDependencyChecker.removeEdgeFromCycleList(model, cycles, cycle[maxzind], cycle[nextind])
                        j = 0
                    else:
                        model.dependencies.remove_edge(cycle[predind], cycle[maxzind])
                        BarDependencyChecker.removeEdgeFromCycleList(model, cycles, cycle[predind], cycle[maxzind])
                        j = 0
                    
    def removeEdgeFromCycleList(model, cycles, id1, id2):
        """Removes edge from dependencies graph and removes it from all found cycles"""
        cyclesToRemove = []
        cycleIndex = 0
        for cycle in cycles:
            nodesToRemove = []
            edgeIndices = [i for i, x in enumerate(cycle) if x == id1]
            for ind1 in edgeIndices:
                ind2 = ind1 + 1
                if ind2 == len(cycle):
                    ind2 = 0
                if cycle[ind2] == id2:
                    if len(cycle) == 3:
                        cyclesToRemove.append(cycleIndex)
                    else:
                        ind0 = ind1 - 1
                        if ind0 < 0:
                            ind0 = len(cycle) - 1
                        ind3 = ind2 + 1
                        if ind3 > len(cycle) - 1:
                            ind3 = 0
                        if model.dependencies.has_edge(cycle[ind0], cycle[ind2]):
                            nodesToRemove.append(ind1)
                        elif model.dependencies.has_edge(cycle[ind1], cycle[ind3]):
                            nodesToRemove.append(ind2)
                        else:
                            cyclesToRemove.append(cycleIndex)
            if not cycleIndex in cyclesToRemove and len(nodesToRemove) > 0:
                nodesToRemove.reverse()
                for node in nodesToRemove:
                    cycle.pop(node)
            cycleIndex += 1
        cyclesToRemove.reverse()
        for cycleInd in cyclesToRemove:
            cycles.pop(cycleInd)
