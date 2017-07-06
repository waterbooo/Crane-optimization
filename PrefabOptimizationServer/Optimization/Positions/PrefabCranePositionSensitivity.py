import math, random, deap, sys, os, traceback, urllib, logging
__filePath = os.path.dirname(os.path.abspath(__file__))

__GeomPath = os.path.join(__filePath, "BLGeometry")
if not __GeomPath in sys.path:
    sys.path.insert(1, __GeomPath)

from enum import Enum
from BLGeometry.PrefabGeometry import Point
from BLGeometry.BoundingStructures import BoundingBox
from Optimization.DataStructures.CraneData import CraneData
from Optimization.DataStructures.TowerCraneData import TowerCraneData
from Optimization.DataStructures.MobileCraneData import MobileCraneData
from Optimization.DataStructures.SiteData import SiteData
from Optimization.Clustering.KMeansBasedBarsDivision import KMeansBasedBarsDivision as kmeans
from Optimization.Order.ConstructionOrdering import ConstructionOrdering
from deap import creator, tools, base, algorithms
from operator import attrgetter, eq
from Optimization.Utils.GATools import varInterval, varLambdaInterval
import numpy as np
from BLGeometry import GeometryUtils
from pprint import pprint
from EndpointConstants import EndpointConstants as ec

class CranePlacementGAData(object):
    """All data needed for crane placement optimization"""
    def __init__(self, *args, **kwargs):
        self._cranes = []
        self._supplyPoints = []
        self._clusterIndices = []
        self._clusterNames = []
        self._prohibitedRegion = None
        self._acceptableRegionForMaterials = None
        self._acceptableRegionForCranes = None
        self._numberOfObjects = 0
        self._demandPoints = []
        self._oneCraneEllipsePolygon = None
        self._constructionOrder = []
        self._objWeights = {}
        self._bounds = []
        self._installationTime = 0
        self._numberOfStops=[]
        self._denpendencies=None
        self._acceptableRegionForEachCraneStop=[]
        self._numCrew=0
        self._installMethod=None
        return super().__init__(*args, **kwargs)

    @property
    def InstallMethod(self):
        return self._installMethod

    @InstallMethod.setter
    def InstallMethod(self,value):
        self._installMethod=value

    @property
    def NumCrew(self):
        return self._numCrew

    @NumCrew.setter
    def NumCrew(self,value):
        self._numCrew=value

    @property
    def AcceptableRegionForEachCraneStop(self):
        return self._acceptableRegionForEachCraneStop

    @AcceptableRegionForEachCraneStop.setter
    def AcceptableRegionForEachCraneStop(self,value):
        self._acceptableRegionForEachCraneStop=value

    @property
    def Dependencies(self):
        """
        Model dependencies graph
        """
        return self._denpendencies
   
    @Dependencies.setter
    def Dependencies(self,value):
        self._denpendencies = value

    @property
    def NumberOfStops(self):
        """Required number of stops for each mobile crane"""
        return self._numberOfStops

    @NumberOfStops.setter
    def NumberOfStops(self,value):
        self._numberOfStops = value
    
    @property
    def InstallationTime(self):
        """Time for placing single element (NOT SURE HERE, NEEDS CHECK)"""
        return self._installationTime

    @InstallationTime.setter
    def InstallationTime(self, value):
        self._installationTime = value

    @property
    def Cranes(self):
        """Set of cranes"""
        return self._cranes

    @Cranes.setter
    def Cranes(self, value):
        self._cranes = value

    @property
    def SupplyPoints(self):
        """Supply points for each tower crane/mobile crane stop"""
        return self._supplyPoints

    @SupplyPoints.setter
    def SupplyPoints(self, value):
        self._supplyPoints = value

    @property
    def ClusterIndices(self):
        """Mapping element numbers to crane/crane stop"""
        return self._clusterIndices

    @ClusterIndices.setter
    def ClusterIndices(self, value):
        self._clusterIndices = value

    @property
    def ClusterNames(self):
        """Mapping element ids to crane/crane stop"""
        return self._clusterNames

    @ClusterNames.setter
    def ClusterNames(self, value):
        self._clusterNames = value

    @property
    def ProhibitedRegion(self):
        """Region where placement of crane/supply points is prohibited"""
        return self._prohibitedRegion

    @ProhibitedRegion.setter
    def ProhibitedRegion(self, value):
        self._prohibitedRegion = value

    @property
    def AcceptableRegionForMaterials(self):
        """Region where placement of supply points is allowed"""
        return self._acceptableRegionForMaterials

    @AcceptableRegionForMaterials.setter
    def AcceptableRegionForMaterials(self, value):
        self._acceptableRegionForMaterials = value

    @property
    def AcceptableRegionForCranes(self):
        """Region where placement of cranes is allowed"""
        return self._acceptableRegionForCranes

    @AcceptableRegionForCranes.setter
    def AcceptableRegionForCranes(self, value):
        self._acceptableRegionForCranes = value

    @property
    def NumberOfObjects(self):
        """Total number of elements in model"""
        return self._numberOfObjects

    @NumberOfObjects.setter
    def NumberOfObjects(self, value):
        self._numberOfObjects = value

    @property
    def DemandPoints(self):
        """Demand point for each element"""
        return self._demandPoints

    @DemandPoints.setter
    def DemandPoints(self, value):
        self._demandPoints = value

    @property
    def OneCraneEllipsePolygon(self):
        """Feasible region for one crane dependent on model bounding polygon"""
        return self._oneCraneEllipsePolygon

    @OneCraneEllipsePolygon.setter
    def OneCraneEllipsePolygon(self, value):
        self._oneCraneEllipsePolygon = value

    @property
    def ConstructionOrder(self):
        """Construction pre-ordering"""
        return self._constructionOrder

    @ConstructionOrder.setter
    def ConstructionOrder(self, value):
        self._constructionOrder = value

    @property
    def NumberOfCranes(self):
        """Number of cranes in process"""
        return len(self._cranes)

    @property
    def ObjectWeights(self):
        """Weights of model objects, lbs"""
        return self._objWeights

    @ObjectWeights.setter
    def ObjectWeights(self, value):
        self._objWeights = value

    @property
    def Bounds(self):
        """Bounds for each element in individual vector"""
        return self._bounds

    @Bounds.setter
    def Bounds(self, value):
        self._bounds = value

