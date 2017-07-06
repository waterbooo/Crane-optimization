import numpy as np
import random
from BLGeometry import GeometryUtils

 
class KMeansBasedBarsDivision(object):
    """Modified K-means algotithm for division of bars between N cranes"""
    def __init__(self, *args, **kwargs):
        self._prohibitedRegion = None
        self._acceptableRegion = None
        self._cranes = []
        self._radiuses = []
        return super().__init__(*args, **kwargs)

    @property
    def ProhibitedRegion(self):
        """Region where it is prohibited to point centers"""
        return self._prohibitedRegion

    @ProhibitedRegion.setter
    def ProhibitedRegion(self, value):
        self._prohibitedRegion = value

    @property
    def AcceptableRegion(self):
        """Region where it is allowed to point centers"""
        return self._acceptableRegion

    @AcceptableRegion.setter
    def AcceptableRegion(self, value):
        self._acceptableRegion = value

    @property
    def Radiuses(self):
        """Maximum allowed distances from corresponding cluster center (e.g. crane max lenghts)"""
        return self._radiuses

    @Radiuses.setter
    def Radiuses(self, value):
        self._radiuses = value

    def ClusterPoints(self, X, mu):
        """Divide points between clusters"""
        clusters  = {}
        clusterIndices = {}
        for x in enumerate(X):
            bestMuKey = min([(i[0], np.linalg.norm(x[1]-mu[i[0]])) \
                        for i in enumerate(mu)], key=lambda t:t[1])[0]
            try:
                clusters[bestMuKey].append(x[1])
                clusterIndices[bestMuKey].append(x[0])
            except KeyError:
                clusters[bestMuKey] = [x[1]]
                clusterIndices[bestMuKey] = [x[0]]

        # Add an array in case if cluster is empty
        if len(mu) > len(clusters):
            for x in range(len(mu)):
                if x not in clusters:
                    clusters[x] = []
                    clusterIndices[x] = []

        return clusters, clusterIndices

    def ClusterPointsByRadius(self, X, mu):
        """Divide points between clusters"""
        clusters  = {}
        clusterIndices = {}
        for x in enumerate(X):
            bestMuKey = min([(i[0], np.linalg.norm(x[1]-mu[i[0]])) \
                        for i in enumerate(mu)], key=lambda t:t[1]/self.Radiuses[t[0]])[0]
            try:
                clusters[bestMuKey].append(x[1])
                clusterIndices[bestMuKey].append(x[0])
            except KeyError:
                clusters[bestMuKey] = [x[1]]
                clusterIndices[bestMuKey] = [x[0]]

        # Add an array in case if cluster is empty
        if len(mu) > len(clusters):
            for x in range(len(mu)):
                if x not in clusters:
                    clusters[x] = []
                    clusterIndices[x] = []

        return clusters, clusterIndices
 
    def ReevaluateCenters(self, mu, clusters):
        """Calculate new cluster centers"""
        newMu = []
        keys = sorted(clusters.keys())
        for k in keys:
            mean = np.mean(clusters[k], axis = 0)
            # If there is no elements in claster, use old center.
            if mean.size == 1 and np.isnan(mean):
                mean = mu[k]
            newMu.append(mean)
        return newMu

    def ProjectCentersToAcceptableRegion(self, clusters, mu):
        """Project cluster centers either to the border of prohibited region or to the border of acceptable one"""
        if not self._prohibitedRegion and not self._acceptableRegion:
            # If no border regions defined just return centers
            return mu
        else:
            from shapely.geometry import Point as ShPoint
            from shapely.geometry import MultiPolygon
            region = None
            newMu = []
            if self._prohibitedRegion and not self._acceptableRegion:
                # If there is prohibited region and no acceptable region defined 
                # project points on prohibited region border nearest point
                region = self._prohibitedRegion

                # Iterate through cluster centers
                for p in mu:
                    shp = ShPoint(p[0], p[1])
                    # Check whether p in region polygon
                    if shp.within(region):
                        pols = [region]
                        if isinstance(region, MultiPolygon):
                            pols = region.geoms
                    
                        # Get projection point
                        coords = GeometryUtils.GetNearestPointOnAreaBound(shp, pols)
                        pp = ShPoint(coords)
                    else:
                        pp = shp

                    # Pass new center coords into outputing mu
                    newMu.append(np.array([pp.x, pp.y]))
                return newMu
                    
            if self._acceptableRegion:
                # Project on border of acceptable region if any
                # If there is prohibited region and no acceptable region defined 
                # project points on prohibited region border nearest point
                region = self._acceptableRegion

                # Iterate through cluster centers
                for p in mu:
                    shp = ShPoint(p[0], p[1])
                    # Check whether p in region polygon
                    if not shp.within(region):
                        pols = [region]
                        if isinstance(region, MultiPolygon):
                            pols = region.geoms
                    
                        # Get projection point
                        coords = GeometryUtils.GetNearestPointOnAreaBound(shp, pols)
                        pp = ShPoint(coords)
                    else:
                        pp = shp

                    # Pass new center coords into outputing mu
                    newMu.append(np.array([pp.x, pp.y]))
                return newMu
            return mu
 
    def HasConverged(self, mu, oldMu):
        """Checks whether cluster centers are stable for two iterations"""
        return (set([tuple(a) for a in mu]) == set([tuple(a) for a in oldMu]))

    def FindCenters(self, x, k):
        """Clustering process
           x: samples
           k: number of clusters
        """
        kmeans = KMeansBasedBarsDivision
        # Initialize to K random centers
        oldMu = random.sample(x, k)
        mu = random.sample(x, k)
        # Assign all points in X to clusters
        clusters, clusterIndices = self.ClusterPoints(x, mu)
        while not self.HasConverged(mu, oldMu):
            oldMu = mu
            # Reevaluate centers
            mu = self.ReevaluateCenters(oldMu, clusters)
            # Project centers to outside the model
            mu = self.ProjectCentersToAcceptableRegion(clusters, mu)
            if len(self._radiuses) != 0:
                # re-assign all points in X to clusters taking in order crane properties
                clusters, clusterIndices = self.ClusterPointsByRadius(x, mu)
            else:
                # Assign all points in X to clusters
                clusters, clusterIndices = self.ClusterPoints(x, mu)
        return(mu, clusters, clusterIndices)

