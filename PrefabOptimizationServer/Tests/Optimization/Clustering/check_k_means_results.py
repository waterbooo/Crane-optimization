import unittest
import numpy as np

from Optimization.Clustering.KMeansBasedBarsDivision import KMeansBasedBarsDivision as kmeans

class check_k_means_results(unittest.TestCase):

     def test_k_means_results_no_error(self):
         """ Check if clusters count correct when center point are the same """
         clusterer = kmeans()
         
         centers = [np.array([10, 10]), np.array([10, 10]), np.array([20, 10]), np.array([10, 20])]
         mu = [centers[0], centers[1]]
         
         clusters, clusterIndices = clusterer.ClusterPoints(centers, mu)
         
         self.assertTrue(len(clusters) == 2)
         self.assertTrue(len(clusterIndices) == 2)


if __name__ == '__main__':
    unittest.main()