# Crosover for each component a * xi + (1 - a) * yi
# Granted feasible results 
def crossoverCraneOptPos(ind1, ind2, optData):
    """
    Crosover for each component a * xi + (1 - a) * yi
    Granted feasible results

    params:
        ind1 - first individual
        ind2 - another individual
        optData - optimization data object
    returns:
        new created individuals after crossover
    """
    threthold=0.8
    temp1 = list(ind1[0])
    temp2 = list(ind2[0])
    cxAlpha = random.random()
    for i in range(len(ind1[0])):
        ind1[0][i] = cxAlpha * temp1[i] + (1 - cxAlpha) * temp2[i]
        ind2[0][i] = (1 - cxAlpha) * temp1[i] + cxAlpha * temp2[i]

    for i in range(len(ind1[0])//2):     
        
        p = Point(ind1[0][i*2], ind1[0][i*2+1])
        index=int(i)
        p = nearestAcceptablePoint(p, optData.ProhibitedRegion, optData.AcceptableRegionForEachCraneStop[index])
        ind1[0][2*i] = p.X
        ind1[0][i*2 + 1] = p.Y

        p = Point(ind2[0][i*2], ind2[0][i*2+1])
        p = nearestAcceptablePoint(p, optData.ProhibitedRegion, optData.AcceptableRegionForEachCraneStop[index])
        ind2[0][i*2] = p.X
        ind2[0][i*2 + 1] = p.Y
    
    return ind1, ind2

def mutationOneCraneOptPos(ind, optData):
    """
    mutation operation

    params:
        ind - individual for applying mutation on
        optData - optimization data object
    returns:
        mutated individual
    """
    # supplyLength = craneData.maxLength
    # Make all atributes random in range and then make attributes acceptable
    threthold=0.8
    ind_t=[]
    
    """
    for i in range(len(optData.Bounds)):
        bounds = optData.Bounds[i]
        ind_t.append(random.uniform(bounds[0], bounds[1]))
    """

    # Check for points acceptance and project if needed
    for i in range(len(ind[0]) // 2):
        r = random.uniform(-0.5, 0.5)
        p = Point(ind[0][i*2]*(1+r), ind[0][i*2+1]*(1+r))
        index=int(i)
        cxAlpha = random.random()
        if cxAlpha>threthold:
            p = nearestAcceptablePoint(p, optData.ProhibitedRegion, optData.AcceptableRegionForEachCraneStop[index])
            ind[0][i*2] = p.X
            ind[0][i*2 + 1] = p.Y
    return ind,

def acceptableProjection(point, region):
    """
    Projecttion on a border of passed region

    params:
        point - point to project
        region - region to project point on, acceptable region for point
    returns:
        tuple of projection coordinates
    """
    from shapely.geometry import MultiPolygon
    pols = [region]
    if isinstance(region, MultiPolygon):
        pols = region.geoms
                    
    # Get projection point
    coords = GeometryUtils.GetNearestPointOnAreaBound(point, pols)
    return coords

def nearestAcceptablePoint(point, prohibitedRegion, acceptableRegion):
    """Gets a projection of point to acceptable region
       If no acceptable region passed point is projected outside prohibited region
       If the position is already acceptable then initial value is returned
    """
    if not prohibitedRegion and not acceptableRegion:
        # If no border regions defined there is no distance
        return np.array([point.X, point.Y])
    else:
        from shapely.geometry import Point as ShPoint
        from shapely.geometry import MultiPolygon
        region = None
        shp = ShPoint(point.X, point.Y)
        if prohibitedRegion and not acceptableRegion:
            # If there is prohibited region and no acceptable region defined 
            # project points on prohibited region border nearest point
            region = prohibitedRegion

            # Check whether p in region polygon
            if shp.within(region):
                coords = acceptableProjection(shp, region)
                return Point(coords[0],coords[1],0)
                    
        if acceptableRegion:
            # Project on border of acceptable region if any
            region = acceptableRegion

            # Check whether p in region polygon 
            if not shp.within(region):
                coords = acceptableProjection(shp, region)
                return Point(coords[0],coords[1],0)
    return point


def getCraneDistanceToAcceptableRegion(point, prohibitedRegion, acceptableRegion):
    """Returns distance to acceptable region for crane point"""
    coords = nearestAcceptablePoint(point, prohibitedRegion, acceptableRegion)
    return np.linalg.norm(np.array([coords.X - point.X, coords.Y - point.Y]))

def evaluateCraneOptPos(individual, optData, genAnimations = False):
    
    tolerance = 0.00000001
    # crane coordinates vector (Xc, Yc) - variable, coordinate system corresponds to revit one, units are feet
    cranePositions = [Point(individual[0][i], individual[0][i + 1], 0.0) for i in range(optData.NumberOfCranes)]
    
    # supply point (Xs, Ys) - variable, coordinate system corresponds to revit one, units are feet
    # TODO: add Z dimension, set maximum Z height of group and group bars by order/weight/type to be real data
    supplyPoints = optData.SupplyPoints

    # check if acceptable and penalty if not
    distances = [getCraneDistanceToAcceptableRegion(cp, optData.ProhibitedRegion, optData.AcceptableRegionForCranes) for cp in cranePositions] # ft
    craneDistance = max(distances)
    acceptable = craneDistance <= tolerance

    if not acceptable:
        big_number=10000000
        if genAnimations:
            return (big_number,)
            return (len(optData.ConstructionOrder) * (200.0 + craneDistance), [len(optData.ConstructionOrder) * (200.0 + craneDistance)], [0])

        if craneDistance > tolerance:
            return (big_number,)
            return (len(optData.ConstructionOrder) * (200.0 + craneDistance),)
        else:
            return (big_number,)
            return (len(optData.ConstructionOrder) * (100.0 + supplyDistance),)

    # demand points matrix (Xdj, Ydj, Zdj) - constants, coordinate system corresponds to revit one, units are feet
    demandPoints = optData.DemandPoints

    # slewing velocity of crane jib (w)                   - constant, ft/min
    Va = [c.trolleyVelocity for c in optData.Cranes]
    VaDiv = [1.0 / va for va in Va]

    # radial velocity of trolley (Va)                     - constant, rad/min
    w = [c.jibRadialVelocity for c in optData.Cranes]
    wDiv = [1.0 / ww for ww in w] 

    emptyCapacityLiftingDiv = [1.0 / c.getSpeedForCapacity(0.0) for c in optData.Cranes]
    
    # cycle time between supply (i) and demand (j) (Tij)  - variable, min
    Tij = []

    maxLength = [c.getMaxLength() for c in optData.Cranes]

    # crane-to-supply distance (Li) - variable (at the moment just one supply point), ft
    liV = [cranePositions[i].vectorTo(supplyPoints[i]) for i in range(optData.NumberOfCranes)]
    li = [np.linalg.norm(liv) for liv in liV]

    numGrew=optData.NumGrew

    for orderEl in optData.ConstructionOrder:
        elems = orderEl
        if not isinstance(orderEl, list):
            elems = [orderEl]
        tis = []
        for index in range(len(elems)):
            elem = elems[index]
            if elem:
                # quantity of material to be handled from 
                #       supply (i) to demand (j) (Qij)                      - constant, lbs
                Qij = optData.ObjectWeights[elems[index]]

                # crane-to-supply distance (Li) - variable (at the moment just one supply point), ft
                liCapacity = optData.Cranes[index].getMaxCapacityForRadius(li[index])

                # crane-to-demand distance (Lj) - variable, ft
                ljV = cranePositions[index].vectorTo(optData.DemandPoints[elems[index]])
                lj = np.linalg.norm(ljV)
        
                ljCapacity = optData.Cranes[index].getMaxCapacityForRadius(lj)
    
                if li[index] <= maxLength[index] and lj <= maxLength[index] and Qij <= liCapacity and Qij <= ljCapacity:        

                    # vertical supply to demand (Zij) - constant, ft
                    #zij = supplyPoints[index].verticalDistanceTo(demandPoints[index])
                    zij = supplyPoints[index].verticalDistanceTo(optData.DemandPoints[elems[index]])
    
                    # angle between Li and Lj (THij) - variable, rad
                    Theta_ij = GeometryUtils.angleBetween(liV[index], ljV)

                    # time for trolley radial movement (Ta) - variable, min
                    Ta = np.fabs(li[index] - lj) * VaDiv[index]

                    # time for trolley tangent movement (Tw)              - variable, min
                    Tw = Theta_ij * wDiv[index]

                    # time for hook horizontal travel - variable, min
                    Thij = np.max([Ta, Tw]) + optData.Cranes[index].alpha * np.min([Ta, Tw])

                    # time for hook vertical travel - const
                    # vertical hoisting time when the hook is             - variable, min
                    #       loaded (TLij)
                    TLvij = zij / optData.Cranes[index].getSpeedForCapacity(Qij)

                    # vertical hoisting time when the hook is unloaded    - variable, min
                    #       (TUij)    
                    TUvij = zij * emptyCapacityLiftingDiv[index]

                    tis.append(TLvij + TUvij + 2 * Thij )
                else:
                    # take in account maximum capacity. In case of unacceptable length add large time
                    # 10000 minutes is very long time for one beam placement, min
                    tis.append(10000.0)

                Tij.append(max(tis)) # times for each element in min

    if genAnimations:
        return (sum(Tij),[sum(Tij)],[0]) # result is in minutes

    return (sum(Tij),)

# just evaluate one crane. 
# extend it to mutiple crane later
def evaluateMobileCraneOptPosSens(individual, optData, genAnimations = False):
    
    panel_hook_time=1
    crane_crew_overlap_time=1

    tolerance = 0.0001
    # for pso datastructure consistency
    if  len(np.array(individual).shape)==2:
        individual=individual[0] 
    # crane coordinates vector (Xc, Yc) - variable, coordinate system corresponds to revit one, units are feet
    # for one crane only at this point
    # --unit for individual should be feet. 
    cranePositions = [Point(individual[i*2], individual[i*2+1], 0.0) for i in range(optData.NumberOfStops[0])]

    # supply point (Xs, Ys) - variable, coordinate system corresponds to revit one, units are feet
    # TODO: add Z dimension, set maximum Z height of group and group bars by order/weight/type to be real data
    supplyPoints = optData.SupplyPoints

    # check if acceptable and penalty if not
    # --unit for distance/craneDistance should be feet
    distances = [getCraneDistanceToAcceptableRegion(cp, optData.ProhibitedRegion, optData.AcceptableRegionForCranes) for cp in cranePositions]
    craneDistance = max(distances)
    acceptable = craneDistance <= tolerance

    if not acceptable:
        big_number=10000
        if  craneDistance > tolerance:
            return (big_number * (200.0 + craneDistance),)
        else:
            return (big_number * (100.0 + supplyDistance),)

    # demand points matrix (Xdj, Ydj, Zdj) - constants, coordinate system corresponds to revit one, units are feet

    demandPoints = optData.DemandPoints

    # slewing velocity of crane jib (Vs)                   - constant
    # --unit for Vs should be radian/minute
    # --unit for VaDiv is minute/radian
    Vs = optData.Cranes[0].getSlewVelocity()
    VsDiv = 1.0 / Vs

    # radial velocity of Boom Angle (Va)                     - constant
    # --unit for Va is radian/minute
    # --unit for VaDiv is minute/radian
    Va = optData.Cranes[0].getBoomAngleVelocity() 
    VaDiv = 1.0/Va

    # radial velocity of Boom Length (Va)                     - constant
    # --unit for Vl is feet/minute
    # --unit for VlDiv is minute/feet
    Vl = optData.Cranes[0].getBoomLengthVelocity() 
    VlDiv = 1.0 / Vl 

    # the hook lifting velocity inverse when cupsection is empty
    # --unit for emptyCupLiftingDiv is minute/feet
    emptyCupLiftingDiv = 1.0 / optData.Cranes[0].getSpeedForCapacity(0.0)
    
    # cycle time when the cupsection is loaded  - variable
    # --unit is minute
    Tl =[]
    # cycle time when the cupsection is not loaded, and Te[0]=0;
    # -- unit is minute
    Tu=[]
    # cycle time for the crane moves on its wheel
    # --unit is minute
    Tm=[]

    # crane-to-supply distance (Li) - variable (at the moment just one supply point)
    # at current time, a supply point is attached to each crane position
    # --the unit for lsV is feet 
    lsV = [cranePositions[i].vectorTo(supplyPoints[i]) for i in range(optData.NumberOfStops[0])]
    ls = [np.linalg.norm(liv) for liv in lsV]

    # --unit for TotalConstructioTime is minute
    TotalConstructionTime = []
    # -- unit for TotalMoveTime is minute
    TotalMoveTime = []

    # we do assume that the construction order is consitent with the crane position ordering
    position_index_before=0;
    print_str=[]
    feasibility=1
    C_total=0

    for orderIndex in range(len(optData.ConstructionOrder)):
        elems = optData.ConstructionOrder[orderIndex]
        if not isinstance(elems, list):
            elems = [elems]

        if genAnimations:
            TlforOne = []
            TuforOne = []
            TmforOne = []

        for elemIndex in range(len(elems)):
            elem = elems[elemIndex]
            

            if elem:
                # quantity of material to be handled from 
                # supply to demand weight (Q)                      - constant
                # -- unit for Q is the lb
                Q = optData.ObjectWeights[elems[elemIndex]]
        
                # crane-to-demand distance (Ld) - variable
                # a fair direct logic: that the closest crane point to i th demand point is chosen to the crane position
                position_index= orderIndex

                # --unit for ldV and ld is the feet
                ldV=cranePositions[position_index].vectorTo(optData.DemandPoints[elems[elemIndex]])
                ld = np.linalg.norm(ldV)

                if isinstance(optData.Cranes[0], MobileCraneData):
                    # set the longest crane length by default
                    if optData.Cranes[0].boomLength is None:
                        optData.Cranes[0].setBoomLength()

                # -- unit for lb is feet
                lb=optData.Cranes[0].boomLength

                # horizontal angle between start point and destination point (THij) - variable
                # -- unit for Theta_sd is radian
                Theta_sd = GeometryUtils.angleBetween(lsV[position_index], ldV)

                # time for boom slew movement (Tw)              - variable
                # -- unit for Tw is minute
                Tw = Theta_sd * VsDiv
                
                #print_str.append('Theta_sd:{:6.2f}'.format(Theta_sd)+'VsDiv:{:6.2f}'.format(VsDiv)+'Tw:{:6.2f}'.format(Tw))

                # Time in regarding the boom angle change            - variable
                # Verticle boom angle
                # -- unit is radian for alpha_d and alpha_s

                if (ld/lb<=1):
                    alpha_d=np.arccos(ld/lb)
                else:
                    alpha_d=np.arccos(1.0)

                if (ls[position_index]/lb<=1):
                    alpha_s=np.arccos(ls[position_index]/lb)
                else:
                    alpha_s=np.arccos(1.0)
                Ta=np.abs(alpha_d-alpha_s)*VaDiv
                
                #print_str.append('alpha_d:{:6.2f} '.format(alpha_d)+'alpha_s:{:6.2f} '.format(alpha_s)+'Ta:{:6.2f} '.format(Ta))
                
                #  verticle distance change due to the change of boom angle
                # -- unit for zva is feet
                zva=lb*(np.sin(alpha_d)-np.sin(alpha_s))

                # z_sd the vertical distance from demand point to supply point
                # --unit for z_sd is feet

                z_sd = supplyPoints[position_index].verticalDistanceTo(optData.DemandPoints[elems[elemIndex]])

                # zv is the vertical distance that a cupsection moves. 
                zv=np.abs(zva-z_sd) # add an panelty if demand point can not be reached when verticle distance is considered

                # Tvh is the time for cupsection verticle moves at load Q vertically
                # -- unit for Tvh is minute
                Tvh = zv / optData.Cranes[0].getSpeedForCapacity(Q)
             
                #print_str.append('zva:{:6.2f} '.format(zva)+'z_sd:{:6.2f} '.format(z_sd)+'zv:{:6.2f} '.format(zv)+'Tvh:{:6.2f}'.format(Tvh))
          
                # vertical hoisting time when the hook is unloaded    - variable
                # -- unit for TUvh is minute
                TUvh = zv * emptyCupLiftingDiv

                # time for boom moves (slew+angle change)
                # -- unit for Th is minute
                Th = np.max([Ta, Tw]) + optData.Cranes[0].alpha * np.min([Ta, Tw])

                # so far consider the installation time is independent with the hook traveling time
                # they will be considered as coupled variables later
                # --unit for Tli and Tui is minute
                Tli=Tvh +  Th 
                Tui=TUvh + Th
                
                #print_str.append('TUvh:{:6.2f} '.format(TUvh)+'Th:{:6.2f} '.format(Th.item())+'Tli:{:6.2f} '.format(Tli.item())+'Tui:{:6.2f} \n'.format(Tui.item()))

                # This next part is to check the constraints violation and then add penalty
                # min working radius for given boom length
                # -- unit for minRadius is feet
                minRadius=optData.Cranes[0].getMinRadius();

                # capacity for crane-to-demand point
                # -- unit for ldCapacity is lb
                ldCapacity = optData.Cranes[0].getMaxCapacityForRadius(ld)

                # capacity for crane-to-supply distance (Ls) 
                # -- unit for lsCapacity is lb
                lsCapacity = optData.Cranes[0].getMaxCapacityForRadius(ls[position_index])

                # -- unit for maxRadius is feet
                maxRadius = optData.Cranes[0].getMaxRadius()

                # -- the distance between crane to demand point
                lld=np.sqrt(pow(ld,2)+pow(z_sd,2))

                # C is a penalty constant
                # -- no unit for C
                C=0
                if ls[position_index] > (maxRadius):
                    C=C+(ls[position_index]-maxRadius)/float(maxRadius)
                if ld > (maxRadius):
                    C=C+(ld-maxRadius)/float(maxRadius)
                if ls[position_index]<minRadius:
                    C=C+(minRadius-ls[position_index])/float(minRadius)  
                if ld < minRadius:
                    C=C+ (minRadius-ld)/float(minRadius)
                if Q > lsCapacity:
                    C=C+ (Q-lsCapacity)/float(lsCapacity)
                if Q > ldCapacity:
                    C=C+(Q-ldCapacity)/ float(ldCapacity)
                if lld>lb:
                    C=C+(lld)/lb

                # add penalty (C+1)^3 to the lifting time with and without load
                # -- unit for tl and tu is minute
                tl=Tli*np.power((C+1),5)
                tu=Tui*np.power((C+1),5)
                C_total=C_total+C

                if (C>tolerance):
                    feasibility=0;

                # crane movement time in each installation cycle:
                if position_index == position_index_before:
                    tm=0
                else:
                    # distance measures the distance between two crane stop locaitons
                    # --unit for distance is minute

                    distance=np.linalg.norm(cranePositions[position_index].vectorTo(cranePositions[position_index_before]))
                    tm=optData.Cranes[0].getMovingTime(distance)
                    position_index_before=position_index
                
                Tl.append(tl+panel_hook_time)
                Tu.append(tu)
                Tm.append(tm)
                
                if genAnimations:
                    TlforOne.append(tl)
                    TuforOne.append(tu)
                    TmforOne.append(tm)

                

        if genAnimations:
            if orderIndex > 0 and len(elems) == 0:
                distance=np.linalg.norm(cranePositions[orderIndex].vectorTo(cranePositions[orderIndex - 1]))
                tm=optData.Cranes[0].getMovingTime(distance)
                TmforOne.append(tm)

            TotalConstructionTime.append(max(sum([sum(TlforOne),sum(TuforOne)]), optData.InstallationTime))
            TotalMoveTime.append(sum(TmforOne))

    # add installation time, as defined in optData
    # -- unit for Tinst is minute
    
    vertical_speed=50 # feet per minute
    horizonal_speed=200 # feet per minute
    elevator=Point(0,0);
    tolerance=0.5

    # time for each cycle
    # unit for T is minute
    T=[]

    def calculateTravelTime(point1,point2):  
        if abs(point1.Z-point2.Z)>tolerance:
            return abs(point1.Z-point2.Z)/vertical_speed+(np.sqrt(pow(point1.X-elevator.X,2)+pow(point1.Y-elevator.Y,2))+np.sqrt(pow(point2.X-elevator.X,2)+pow(point2.Y-elevator.Y,2)))/horizonal_speed
        else:
            return np.sqrt(pow(point1.X-point2.X,2)+pow(point1.Y-point2.Y,2))/horizonal_speed

    if optData.InstallMethod != 2 or optData.NumCrew != 2 : # vertical or horizontal
        Tinst=[optData.InstallationTime]
        newOrder=[item for sublist in optData.ConstructionOrder for item in sublist]
        for Index in range(1,len(newOrder)):
            p_new=newOrder[Index]
            p_old=newOrder[Index-1]
            travelTime=calculateTravelTime(demandPoints[p_new],demandPoints[p_old]);
            if optData.NumCrew ==0:
                Tinst.append(0)
            if optData.NumCrew == 1:   
                Tinst.append(optData.InstallationTime+travelTime)
            if optData.NumCrew == 2:
                Tinst.append(max(optData.InstallationTime,travelTime))
        
        # time for each cycle is the longer time of installation time as well as the lifting time
        flatten_ordering=[item for sublist in optData.ConstructionOrder for item in sublist]
        for i in range(len(Tl)):
            Ctime=Tl[i]+Tu[i]+Tm[i]
            if Ctime<Tinst[i]:
                #print(flatten_ordering[i])
                #print(' installTime:'+str(Tinst[i])+', CraneTime:'+str(Ctime))
                T.append(Tinst[i])
            else:
                T.append(Ctime)

        T=[t+crane_crew_overlap_time for t in T]
            
    elif  optData.InstallMethod == 2 and optData.NumCrew ==2:
        newOrder=[item for sublist in optData.ConstructionOrder for item in sublist]
        Tinst=optData.InstallationTime
        T.append(max(Tl[0]+Tu[0]+Tm[0],Tinst)+crane_crew_overlap_time)

        for Index in range(2,len(newOrder)):
            if Index % 2 ==0:
                p_new=newOrder[Index]
                p_old=newOrder[Index-2]
                travelTime=calculateTravelTime(demandPoints[p_new],demandPoints[p_old])
                Tinst=optData.InstallationTime+travelTime
                Tc=Tl[Index-1]+Tu[Index-1]+Tm[Index-1]+Tl[Index]+Tu[Index]+Tm[Index]
                T.append(max(Tc,Tinst)+crane_crew_overlap_time*2)

        if len(newOrder) % 2 == 0:
            Tinst=optData.InstallationTime
            T.append(max(Tl[-1]+Tm[-1]+Tu[-1],Tinst)+crane_crew_overlap_time)
    
    sum_T=sum(T)


    if feasibility == 1:
        print ("We found a feasible solution!!!!!Cheers!!")

    return (sum_T,feasibility)

def createIndividual(optData):
    """Random individual creation
       It is not granted that crane positions for individual would be acceptable
    """
    individual = []
    for bounds in optData.Bounds:
        individual.append(random.uniform(bounds[0], bounds[1]))

    return individual

def initIndividualOneCrane(icls, index, total, shift, optData):
    """Uniform individual creation for one crane flow
       Creates an individual on a bound of ellipse which is a set of acceptable points for crane.
       index - number of point
       total - total amount of points
       shift - shift in radians for the first point
       optData - set of optimization data
    """
    individual = []
    craneEllipsePolygon = optData.OneCraneEllipsePolygon
    allowedPolygon = craneEllipsePolygon.polygon.difference(optData.ProhibitedRegion)
    p = GeometryUtils.NthPointOnEllipse(craneEllipsePolygon.x0, craneEllipsePolygon.y0, craneEllipsePolygon.a, craneEllipsePolygon.b, craneEllipsePolygon.angle, index, total, shift)
    rndShift = random.random()
    p = ((p[0]-craneEllipsePolygon.x0) * rndShift + craneEllipsePolygon.x0, (p[1]-craneEllipsePolygon.y0) * rndShift + craneEllipsePolygon.y0)

    from shapely.geometry import Point as ShPoint
    point = ShPoint(p[0], p[1])
    if not allowedPolygon.contains(point):
        p = acceptableProjection(point, allowedPolygon)

    individual.append(p[0])
    individual.append(p[1])

    return icls([individual])

def initIndividualOneMobileCrane(icls, index, total, shift, optData):
    """
       Uniform individual creation for one crane flow
       Creates an individual on a bound of ellipse which is a set of acceptable points for crane.
       index - number of point
       total - total amount of points
       shift - shift in radians for the first point
       optData - set of optimization data
    """
    # -- unit for individual should be meter, but it depends on the unit of Polygon 
    individual = []
    craneEllipsePolygon = optData.OneCraneEllipsePolygon
    allowedPolygon = craneEllipsePolygon.polygon.difference(optData.ProhibitedRegion)
    
    for i in range(optData.NumberOfStops[0]):
        poly=optData.AcceptableRegionForEachCraneStop[i]
        x,y=poly.exterior.xy

        p=random.uniform(min(x),max(x))
        individual.append(p)

        p=random.uniform(min(y),max(y))  
        individual.append(p)

    cranePositions = [Point(individual[i*2], individual[i*2+1], 0.0) for i in range(optData.NumberOfStops[0])]
    cranePositions=[nearestAcceptablePoint(cranePositions[i], optData.ProhibitedRegion, optData.AcceptableRegionForEachCraneStop[i]) for i in range(optData.NumberOfStops[0])]

    # adjust the crane position to the order how the panels installed
    # adjustedCranePositions=ConstructionOrdering.getTheCraneStopOrder(cranePositions, optData.SupplyPoints)

    #flatten the variable to a one-dimension list
    location=[[p.X,p.Y] for p in cranePositions]
    individual=list(np.reshape(location,len(individual)))

    return icls([individual])

def initIndividualMultCranes(icls, index, total, shift, optData):
    """
        Uniform init for multiple cranes
        Inits cranes in uniform squares through the bounds
    """

    individual = []
    n = int(pow(total, 0.5))
    vn = index // n
    hn = index % n

    r = np.max([cr.getMaxRadius() for cr in optData.Cranes])

    for i in range(0, len(optData.Bounds), 2):
        boundsX = optData.Bounds[i]
        boundsY = optData.Bounds[i+1]

        x = 0.0
        y = 0.0

        if index < pow(n, 2):
            x = boundsX[0] + ((boundsX[1] - boundsX[0]) / n) * (hn + 0.5)
            y = boundsY[0] + ((boundsY[1] - boundsY[0]) / n) * (vn + 0.5)
        else:
            x = random.uniform(boundsX[0], boundsX[1])
            y = random.uniform(boundsY[0], boundsY[1])

        a = r - (boundsX[1] - boundsX[0]) / 2
        b = r - (boundsY[1] - boundsY[0]) / 2
        origin = ((boundsX[1] + boundsX[0]) / 2 - (r - (boundsX[1] - boundsX[0])), (boundsY[1] + boundsY[0]) / 2 - (r - (boundsY[1] - boundsY[0])))
        craneEllipsePolygon = GeometryUtils.CreateEllipsePolygon(origin[0],origin[1], a, b, 0)
        allowedPolygon = craneEllipsePolygon.difference(optData.ProhibitedRegion)

        from shapely.geometry import Point as ShPoint
        point = ShPoint(x, y)
        if not allowedPolygon.contains(point):
            p = acceptableProjection(point, allowedPolygon)
            x = p[0]
            y = p[1]

        individual.append(x)
        individual.append(y)

    return icls([individual])

def initIndividualMultMobileCranes(icls, index, total, shift, optData):
    """
        Uniform init for multiple cranes
        Inits cranes in uniform squares through the bounds
        This part is so far has not been developed
    """
    individual = []
    n = int(pow(total, 0.5))
    vn = index // n
    hn = index % n

    r = np.max([cr.getMaxRadius() for cr in optData.Cranes])

    for i in range(0, len(optData.Bounds), 2):
        boundsX = optData.Bounds[i]
        boundsY = optData.Bounds[i+1]

        x = 0.0
        y = 0.0

        if index < pow(n, 2):
            x = boundsX[0] + ((boundsX[1] - boundsX[0]) / n) * (hn + 0.5)
            y = boundsY[0] + ((boundsY[1] - boundsY[0]) / n) * (vn + 0.5)
        else:
            x = random.uniform(boundsX[0], boundsX[1])
            y = random.uniform(boundsY[0], boundsY[1])

        a = r - (boundsX[1] - boundsX[0]) / 2
        b = r - (boundsY[1] - boundsY[0]) / 2
        origin = ((boundsX[1] + boundsX[0]) / 2 - (r - (boundsX[1] - boundsX[0])), (boundsY[1] + boundsY[0]) / 2 - (r - (boundsY[1] - boundsY[0])))

        craneEllipsePolygon = GeometryUtils.CreateEllipsePolygon(origin[0],origin[1], a, b, 0)
        allowedPolygon = craneEllipsePolygon.difference(optData.ProhibitedRegion)

        from shapely.geometry import Point as ShPoint
        point = ShPoint(x, y)
        if not allowedPolygon.contains(point):
            p = acceptableProjection(point, allowedPolygon)
            x = p[0]
            y = p[1]

        individual.append(x)
        individual.append(y)

    return icls([individual])

def initPopulation(pcls, ind_init, total, shift, optData):
    return pcls(ind_init(c, total, shift, optData) for c in range(total))

class CraneOptPosHOF(tools.HallOfFame):
    def __init__(self, maxsize, similar=eq, updCallback=None, optData=None):
        super().__init__(maxsize, similar)
        self.updCallback = updCallback
        self.optData = optData

    def update(self, population):
        super().update(population)
        self.items.sort(key=lambda ind:ind.fitness.values[0])
        if self.updCallback:
            bv = self.items[0]
            for i in range(self.optData.NumberOfCranes):
                sp = self.optData.SupplyPoints[i]
                bv = bv + [sp.X, sp.Y]
            self.updCallback(bv)

def GetCraneGAOptimizationData(siteData, cranes, installationTime=10,number_of_stop=[-1],installMethod=-1,numCrew=-1):
    """Fills crane optimization data object"""
    optData = CranePlacementGAData()

    if installMethod is -1:
        print ("set the installMethod as default: horizontal")
        installMethod=0;
    if numCrew is -1:
        print ("set the numCrew as default: 2")
        numGrew=2
    if number_of_stop[0] is -1:
        print ("set the number of stop as default : 4")
        number_of_stop=[4]

    objs = list(siteData.ConstructionObjects.values())

    # Number of bars in model
    optData.NumberOfObjects = len(objs)

    # For one crane we can define an applicable region as an ellipse
    if len(cranes) == 1:
        optData.OneCraneEllipsePolygon = siteData.craneEllipsePolygon

    optData.InstallationTime = installationTime

    # Important regions
    optData.AcceptableRegionForMaterials = siteData.acceptableRegionForMaterials
    optData.AcceptableRegionForCranes = siteData.acceptableRegionForCranes
    optData.ProhibitedRegion = siteData.prohibitedRegion

    if optData.AcceptableRegionForMaterials is None:
        craneEllipsePolygon = optData.OneCraneEllipsePolygon.polygon
        optData.AcceptableRegionForMaterials = craneEllipsePolygon.difference(optData.ProhibitedRegion)

    if optData.AcceptableRegionForCranes is None:
        craneEllipsePolygon = optData.OneCraneEllipsePolygon.polygon
        optData.AcceptableRegionForCrane = craneEllipsePolygon.difference(optData.ProhibitedRegion)
    
    
    # Information about the cranes
    # unit for crane data should be meters
    optData.Cranes = cranes

    clusterIndices = {}
    supplyPoints = []

    if isinstance(cranes[0], TowerCraneData):
        optData.pointsPerCrane = 1
        # Cluster bars between cranes

        if len(cranes) > 1:
            # Get supply points for each crane
            clusterer = kmeans()
            clusterer.AcceptableRegion = siteData.acceptableRegionForMaterials
            clusterer.ProhibitedRegion = siteData.boundingPolygon.multiPolygon
            clusterer.Radiuses = [cr.maxLength for cr in cranes]
            centers = [np.array([obj.CenterPoint.X, obj.CenterPoint.Y]) for obj in objs]
            supplyPoints, clusters, clusterIndices = clusterer.FindCenters(centers, len(cranes))
        else:
            sp = siteData.GetSupplyPoints()[0]
            supplyPoints.append(np.array([sp.X, sp.Y]))
            clusters = {0: [np.array([obj.CenterPoint.X, obj.CenterPoint.Y]) for obj in objs]}
            clusterIndices[0] = [i for i in range(optData.NumberOfObjects)]

        optData.ClusterIndices = clusterIndices
    
        clusterNames = {}
        for k in clusterIndices.keys():
            clusterNames[k] = [objs[i].Id for i in clusterIndices[k]]


        from Optimization.Order.BarDependencyChecker import BarDependencyChecker
        from Optimization.Order.ConstructionOrdering import ConstructionOrdering
        logging.debug("Dependency graph")
        BarDependencyChecker.buildDependencyGraph(siteData)

        order = []
        # so far only for panel
        if len(optData.Cranes) > 1:
            # haven't implement
            order = ConstructionOrdering.GetConstructionOrderClustered(siteData.dependencies, objs, clusterIndices) 
        else:
            order = ConstructionOrdering.GetConstructionOrder(siteData.dependencies, objs)

        logging.debug("Construction order")
        optData.ConstructionOrder = order
        
        #optData.ClusterNames = clusterNames
        optData.SupplyPoints =  supplyPoints
    
        # Get demand points
        optData.DemandPoints = {}
        optData.ObjectWeights = {}
        for obj in objs:
            optData.DemandPoints[obj.Id] = obj.CenterPoint
            optData.ObjectWeights[obj.Id] = obj.Weight

        # Initialization bounds
        optData.Bounds = []

        logging.debug("Bounding box")

        for i in range(len(cranes)):
            craneDeltaX = cranes[i].baseSizeX / 2
            craneDeltaY = cranes[i].baseSizeY / 2

            elems = [obj for obj in objs if obj.Id in clusterNames[i]]

            bb = BoundingBox()
            bb.maxPoint.X = np.max([np.max([obj.CenterPoint.X, obj.StartPoint.X, obj.EndPoint.X]) for obj in elems]) + craneDeltaX
            bb.maxPoint.Y = np.max([np.max([obj.CenterPoint.Y, obj.StartPoint.Y, obj.EndPoint.Y]) for obj in elems]) + craneDeltaY
            bb.minPoint.X = np.min([np.min([obj.CenterPoint.X, obj.StartPoint.X, obj.EndPoint.X]) for obj in elems]) - craneDeltaX
            bb.minPoint.Y = np.min([np.min([obj.CenterPoint.Y, obj.StartPoint.Y, obj.EndPoint.Y]) for obj in elems]) - craneDeltaY

            bbSizes = (abs(bb.maxPoint.X - bb.minPoint.X), abs(bb.maxPoint.Y - bb.minPoint.Y))

            deltaX = cranes[i].maxLength - bbSizes[0]
            optData.Bounds.append((bb.minPoint.X - deltaX, bb.maxPoint.X + deltaX))
            deltaY = cranes[i].maxLength - bbSizes[1]
            optData.Bounds.append((bb.minPoint.Y - deltaY, bb.maxPoint.Y + deltaY))
    else:
        from Optimization.Order.PanelConstructionOrdering import PanelConstructionOrdering
        pco= PanelConstructionOrdering

        # determine the number of stops the crane needed
        print ("* so far design for single crane optimization problem")
        print ("* hardcode the number of stop, see function -- GetCraneGAOptimizationData ")
        
        optData.NumCrew=numCrew
        optData.InstallMethod=installMethod

        if number_of_stop!=0:
            optData.NumberOfStops=number_of_stop;
        else:
            optData.NumberOfStops=[len(siteData.Walls)]

        logging.debug("Finding order")
        
        #dummy,clusters, clusterIndices = clusterer.FindCenters(centers, optData.NumberOfStops[0]) # cluster it according to the coordinate
        order=pco.getPanelInstallOrder(siteData.Panels,siteData.Walls,optData.NumberOfStops[0],installMethod) 
        optData.ConstructionOrder = order

        logging.debug("Getting supply points")

        # -- unit for supplyPoint should be feet
        # the supply point has been arranged in clockwise(or counterclockwise)
        # supplyPoints = GetSupplyPointsAccordingToCraneStop(siteData,order)

        minWorkRadius=cranes[0].getMinRadius();
        maxWorkRadius=cranes[0].getMaxRadius();
        rawSP,acceptableRegionForEachCraneStop=pco.getSupplyPointAndAcceptableLocation(optData.AcceptableRegionForCrane,siteData.Panels,order,minWorkRadius,maxWorkRadius)
        supplyPoints=[nearestAcceptablePoint(rawSP[i], siteData.prohibitedRegion, siteData.acceptableRegionForMaterials) for i in range(len(rawSP))]

        optData.AcceptableRegionForEachCraneStop=acceptableRegionForEachCraneStop
        optData.SupplyPoints =  supplyPoints
    
        # Get demand points
        optData.DemandPoints = {}
        optData.ObjectWeights = {}
        for obj in objs:
            optData.DemandPoints[obj.Id] = obj.CenterPoint
            optData.ObjectWeights[obj.Id] = obj.Weight

        # Initialization bounds
        optData.Bounds = []

        logging.debug("Bounding box")

        for i in range(len(cranes)):
            craneDeltaX = cranes[i].baseSizeX / 2
            craneDeltaY = cranes[i].baseSizeY / 2

            elems = [obj for obj in objs if obj.Id in order[i]]

            bb = BoundingBox()
            bb.maxPoint.X = np.max([np.max([obj.CenterPoint.X, obj.StartPoint.X, obj.EndPoint.X]) for obj in elems]) + craneDeltaX
            bb.maxPoint.Y = np.max([np.max([obj.CenterPoint.Y, obj.StartPoint.Y, obj.EndPoint.Y]) for obj in elems]) + craneDeltaY
            bb.minPoint.X = np.min([np.min([obj.CenterPoint.X, obj.StartPoint.X, obj.EndPoint.X]) for obj in elems]) - craneDeltaX
            bb.minPoint.Y = np.min([np.min([obj.CenterPoint.Y, obj.StartPoint.Y, obj.EndPoint.Y]) for obj in elems]) - craneDeltaY

            bbSizes = (abs(bb.maxPoint.X - bb.minPoint.X), abs(bb.maxPoint.Y - bb.minPoint.Y))

            deltaX = cranes[i].maxLength - bbSizes[0]
            optData.Bounds.append((bb.minPoint.X - deltaX, bb.maxPoint.X + deltaX))
            deltaY = cranes[i].maxLength - bbSizes[1]
            optData.Bounds.append((bb.minPoint.Y - deltaY, bb.maxPoint.Y + deltaY))
    
    return optData

# this function check whether the group panels can be lifted by one crane.
# This function is a double check, but so far it is not essential
def CheckIfFeasible(clusters, cranes, modelPolygon):
    """ Check if model with sets of cranes has feasible solutions """
    result = {}
    for key, claster in clusters.items():
        circle = GeometryUtils.MakeCircle(claster)
        feasible = not all(circle[2] * 2 > crane.getMaxRadius() for crane in cranes)
        if feasible:
            from shapely.geometry import Point as ShPoint
            from shapely.geometry import MultiPolygon
            point = ShPoint(circle[0], circle[1])

            if not point.within(modelPolygon):
                pols = [modelPolygon]
                if isinstance(modelPolygon, MultiPolygon):
                    pols = modelPolygon.geoms

                coords = GeometryUtils.GetNearestPointOnAreaBound(point, pols)

                maxDistance = np.max([ShPoint(coords[0], coords[1]).distance(ShPoint(cl[0], cl[1])) for cl in claster])
                feasible = not all(maxDistance > crane.getMaxRadius() for crane in cranes)

        result[key] = feasible

    return result


def plotPolygonAndPoint(polys,points,fig_name='untitle.png',title_='',fig_index=10):
    from matplotlib import pyplot as plt

    color_array=['b','g','r','c','m','y','k','w']

    fig = plt.figure(fig_index, figsize=(7,5), dpi=90)
    index=0;
    for poly in polys:
        x,y=poly.exterior.xy
        plt.plot(x,y,color='#6699cc', alpha=0.7,linewidth=3, solid_capstyle='round', zorder=2)
        plt.fill(x, y, color=color_array[index], alpha=0.5)
        index=index+1
    
    offset=10 # offset for text
    
    if not isinstance(points[0],Point):
        pps=[]
        for i in range(len(points)//2):
            pps.append(Point(points[i*2],points[i*2+1],0))
    else:
        pps=points

    index=0;
    for point in pps:
        plt.scatter(point.X,point.Y,c=color_array[index])
        plt.text(point.X+offset,point.Y+offset,'crane stop '+str(index))
        index=index+1

    plt.xlabel('X (feet)')
    plt.ylabel('Y (feet)')
    plt.title(title_,fontsize=20, fontweight='bold')
    plt.savefig('pics/'+fig_name+'.png')
    plt.close(fig)


def plot_history(value, title_, figure_name, figure_number):
    from matplotlib import pyplot as plt
    fig = plt.figure(figure_number, figsize=(7,5), dpi=90)
    a=fig.add_subplot(111)
    y_range=max(value)+100
    a.axis([-1, 10, 0, y_range])
    plt.plot(value)
    plt.title(title_)
    
    plt.xlabel('Generation')
    plt.ylabel('Time (hour)')
    plt.savefig(figure_name,fontsize=30, fontweight='bold')

def CranePositionSensitivity(iterNum,structureData, craneData, visualize=False, hofUpdateCallback=None, surroundingPolygons=[], sitePolygons=[], \
    installationTime=10,Algorithm='GA',number_of_stop=[8],installMethod=0,numCrew=2,crane_type=1, worker_per_crew=4):
    """Genetic Algorithm running optimization of crane position"""
    
    import json
    logging.debug("Creating cranes")

    # Read crane data
    cranes = []
    rawCranes = craneData

    from EndpointUtils import EndpointUtils as eutils
    for c in craneData:
        if not isinstance(c, CraneData):
            cranes.append(eutils.GetCraneByType(c))
        else:
            cranes.append(c)

    logging.debug("Creating model data")
    #Read model data
    modelData = structureData
    if not isinstance(structureData, SiteData):
        modelData = SiteData(structureData, cranes, surroundingPolygons, sitePolygons)

    logging.debug("Getting opt data")

    optData = GetCraneGAOptimizationData(modelData, cranes, installationTime,number_of_stop,installMethod,numCrew)
    
    # for testification, a single evaluation
    # for two stops per wall
    """
    individuals=[[[-50,90,-50,30,30,-30,90,-30],[-50,80,-50,20,30,-30,90,-30],[-50,70,-50,10,30,-30,90,-30],[-50,80,-50,20,30,-30,90,-30]],
    [[-40,90,-40,30,30,-30,90,-30],[-40,80,-40,20,30,-30,90,-30],[-40,70,-40,10,30,-30,90,-30],[-40,60,-40,0,30,-30,90,-30]],
    [[-30,90,-30,30,30,-30,90,-30],[-30,80,-30,20,30,-30,90,-30],[-30,70,-30,10,30,-30,90,-30],[-30,60,-30,0,30,-30,90,-30]],
    [[-20,90,-20,30,30,-30,90,-30],[-20,80,-20,20,30,-30,90,-30],[-20,70,-20,10,30,-30,90,-30],[-20,60,-20,0,30,-30,90,-30]]]

    individuals=[[[-20,60,60,-30],[-20,55,60,-30],[-20,50,60,-30],[-20,45,60,-30],[-20,40,60,-30],[-20,35,60,-30],[-20,30,60,-30],[-20,25,60,-30]],\
        [[-25,60,60,-30],[-25,55,60,-30],[-25,50,60,-30],[-25,45,60,-30],[-25,40,60,-30],[-25,35,60,-30],[-25,30,60,-30],[-25,25,60,-30]],\
        [[-30,60,60,-30],[-30,55,60,-30],[-30,50,60,-30],[-30,45,60,-30],[-30,40,60,-30],[-30,35,60,-30],[-30,30,60,-30],[-30,25,60,-30]],\
        [[-35,60,60,-30],[-35,55,60,-30],[-35,50,60,-30],[-35,45,60,-30],[-35,40,60,-30],[-35,35,60,-30],[-35,30,60,-30],[-35,25,60,-30]],\
        [[-40,60,60,-30],[-40,55,60,-30],[-40,50,60,-30],[-40,45,60,-30],[-40,40,60,-30],[-40,35,60,-30],[-40,30,60,-30],[-40,25,60,-30]],\
        [[-45,60,60,-30],[-45,55,60,-30],[-45,50,60,-30],[-45,45,60,-30],[-45,40,60,-30],[-45,35,60,-30],[-45,30,60,-30],[-45,25,60,-30]],\
        [[-50,60,60,-30],[-50,55,60,-30],[-50,50,60,-30],[-50,45,60,-30],[-50,40,60,-30],[-50,35,60,-30],[-50,30,60,-30],[-50,25,60,-30]]]

    for indiv in individuals:
        for indi in indiv: 
            ans=evaluateMobileCraneOptPos(indi,optData)
            print (indi)
            print(ans)
    """

    # for one stop per wall
    n=20;
    range_X_1=45
    range_Y_1=40
    range_X_2=40
    range_Y_2=45

    start_X_1=-62
    start_Y_1=60
    start_X_2=60
    start_Y_2=-62

    individuals=[[[0,0,0,0] for i in range(0,n)] for i in range(0,n)];

    for i in range(0,n):
        for j in range(0,n):
            P1_X=start_X_1+range_X_1*(i/n)
            P1_Y=start_Y_1+range_Y_1*(j/n)
            P2_X=start_X_2+range_X_2*(j/n)
            P2_Y=start_Y_2+range_Y_2*(i/n)
            individuals[i][j][:]=[P1_X,P1_Y,P2_X,P2_Y];
    
    time=[];
    for indiv in individuals:
        for indi in indiv: 
            print (indi)
            ans,feasibility=evaluateMobileCraneOptPosSens(indi,optData)
            if feasibility:
                time.append(ans)
                print (indi)
                print(ans)

    return max(time)/min(time)
    
       




   
