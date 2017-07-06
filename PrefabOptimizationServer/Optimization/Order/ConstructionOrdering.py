import networkx as nx
import copy

class ConstructionOrdering(object):
    """Methods for calculation of construction order with dependecies graph of the model"""

    kAttrNameNodeLevel = "level"
    kAttrNameGraphMaxLevel = "maxLevelMark"
    kAttrNameNodeAfterLength = "afterLength"
    kAttrNameNodeNumOfChildren = "numOfChildren"
    kAttrNameNodeDependentSetSize = "dependentSet"
    kAttrNameGraphMaxDependentNumber = "maxDependentNumber"
    kAttrNameNodePriority = "priority"

    def _dfs_level_mark(G):
        """Marks each node with its max depth level using DFS"""
        kLevelNodeAttrName = ConstructionOrdering.kAttrNameNodeLevel
        kLevelGraphAttrName = ConstructionOrdering.kAttrNameGraphMaxLevel
        kAfterLengthAttrName = ConstructionOrdering.kAttrNameNodeAfterLength
        ConstructionOrdering.markNodes(G, kLevelNodeAttrName, lambda G, node: 0)
        ConstructionOrdering.markNodes(G, kAfterLengthAttrName, lambda G, node: 0)
        maxLevelMark = 0
        nodes = G
        visited=set()
        for rootNode in nodes:
            if rootNode in visited:
                continue
            visited.add(rootNode)
            nodeStack = [(rootNode,iter(G[rootNode]))]
            while nodeStack:
                parent,children = nodeStack[-1]
                try:
                    child = next(children)
                    if G.node[child][kLevelNodeAttrName] <= G.node[parent][kLevelNodeAttrName] and child in visited:
                        visited.remove(child)
                    elif G.node[child][kLevelNodeAttrName] == G.node[parent][kLevelNodeAttrName] + 1:
                        G.node[parent][kAfterLengthAttrName] = G.node[child][kAfterLengthAttrName] + 1
                    if child not in visited:
                        visited.add(child)
                        G.node[child][kLevelNodeAttrName] = G.node[parent][kLevelNodeAttrName] + 1
                        if G.node[child][kLevelNodeAttrName] > maxLevelMark:
                            maxLevelMark = G.node[child][kLevelNodeAttrName]
                        nodeStack.append((child,iter(G[child])))
                        for i in range(len(nodeStack)):
                            p,c = nodeStack[i]
                            G.node[p][kAfterLengthAttrName] = max(G.node[p][kAfterLengthAttrName], len(nodeStack) - 1 - i)
                except StopIteration:
                    nodeStack.pop()
        G.graph[kLevelGraphAttrName] = maxLevelMark
            
    def _dfs_critical_ways(G):
        """Search for critical ways with DFS"""
        kLevelNodeAttrName = ConstructionOrdering.kAttrNameNodeLevel
        kLevelGraphAttrName = ConstructionOrdering.kAttrNameGraphMaxLevel
        kAfterLengthAttrName = ConstructionOrdering.kAttrNameNodeAfterLength
        nodes = G
        visited=set()
        routes = []
        for rootNode in nodes:
            if rootNode in visited or G.graph[kLevelGraphAttrName] != G.node[rootNode][kAfterLengthAttrName]:
                continue
            visited.add(rootNode)
            nodeStack = [(rootNode,iter(G[rootNode]))]
            curRoute = [rootNode]
            while nodeStack:
                parent,children = nodeStack[-1]
                try:
                    child = next(children)
                    if G.node[child][kAfterLengthAttrName] + len(nodeStack) != G.graph[kLevelGraphAttrName]:
                        visited.add(child)
                    elif child in visited:
                        visited.remove(child)
                    if child not in visited:
                        visited.add(child)
                        curRoute.append(child)
                        nodeStack.append((child,iter(G[child])))
                        if G.node[child][kAfterLengthAttrName] == 0:
                            routes.append(copy.deepcopy(curRoute))
                except StopIteration:
                    nodeStack.pop()
                    curRoute.pop()
        return routes

    def markLevels(G):
        """Marks graph nodes levels"""
        ConstructionOrdering._dfs_level_mark(G)
        
    def markNodes(G, attrName, markF, nodes=None):
        """Utility method for node marking"""
        if nodes == None:
            nodes = G.nodes()
        for node in nodes:
            G.node[node][attrName] = markF(G, node)

    def getCriticalWays(G):
        """Finds critical ways in the graph"""
        if G.graph[ConstructionOrdering.kAttrNameGraphMaxLevel] == None:
            ConstructionOrdering.markLevels(G)
        return ConstructionOrdering._dfs_critical_ways(G)

    def markChildrenCount(G):
        """Marks each node with a count of its children"""
        ConstructionOrdering.markNodes(G, ConstructionOrdering.kAttrNameNodeNumOfChildren, lambda G, node: G.out_degree(node))

    def markDependentCount(G):
        """Marks each node with a number of dependent nodes"""
        kAttrNameNodeDependentSetSize = ConstructionOrdering.kAttrNameNodeDependentSetSize
        G_copy = copy.deepcopy(G)
        maxDepenrentNumber = 0
        
        ConstructionOrdering.markNodes(G, kAttrNameNodeDependentSetSize, lambda G, node: set())
        while G_copy.number_of_nodes() > 0:
            nodes = [k for k,v in G_copy.out_degree().items() if v == 0]
            visited=set()
            for node in nodes:
                pred = G.predecessors(node)
                ConstructionOrdering.markNodes(G, kAttrNameNodeDependentSetSize, lambda G, p: G.node[p][kAttrNameNodeDependentSetSize].union(G.node[node][kAttrNameNodeDependentSetSize].union([node])), pred)
                visited.add(node)
            for v in visited:
                G_copy.remove_node(v)
                G.node[v][kAttrNameNodeDependentSetSize] = len(G.node[v][kAttrNameNodeDependentSetSize])
                if G.node[v][kAttrNameNodeDependentSetSize] > maxDepenrentNumber:
                    maxDepenrentNumber = G.node[v][kAttrNameNodeDependentSetSize]
        return maxDepenrentNumber

    def _getNodePriority(G, node):
        """Calculate priority for a single node"""
        priority = 1.0
        if ConstructionOrdering.kAttrNameGraphMaxDependentNumber in G.graph and G.graph[ConstructionOrdering.kAttrNameGraphMaxDependentNumber] != 0:
            if ConstructionOrdering.kAttrNameNodeDependentSetSize in G.node[node]:
                priority *= ((G.node[node][ConstructionOrdering.kAttrNameNodeDependentSetSize] + 1) / (G.graph[ConstructionOrdering.kAttrNameGraphMaxDependentNumber] + 1))
        if ConstructionOrdering.kAttrNameGraphMaxLevel in G.graph and G.graph[ConstructionOrdering.kAttrNameGraphMaxLevel] != 0:
            if ConstructionOrdering.kAttrNameNodeLevel in G.node[node]:
                numerator = G.graph[ConstructionOrdering.kAttrNameGraphMaxLevel] - G.node[node][ConstructionOrdering.kAttrNameNodeLevel]
                if numerator == 0:
                    numerator = 0.5
                priority *= (numerator / G.graph[ConstructionOrdering.kAttrNameGraphMaxLevel])
        return priority

    def setOrderPriorities(G):
        """Mark nodes taking into account critical ways, maximum level on route in graph and number of dependent nodes"""
        ConstructionOrdering.markLevels(G)
        maxDependentNumber = ConstructionOrdering.markDependentCount(G)
        G.graph[ConstructionOrdering.kAttrNameGraphMaxDependentNumber] = maxDependentNumber
        criticalRoutes = ConstructionOrdering.getCriticalWays(G)
        ConstructionOrdering.markNodes(G, ConstructionOrdering.kAttrNameNodePriority, lambda G, node: ConstructionOrdering._getNodePriority(G, node))
        criticalSet = set()
        for cr in criticalRoutes:
            criticalSet = criticalSet.union(cr)
        notCriticalNodes = [k for k in G.nodes() if not k in criticalSet]
        
        ConstructionOrdering.markNodes(G, ConstructionOrdering.kAttrNameNodePriority, lambda G, node: G.node[node][ConstructionOrdering.kAttrNameNodePriority] * 0.9, notCriticalNodes)
        
    def __isAnyPointInsideBB(bb, structualObject):
        """Helper function for check of structualObjects just below considered"""
        bb1 = structualObject.getBBforZCheck(0.5)
        if (bb1.maxPoint.X < bb.minPoint.X or bb.maxPoint.X < bb1.minPoint.X or bb1.maxPoint.Y < bb.minPoint.Y or bb.maxPoint.Y < bb1.minPoint.Y):
            return False
        else:
            return True

    def __CorrectNodeByZ(structualObjectCandidates, structualObjects, nodes, node):
        """Helper function for check of lower structualObjects which should be placed before current one"""
        co = ConstructionOrdering
        res = node
        if len(structualObjectCandidates) > 0:
            structualObjectCandidate = structualObjectCandidates[0]
            bb = structualObjectCandidate.getBBforZCheck(0.5)
            lowerstructualObjects = [obj for obj in structualObjects if min(obj.StartPoint.Z, obj.EndPoint.Z) <= min(structualObjectCandidate.StartPoint.Z, structualObjectCandidate.EndPoint.Z) and obj.Id in nodes]
            if lowerstructualObjects:
                candidates = [obj for obj in lowerstructualObjects if co.__isAnyPointInsideBB(bb, obj)]
                if candidates:
                    nodeStructualObject = min(candidates, key=lambda obj:min(obj.StartPoint.Z, obj.EndPoint.Z))
                    res = nodeStructualObject.Id
        return res

    def GetConstructionOrder(G, structualObjects):
        """Ordering of structualObjects in model"""
        co = ConstructionOrdering
        # set priorities for nodes

        co.setOrderPriorities(G)
        
        # copy graph
        G_copy = copy.deepcopy(G)

        order = []
        
        # select all nodes with no parents
        nodes = set([k for k,v in G_copy.in_degree().items() if v == 0])
        
        # do while not all nodes are seen
        while G_copy.number_of_nodes() > 0:
            # select node with maximum priority from the list
            node = max(nodes, key=lambda k: G_copy.node[k][ConstructionOrdering.kAttrNameNodePriority])
            
            # if there is structualObjects info, select the lowest acceptable structualObject just below current one
            if structualObjects:
                bCands = [obj for obj in structualObjects if obj.Id == node]
                node = co.__CorrectNodeByZ(bCands, structualObjects, nodes, node)

            order.append(node)
            nodes.remove(node)
            succ = G.successors(node)
            G_copy.remove_node(node)

            # refresh list of nodes with new nodes without any parents
            freeSucc = [k for k in succ if G_copy.in_degree(k) == 0]
            nodes = nodes.union(freeSucc)
        return order

    def GetConstructionOrderClustered(G, structuralObjects, clusterIndices):
        """Gets parallelized order according to cluster
           One structualObject from cluster at single order position
        """

        co = ConstructionOrdering
        order = []

        clusterNames = {}
        for k in clusterIndices.keys():
            clusterNames[k] = [structuralObjects[i].Id for i in clusterIndices[k]]
        
        # set priorities for nodes
        co.setOrderPriorities(G)
        
        # copy graph
        G_copy = copy.deepcopy(G)

        # select all nodes with no parents
        nodes = set([k for k,v in G_copy.in_degree().items() if v == 0])
        
        # do while not all nodes are seen
        while G_copy.number_of_nodes() > 0:
            orderPlace = []
            for cn in clusterNames.keys():
                # select node with maximum priority from the list
                cnodes = [n for n in nodes if n in clusterNames[cn]]
                node = max(cnodes, key=lambda k: G_copy.node[k][ConstructionOrdering.kAttrNameNodePriority], default=None)
            
                # if there is structuralObjects info, select the lowest acceptable structualObject just below current one
                if node and structuralObjects:
                    bCands = [obj for obj in structuralObjects if obj.Id == node]
                    node = co.__CorrectNodeByZ(bCands, structuralObjects, cnodes, node)

                orderPlace.append(node)

            order.append(orderPlace)
            succ = []
            for node in orderPlace:
                if node:
                    nodes.remove(node)
                    succ += G.successors(node)
                    G_copy.remove_node(node)

                # refresh list of nodes with new nodes without any parents
                freeSucc = [k for k in succ if G_copy.in_degree(k) == 0]
                nodes = nodes.union(freeSucc)
        return order

    def GetConstructionOrderMult(G, structualObjects, numFlows):
        """Gets parallelized order with just number of working instances
        """
        co = ConstructionOrdering
        order = []

        # set priorities for nodes
        co.setOrderPriorities(G)
        
        # copy graph
        G_copy = copy.deepcopy(G)

        # select all nodes with no parents
        nodes = set([k for k,v in G_copy.in_degree().items() if v == 0])
        
        # do while not all nodes are seen
        while G_copy.number_of_nodes() > 0:
            orderPlace = []
            for i in range(numFlows):
                # select node with maximum priority from the list
                node = max(nodes, key=lambda k: G_copy.node[k][ConstructionOrdering.kAttrNameNodePriority], default=None)
            
                # if there is structualObjects info, select the lowest acceptable structualObject just below current one
                if node and structualObjects:
                    bCands = [obj for obj in structualObjects if obj.Id == node]
                    node = co.__CorrectNodeByZ(bCands, structualObjects, nodes, node)

                    nodes.remove(node)

                orderPlace.append(node)

            order.append(orderPlace)
            succ = []
            for node in orderPlace:
                if node:
                    succ += G.successors(node)
                    G_copy.remove_node(node)

                # refresh list of nodes with new nodes without any parents
                freeSucc = [k for k in succ if G_copy.in_degree(k) == 0]
                nodes = nodes.union(freeSucc)
        return order

    def getRelativeNodes(G, id):
        """Gets all nodes in graph related to current and its parent stack"""
        rootNode = id
        nodeStack = [(rootNode, iter(G.predecessors(rootNode)))]
        rootNodes = set()
        visited = set()
        while nodeStack:
            child,parents = nodeStack[-1]
            try:
                parent = next(parents)
                if parent not in visited:
                    nodeStack.append((parent, iter(G.predecessors(parent))))
                    if len(G.predecessors(parent)) == 0:
                        rootNodes.add(parent)
                    visited.add(parent)
            except StopIteration:
                nodeStack.pop()   
        
        visited = set()
        for node in rootNodes:
            nodeStack = [(node,iter(G[node]))]
            
            visited.add(node)
            while nodeStack:
                parent,children = nodeStack[-1]
                try:
                    child = next(children)
                    if child not in visited:
                        visited.add(child)
                        nodeStack.append((child, iter(G[child])))
                except StopIteration:
                    nodeStack.pop()
        if rootNode in visited:
            visited.remove(rootNode)
        return visited 

    def getTheCraneStopOrder(cranePosition, supplyPoint):
        """ This function will assign the stop order according to the corresponding
        supply points """
        import numpy as np

        cranePosition_copy=copy.deepcopy(cranePosition)
        newCranePosition=[]
        maxDependencyInClusters=dict()
        bigNumer=1000000
        # reorder the crane stop according to the arranged supply point.
        for i in range(len(supplyPoint)):
            dis_C_S=[np.sqrt(np.square(cranePosition_copy[j].X-supplyPoint[i].X)+np.square(cranePosition_copy[j].Y-supplyPoint[i].Y)) for j in range(len(cranePosition))]
            index=min(range(len(cranePosition)),key=lambda k: dis_C_S[k])
            newCranePosition.append(cranePosition[index])
            cranePosition_copy[index].X=bigNumer
            cranePosition_copy[index].Y=bigNumer
        
        return newCranePosition

    def getTheSupplyLocationOrder(Data,Wall):

        import numpy as np
        from BLGeometry.PrefabGeometry import Point
        from shapely.geometry import Polygon

        G=Data.Dependencies
        SupplyPosition=Data.SupplyPoints
        clusterNames=Data.ClusterNames
        siteAcceptableRegion=Data.AcceptableRegionForCrane

        def length(v):
            return np.sqrt(v[0]**2+v[1]**2)
        def dot_product(v,w):
           return v[0]*w[0]+v[1]*w[1]
        def determinant(v,w):
           return v[0]*w[1]-v[1]*w[0]
        def inner_angle(v,w):
           cosx=dot_product(v,w)/(length(v)*length(w))*0.99999
           rad=np.arccos (cosx) # in radians
           return rad # returns degrees
        def angle_clockwise(A,B):
            inner=inner_angle(A,B)
            det = determinant(A,B)
            if det<0: #this is a property of the det. If the det < 0 then B is clockwise of A
                return inner
            else: # if the det > 0 then A is immediately clockwise of B
                return 2*np.pi-inner
       
        """ This function will assign the stop order according to the corresponding
        the maximum dependency set size """
        newSupplyPosition=[]
        newClusterNames={}
        maxDependencyInClusters=dict()
        
        # get the maximum dependency set size in each cluster
        nodes=set([k for k,v in G.in_degree().items()])
        for cn in clusterNames.keys():
            cnodes = [n for n in nodes if n in clusterNames[cn]]
            maxDependencySetSize = max([ G.node[k][ConstructionOrdering.kAttrNameNodeDependentSetSize] for k in cnodes])
            maxDependencyInClusters[cn]=maxDependencySetSize
        
        # start point is the one with the largest dependency set
        start_index=max(maxDependencyInClusters.keys(),key=lambda k: maxDependencyInClusters[k])
        center_x=np.mean([s.X for s in SupplyPosition])
        center_y=np.mean([s.Y for s in SupplyPosition])
        center=Point(center_x,center_y,0)

        Angles=[]
        for i in range(len(SupplyPosition)):
            v1=center.vectorTo(SupplyPosition[start_index])
            v2=center.vectorTo(SupplyPosition[i])
            Angles.append(angle_clockwise(v1,v2))

        Wall_start=[Wall[i].StartPoint for i in Wall.keys()]
        Wall_end=[Wall[i].EndPoint for i in Wall.keys()]

        # return a sudo half-space
        def findAcceptableRegion(start,end,center):
            extension_factor=100
            
            tang_vector=start.vectorTo(end)
            p1=Point(start.X+tang_vector[0]*extension_factor,start.Y+tang_vector[1]*extension_factor,0)
            p2=Point(end.X-tang_vector[0]*extension_factor,end.Y-tang_vector[1]*extension_factor,0)
            
            radius_vector=center.vectorTo(Point((start.X+end.X)/2,(start.Y+end.Y)/2,0))
            p3=Point(p2.X+radius_vector[0]*extension_factor,p2.Y+radius_vector[1]*extension_factor,0)
            p4=Point(p1.X+radius_vector[0]*extension_factor,p1.Y+radius_vector[1]*extension_factor,0)
            
            region=Polygon([(p1.X,p1.Y),(p2.X,p2.Y),(p3.X,p3.Y),(p4.X,p4.Y)])

            return region

        def plotAcceptableRegion(poly,index):

            from matplotlib import pyplot as plt
            fig_index=10+index
            fig = plt.figure(fig_index, figsize=(5,5), dpi=90)
            x,y=poly.exterior.xy
            plt.plot(x,y, color='#6699cc', alpha=0.7,linewidth=3, solid_capstyle='round', zorder=2)
            plt.fill(x, y, 'g')
            plt.xlabel('X')
            plt.ylabel('Y')
            fig_title='feasible region for Wall'+ str(index)
            plt.title(fig_title)
            title_name=str(fig_index)+".png"
            plt.savefig(title_name)
        

        # reorder the supply location clockwise
        acceptableRegionForEachCraneStop=[]
        for i in range(len(SupplyPosition)):
            index=min(range(len(Angles)),key=lambda k: Angles[k])
            Angles[index]=10000;
            newSupplyPosition.append(SupplyPosition[index])
            newClusterNames[i]=clusterNames[index]
            acceptableRegion = findAcceptableRegion(Wall_start[index],Wall_end[index],center)
            acceptableRegion = acceptableRegion.intersection(siteAcceptableRegion)
            acceptableRegionForEachCraneStop.append(acceptableRegion)
            plotAcceptableRegion(acceptableRegionForEachCraneStop[i],i)
            
        return acceptableRegionForEachCraneStop,newSupplyPosition,newClusterNames



