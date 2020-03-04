##
# File:    ChemCompSearchIndexProviderTests.py
# Author:  J. Westbrook
# Date:    3-Mar-2020
# Version: 0.001
#
# Update:
#
#
##
"""
Tests for utilities to read and process the dictionary of PDB chemical component definitions.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import resource
import time
import unittest


from rcsb.utils.chem import __version__
from rcsb.utils.chem.ChemCompSearchIndexProvider import ChemCompSearchIndexProvider

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()


class ChemCompSearchIndexProviderTests(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        self.__dataPath = os.path.join(HERE, "test-data")
        self.__cachePath = os.path.join(HERE, "test-output")
        #
        logger.debug("Running tests on version %s", __version__)
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        rusageMax = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("Maximum resident memory size %.4f MB", rusageMax / 10 ** 6)
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testChemCompSearchIndexCacheFilesAbbrev(self):
        """ Test construction of full chemical component resource files.
        """
        self.__testBuildSearchIndexCacheFiles(logSizes=True, useCache=False, ccFileNamePrefix="cc-abbrev")

    def testChemCompSearchIndexCacheFilesFull(self):
        """ Test construction of full chemical component resource files.
        """
        self.__testBuildSearchIndexCacheFiles(logSizes=True, useCache=False, ccFileNamePrefix="cc-full")

    def testChemCompSearchIndexCacheFilesFiltered(self):
        """ Test construction of a filtered subset of chemical component definitions.
        """
        self.__testBuildSearchIndexCacheFiles(logSizes=True, useCache=False, ccFileNamePrefix="cc-filtered")

    def __testBuildSearchIndexCacheFiles(self, **kwargs):
        """ Test build chemical component cache files from the input component dictionaries
        """
        molLimit = kwargs.get("molLimit", None)
        useCache = kwargs.get("useCache", True)
        logSizes = kwargs.get("logSizes", False)
        ccFileNamePrefix = kwargs.get("ccFileNamePrefix", "cc")
        ccsiP = ChemCompSearchIndexProvider(cachePath=self.__cachePath, useCache=useCache, molLimit=molLimit, ccFileNamePrefix=ccFileNamePrefix)
        ok = ccsiP.testCache(minCount=molLimit, logSizes=logSizes)
        self.assertTrue(ok)
        logger.info(" ******* Completed operation ******** ")
        #


def buildCacheFiles():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ChemCompSearchIndexProviderTests("testChemCompSearchIndexCacheFilesFull"))
    suiteSelect.addTest(ChemCompSearchIndexProviderTests("testChemCompSearchIndexCacheFilesFiltered"))
    suiteSelect.addTest(ChemCompSearchIndexProviderTests("testChemCompSearchIndexCacheFilesAbbrev"))
    return suiteSelect


if __name__ == "__main__":

    mySuite = buildCacheFiles()
    unittest.TextTestRunner(verbosity=2).run(mySuite)