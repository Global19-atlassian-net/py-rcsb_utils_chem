##
# File:    ChemCompMoleculeProvider.py
# Author:  J. Westbrook
# Date:    16-Feb-2020
#
# Updates:
#
##
"""
Utilities to read and process the dictionary of PDB chemical component definitions.
"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
import os
import time

from rcsb.utils.chem.PdbxChemComp import PdbxChemCompIt
from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.IoUtil import getObjSize
from rcsb.utils.io.MarshalUtil import MarshalUtil
from rcsb.utils.io.SingletonClass import SingletonClass

logger = logging.getLogger(__name__)


class ChemCompMoleculeProvider(SingletonClass):
    """Utilities to read and process the dictionary of PDB chemical component definitions.
    """

    def __init__(self, **kwargs):
        # Source target locators
        self.__ccUrlTarget = kwargs.get("ccUrlTarget", "http://ftp.wwpdb.org/pub/pdb/data/monomers/components.cif.gz")
        self.__birdUrlTarget = kwargs.get("birdUrlTarget", "http://ftp.wwpdb.org/pub/pdb/data/bird/prd/prdcc-all.cif.gz")
        self.__ccFileNamePrefix = kwargs.get("ccFileNamePrefix", "cc")
        self.__cachePath = kwargs.get("cachePath", ".")
        dirPath = os.path.join(self.__cachePath, "chem_comp")
        useCache = kwargs.get("useCache", True)
        self.__molLimit = kwargs.get("molLimit", 0)
        filterIdD = kwargs.get("filterIdD", None)
        #
        self.__mU = MarshalUtil(workPath=dirPath)
        self.__ccMolD = self.__reload(self.__ccUrlTarget, self.__birdUrlTarget, dirPath, useCache=useCache, molLimit=self.__molLimit, filterIdD=filterIdD)

    def testCache(self, minCount=29000, logSizes=False):
        if logSizes and self.__ccMolD:
            logger.info("ccMolD object size %.2f MB", getObjSize(self.__ccMolD) / 1000000.0)
        ok = self.__ccMolD and len(self.__ccMolD) >= minCount if minCount else self.__ccMolD is not None
        return ok

    def getMolD(self):
        return self.__ccMolD

    def getMol(self, ccId):
        try:
            return self.__ccMolD[ccId]
        except Exception as e:
            logger.debug("Get molecule %r failing with %s", ccId, str(e))
        return None

    def __reload(self, ccUrlTarget, birdUrlTarget, dirPath, useCache=False, molLimit=None, filterIdD=None):
        """Reload or create serialized data dictionary of chemical components.

        Args:
            ccUrlTarget (str): target url for chemical component dictionary resource file
            birdUrlTarget (str): target url for bird dictionary resource file (cc format)
            dirPath (str): path to the directory containing cache files
            useCache (bool):
            molLimit (int): maximum number of definitions to process
            filterIdD (dict): dictionary of selected chemical component identifier codes

         Returns:
            (list): chemical component data containers
        """
        #
        startTime = time.time()
        ccDataFilePath = os.path.join(dirPath, "%s-data.pic" % self.__ccFileNamePrefix)
        _, fExt = os.path.splitext(ccDataFilePath)
        ccDataFormat = "json" if fExt == "json" else "pickle"
        #
        if useCache and self.__mU.exists(ccDataFilePath):
            rdCcObjD = self.__mU.doImport(ccDataFilePath, fmt=ccDataFormat)
            ccObjD = {k: rdCcObjD[k] for k in sorted(rdCcObjD.keys())[:molLimit]} if molLimit else rdCcObjD
        else:
            # Source component data files ...
            ccdFilePath = self.__fetchUrl(ccUrlTarget, dirPath, useCache=useCache)
            birdFilePath = self.__fetchUrl(birdUrlTarget, dirPath, useCache=useCache)
            rdCcObjD = self.__readComponentDefinitions(ccdFilePath, birdFilePath, molLimit=molLimit)
            ccObjD = {ccId: ccObj for ccId, ccObj in rdCcObjD.items() if ccId in filterIdD} if filterIdD else rdCcObjD
            ok = self.__mU.doExport(ccDataFilePath, ccObjD, fmt=ccDataFormat)
            logger.info("Storing %s with data for %d definitions (status=%r) ", ccDataFilePath, len(ccObjD), ok)
        #
        endTime = time.time()
        logger.info("Loaded/reloaded %d definitions (%.4f seconds)", len(ccObjD), endTime - startTime)
        return ccObjD

    def __fetchUrl(self, urlTarget, dirPath, useCache=False):
        fU = FileUtil()
        fn = fU.getFileName(urlTarget)
        filePath = os.path.join(dirPath, fn)
        if not (useCache and fU.exists(filePath)):
            startTime = time.time()
            ok2 = fU.get(urlTarget, filePath)
            endTime = time.time()
            if ok2:
                logger.info("Fetched %s for resource file %s (status = %r) (%.4f seconds)", urlTarget, filePath, ok2, endTime - startTime)
            else:
                logger.error("Failing fetch for %s for resource file %s (status = %r) (%.4f seconds)", urlTarget, filePath, ok2, endTime - startTime)
        #
        return filePath

    def __readComponentDefinitions(self, ccdFilePath, birdFilePath=None, molLimit=None):
        ccObjD = {}
        try:
            startTime = time.time()
            logger.debug("Reading %s", ccdFilePath)
            rdCcObjL = self.__mU.doImport(ccdFilePath, fmt="mmcif")
            endTime = time.time()
            logger.info("Read %s with %d CCD definitions (%.4f seconds)", ccdFilePath, len(rdCcObjL), endTime - startTime)
            # -------
            if birdFilePath:
                startTime = time.time()
                logger.debug("Reading %s", birdFilePath)
                birdCcObjL = self.__mU.doImport(birdFilePath, fmt="mmcif")
                endTime = time.time()
                logger.info("Read %s with %d BIRD definitions (%.4f seconds)", birdFilePath, len(birdCcObjL), endTime - startTime)
                rdCcObjL.extend(birdCcObjL)
            #
            startTime = time.time()
            ccObjL = rdCcObjL[:molLimit] if molLimit else rdCcObjL
            for ccObj in ccObjL:
                ccIt = iter(PdbxChemCompIt(ccObj))
                ccIt = next(ccIt, None)
                ccId = ccIt.getId() if ccIt else ccObj.getName()
                ccObjD[ccId] = ccObj
            endTime = time.time()
            logger.info("Processed %d definitions (%.4f seconds)", len(ccObjD), endTime - startTime)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        #
        return ccObjD