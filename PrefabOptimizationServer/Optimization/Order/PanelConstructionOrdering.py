class PanelConstructionOrdering(object):
    """Methods for automatically group the panels according to the number of mobile stops"""
    

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

    def clusterThePanels(points,centers):
        """cluster the points according to the center"""
        num_cluster=len(centers)
        clusterIndices=dict()
        for  index in enumerate(points):
            center_index=np.argmin([np.linalg.norm(centers[j].vectorTo(points[index[1]])) for j in range (len(centers))])
            if center_index not in clusterIndices:
                clusterIndices[center_index]=[index[1]]
            else:
                clusterIndices[center_index].append(index[1])
        return clusterIndices
    ################################################################
    def rearrangeWall(walls):
        # so far, given the correct order of the wall, and given the correct order of startPoint and endPoint 
        #in the input file is a requirement. I might want to automate this later.
         
        wallOrder=[1001,1002]
        
        print ('* so far the wall installation order is set manually, and it is assume that the wall start-end point order is the same as the installation order')
            
        return wallOrder
    ################################################################
    def getOrder(panels,clusterName,installMethod=2):
        #installMethod: 0->horizontal, 1-> vertical, 2-> diagnal
           
        def isNextTo(panela, panelb):
            bb1 = panela.getBBforZCheck()
            bb2 = panelb.getBBforZCheck()
            if (bb2.maxPoint.X < bb1.minPoint.X or bb1.maxPoint.X < bb2.minPoint.X or bb2.maxPoint.Y < bb1.minPoint.Y or bb1.maxPoint.Y < bb2.minPoint.Y or bb2.maxPoint.Z < bb1.minPoint.Z or bb1.maxPoint.Z < bb2.minPoint.Z):
                return False
            else:
                return True

        def BisLeftUpA(panela,panelb):
            buff=1
            if panelb.CenterPoint.X+buff<panela.CenterPoint.X and panelb.CenterPoint.Z>panela.CenterPoint.Z:
                return True
            else:
                return False

        def findNextDiag(P,Pset):
            relativePanels = [p for p in Pset if  isNextTo(panels[P],panels[p])]
            nextDiag=[p for p in relativePanels if BisLeftUpA(panels[P],panels[p])]

            if len(nextDiag)>0:
                return nextDiag[0]
            else:
                return None

        def findTheFirst(Pset):
            Zbuff=1
            heightDimen=min([panels[p].CenterPoint.Z for p in Pset])+Zbuff;
            firstRow={p:panels[p].CenterPoint for p in Pset if panels[p].CenterPoint.Z<=heightDimen}
            firstPanel=min(firstRow, key=lambda x: firstRow[x].X)

            return firstPanel
        
        order=[]
        Zbuff=1
        XYbuff=1

        if installMethod == 0: # horizontal
            for i in range(len(clusterName)):
                subset=clusterName[i];
                suborder=[]
                while len(subset) >0:
                    rowHeight=min([panels[p].CenterPoint.Z for p in subset])+Zbuff;
                    currentRow={p:panels[p].CenterPoint for p in subset if panels[p].CenterPoint.Z<=rowHeight}
                    subset= set(k for k in subset if k not in currentRow.keys())

                    while len(currentRow) >0:
                        firstPanel=min(currentRow, key=lambda x: currentRow[x].X)
                        suborder.append(firstPanel)
                        del currentRow[firstPanel]        
                
                order.append(suborder)

        elif installMethod == 1: # vertical
            
            for i in range(len(clusterName)):
                subset=clusterName[i];
                suborder=[]
                while len(subset) >0:
                    rowDimen=min([panels[p].CenterPoint.X for p in subset])+XYbuff;
                    currentColumn={p:panels[p].CenterPoint for p in subset if panels[p].CenterPoint.X<=rowDimen}
                    subset= set(k for k in subset if k not in currentColumn.keys())

                    while len(currentColumn) >0:
                        firstPanel=min(currentColumn, key=lambda x: currentColumn[x].Z)
                        suborder.append(firstPanel)
                        del currentColumn[firstPanel]        
                
                order.append(suborder)

        elif installMethod == 2: #diagnal
            for i in range(len(clusterName)):
                subset=clusterName[i];
                suborder=[]
                while len(subset) >0:
                    firstPanel=findTheFirst(subset)
                    suborder.append(firstPanel)
                    subset.remove(firstPanel)
                    
                    nextInDiag=findNextDiag(firstPanel,subset)

                    while nextInDiag is not None:
                        suborder.append(nextInDiag)
                        subset.remove(nextInDiag)

                        nextInDiag=findNextDiag(nextInDiag,subset)
                        
                order.append(suborder)

        return order
    ###############################################################################
    # for current point it is manually set the installation method#################
    ###############################################################################
    def getPanelInstallOrder(OrigPanels,walls, numStop,installMethod=-1):
        """
            Gets sequential order according to cluster
           One structualObject from cluster at single order position
        """
        # going to change the panels X value for ordering convenience
        import copy
        panels=copy.deepcopy(OrigPanels)


        def findNumStopPerWall(walls,numStop):
            """"""
            import numpy as np

            wallLength={}
            numStopsPerWall={}
            for wall in walls:
                wallLength[wall]=np.linalg.norm(walls[wall]._startPoint.vectorTo(walls[wall]._endPoint))
            
            normalizing=sum(wallLength.values())/numStop
            wallLength={wall:wallLength[wall]/normalizing-1 for wall in wallLength.keys()}
            for wall in walls:
                numStopsPerWall[wall]=1+int(round(wallLength[wall]))
                numStop=numStop-int(round(wallLength[wall]))-1

            return numStopsPerWall

        def findTheGroupPerWall(wall,numGroup):
            """
            """
            import numpy as np
            panels=wall._panels;
            panelsPerWall={}
            segment=np.zeros([2,2])
            sp=wall.StartPoint
            ep=wall.EndPoint

            DiffX=abs(sp.X-ep.X)
            DiffY=abs(sp.Y-ep.Y)

            for i in range(numGroup):
                segment[0][0]=sp.X+(ep.X-sp.X)*(i/numGroup)
                segment[1][0]=sp.X+(ep.X-sp.X)*((i+1)/numGroup)
                segment[0][1]=sp.Y+(ep.Y-sp.Y)*(i/numGroup)
                segment[1][1]=sp.Y+(ep.Y-sp.Y)*((i+1)/numGroup)

                if segment[0][0]>segment[1][0]:
                    segment[0][0],segment[1][0]=segment[1][0],segment[0][0]

                if segment[0][1]>segment[1][1]:
                    segment[0][1],segment[1][1]=segment[1][1],segment[0][1]
                
                if(DiffX>DiffY and segment[1][0]>segment[0][0]):
                    subPanelGroup=[panels[p].Id for p in panels if panels[p].CenterPoint.X<segment[1][0] and panels[p].CenterPoint.X>segment[0][0]]
                else:
                    subPanelGroup=[panels[p].Id for p in panels if panels[p].CenterPoint.Y<segment[1][1] and panels[p].CenterPoint.Y>segment[0][1]]
                panelsPerWall[i]=subPanelGroup

            return panelsPerWall
       
        def  mapPanelToPositiveDirection(panels,walls):
            import numpy as np
            for w in walls:
                sx=walls[w].StartPoint.X
                sy=walls[w].StartPoint.Y
                for p in walls[w]._panels.keys():

                    panels[p].CenterPoint.X=np.sqrt(pow((panels[p].CenterPoint.X-sx),2)+pow((panels[p].CenterPoint.Y-sy),2))
                    panels[p].CenterPoint.Y=0
            return panels
       
        
        wallOrder=PanelConstructionOrdering.rearrangeWall(walls)

        numWall=len(walls)
        panelGroup=[]

        if(numWall>numStop):
            print ("the number of Stop should be greater than the number of walls")
            exist
        elif numWall==numStop:  
            for key in walls:
                panelPerWall=list(walls[key]._panels.keys())
                panelGroup.append(panelPerWall)

        else:
            numStopsPerWall=findNumStopPerWall(walls,numStop)
            
            for wall in wallOrder:
                groupsPerWall=findTheGroupPerWall(walls[wall],numStopsPerWall[wall])
                for j in range(numStopsPerWall[wall]):
                    panelGroup.append(groupsPerWall[j])

        panels=mapPanelToPositiveDirection(panels,walls)

        if installMethod is -1:
            print ("* the installation method is manually set in the function --getPanelInstallOrder-- as diagnal  here")
            installMethod=2

        Orders=PanelConstructionOrdering.getOrder(panels,panelGroup,installMethod)
        
        
        return Orders

    
    ########################################################################################
    def getSupplyPointAndAcceptableLocation(siteAcceptableRegion,Panels,clusterName,MinWorkRadiu,MaxWorkRadiu):

        import numpy as np
        from BLGeometry.PrefabGeometry import Point
        from shapely.geometry import Polygon

        # return a sudo half-space
        def findAcceptableRegion(start,end,siteAcceptableRegion,MinWorkRadiu,MaxWorkRadiu,center):
            extend=MaxWorkRadiu*0.2

            tang_vector=start.vectorTo(end)

            length = np.sqrt(tang_vector[0] ** 2 + tang_vector[1] ** 2)
            ux, uy = tang_vector[0] / length, tang_vector[1] / length
            
            # compute the normalized perpendicular vector
            vx, vy = -uy, ux

            # adjust the direction pointed to feasible region
            dir_vector=center.vectorTo(end)
            dir_sign=dir_vector[0]*vx+dir_vector[1]*vy

            if dir_sign<0:
                vx,vy=-vx,-vy

            MaxWorkRadiu=MaxWorkRadiu*0.8
            p1=Point(start.X+vx*MaxWorkRadiu-ux*extend,start.Y+vy*MaxWorkRadiu-uy*extend,0)
            p2=Point(end.X+vx*MaxWorkRadiu+ux*extend,end.Y+vy*MaxWorkRadiu+uy*extend,0)
            p3=Point(end.X+vx*MinWorkRadiu+ux*extend,end.Y+vy*MinWorkRadiu+uy*extend,0)
            p4=Point(start.X+vx*MinWorkRadiu-ux*extend,start.Y+vy*MinWorkRadiu-uy*extend,0)

            region=Polygon([(p1.X,p1.Y),(p2.X,p2.Y),(p3.X,p3.Y),(p4.X,p4.Y)])
            Region = region.intersection(siteAcceptableRegion)

            return Region


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
        
        #siteAcceptableRegion=Data.AcceptableRegionForCrane
 
        RawSupplyPoints = []
        group_start=[]
        group_end=[]

        for i in range(len(clusterName)):
            maxX=max([Panels[p].CenterPoint.X for p in clusterName[i]])
            maxY=max([Panels[p].CenterPoint.Y for p in clusterName[i]])
            minX=min([Panels[p].CenterPoint.X for p in clusterName[i]])
            minY=min([Panels[p].CenterPoint.Y for p in clusterName[i]])

            x=(maxX+minX)/2.0
            y=(maxY+minY)/2.0

            RawSupplyPoints.append(Point(x,y,0))
            group_start.append(Point(minX,minY,0))
            group_end.append(Point(maxX,maxY,0))

        center_x=np.mean([s.X for s in RawSupplyPoints])
        center_y=np.mean([s.Y for s in RawSupplyPoints])
        center=Point(center_x,center_y,0)

        # reorder the supply location clockwise
        acceptableRegionForEachCraneStop=[]
        for i in range(len(RawSupplyPoints)):
            acceptableRegion = findAcceptableRegion(group_start[i],group_end[i],siteAcceptableRegion,MinWorkRadiu,MaxWorkRadiu,center)
            acceptableRegionForEachCraneStop.append(acceptableRegion)
            plotAcceptableRegion(acceptableRegionForEachCraneStop[i],i)
            
        return RawSupplyPoints,acceptableRegionForEachCraneStop



