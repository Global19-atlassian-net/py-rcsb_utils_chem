##
#
# File:    OeDepictTests.py
# Author:  jdw
# Date:    5-May-2013
# Version: 0.001
#
# Updates:
#  4-May-2014 jdw add example for depiction from SMILES input
#  6-Jun-2016 jdw general cleanup
##
"""
A collection of tests for the OEDepict and related classes.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import logging
import os
import os.path
import time
import unittest

from rcsb.utils.chem.OeDepict import OeDepict
from rcsb.utils.chem.OeDepict import OeDepictMultiPage
from rcsb.utils.chem.OeIoUtils import OeIoUtils
from rcsb.utils.chem.OeMoleculeProvider import OeMoleculeProvider

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()


class OeDepictTests(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        self.__workPath = os.path.join(HERE, "test-output")
        self.__dataPath = os.path.join(HERE, "test-data")
        self.__cachePath = os.path.join(HERE, "test-output")
        self.__ccUrlTarget = os.path.join(self.__dataPath, "components-abbrev.cif")
        self.__birdUrlTarget = os.path.join(self.__dataPath, "prdcc-abbrev.cif")
        #
        self.__ccIdList = ["000", "001", "002", "003", "004", "0K3", "LHI", "NTP", "X12", "GLC", "MAN"]
        self.__ccIdListLong = self.__ccIdList
        self.__oeMolD = self.__getCache(molBuildType="model-xyz", useCache=True)

    def tearDown(self):
        pass

    def __getCache(self, molBuildType="model-xyz", useCache=True):
        oemp = OeMoleculeProvider(
            ccUrlTarget=self.__ccUrlTarget,
            birdUrlTarget=self.__birdUrlTarget,
            ccFileNamePrefix="cc-abbrev",
            cachePath=self.__cachePath,
            molBuildType=molBuildType,
            useCache=useCache,
        )
        ok = oemp.testCache()
        self.assertTrue(ok)
        return oemp.getOeMolD()

    def __getMolDepictList(self, ccIdList):
        dL = []
        for ccId in ccIdList:
            ccId = ccId.upper()
            if ccId in self.__oeMolD:
                dL.append((ccId, self.__oeMolD[ccId], "Title: " + ccId))
            else:
                logger.info("Missing molecule %r", ccId)
        return dL

    def testDepictCCIdList(self):
        """Test case -  single OE molecule depiction.
        labelAtomName=True, labelAtomCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, abelBondCIPStereo=True, cellBorders=False, bondDisplayWidth=3.0
        """
        try:
            oeMolTitleList = self.__getMolDepictList(self.__ccIdList)
            for ccId, mol, title in oeMolTitleList:
                imagePath = os.path.join(self.__workPath, ccId + ".svg")
                oed = OeDepict()
                title = ""
                oed.setMolTitleList([(ccId, mol, title)])
                oed.setDisplayOptions(
                    labelAtomName=False, labelAtomCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, labelBondCIPStereo=True, cellBorders=False, bondDisplayWidth=8.0
                )
                oed.setGridOptions(rows=1, cols=1, cellBorders=False)
                oed.prepare()
                oed.write(imagePath)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testDepictCCIdListLabeled(self):
        """Test case -  single OE molecule depiction."""
        try:
            oeMolTitleList = self.__getMolDepictList(self.__ccIdList)
            for ccId, mol, title in oeMolTitleList:
                imagePath = os.path.join(self.__workPath, ccId + "-labeled.svg")
                oed = OeDepict()
                title = ""
                oed.setMolTitleList([(ccId, mol, title)])
                bondDisplayWidth = 10.0
                numAtoms = mol.NumAtoms()
                if numAtoms > 100 and numAtoms <= 200:
                    bondDisplayWidth = 6.0
                elif mol.NumAtoms() > 200:
                    bondDisplayWidth = 4.0

                oed.setDisplayOptions(
                    labelAtomName=True,
                    labelAtomCIPStereo=True,
                    labelAtomIndex=False,
                    labelBondIndex=False,
                    labelBondCIPStereo=True,
                    cellBorders=False,
                    bondDisplayWidth=bondDisplayWidth,
                )
                oed.setGridOptions(rows=1, cols=1, cellBorders=False)
                oed.prepare()
                oed.write(imagePath)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testDepictGrid(self):
        """Test case - depict molecule list  grid."""
        try:
            oeMolTitleList = self.__getMolDepictList(self.__ccIdList)
            oed = OeDepict()
            oed.setMolTitleList(oeMolTitleList)
            oed.setDisplayOptions(
                imageX=1000, imageY=1000, labelAtomName=True, labelAtomCIPStereo=True, labelBondCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, bondDisplayWidth=0.5
            )
            oed.setGridOptions(rows=2, cols=2)
            oed.prepare()
            oed.write(os.path.join(self.__workPath, "myIdListtest.png"))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testDepictMultiSmall(self):
        """Test case -  get, read, build OE molecule, and depict the molecule."""
        try:
            oeMolTitleList = self.__getMolDepictList(self.__ccIdList)
            oed = OeDepictMultiPage()
            oed.setMolTitleList(oeMolTitleList)
            oed.prepare()
            oed.write(os.path.join(self.__workPath, "mulitIdListtest.pdf"))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testDepictMultiLarge(self):
        """Test case -  get, read, build OE molecule, and depict the molecule."""
        try:
            oeMolTitleList = self.__getMolDepictList(self.__ccIdListLong)
            oed = OeDepictMultiPage()
            oed.setMolTitleList(oeMolTitleList)
            oed.setDisplayOptions(
                pageOrientation="Portrait", labelAtomName=True, labelAtomCIPStereo=True, labelBondCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, bondDisplayWidth=0.5
            )
            oed.setGridOptions(rows=2, cols=1)
            oed.prepare()
            oed.write(os.path.join(self.__workPath, "multiPathListtest.pdf"))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testDepictOneSDF(self):
        """Test case -  get, read, build OE molecule from SDF file, and depict the molecule."""
        try:
            imagePath = os.path.join(self.__workPath, "benzene-from-smi.svg")
            sdfPath = os.path.join(self.__dataPath, "ATP.sdf")
            oeio = OeIoUtils()
            oeMolL = oeio.fileToMols(sdfPath)
            #
            oed = OeDepict()
            oed.setMolTitleList([("ATP", oeMolL[0], "Title for ATP")])
            oed.setDisplayOptions(labelAtomName=True, labelAtomCIPStereo=True, labelBondCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, bondDisplayWidth=0.5)
            oed.setGridOptions(rows=1, cols=1)
            oed.prepare()
            oed.write(imagePath)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testDepictSMILES(self):
        """Test case -  create depiction from SMILES descriptor."""
        try:
            imagePath = os.path.join(self.__workPath, "benzene-from-smi.svg")
            oeio = OeIoUtils()
            oeMol = oeio.smilesToMol("c1ccccc1")

            oed = OeDepict()
            oed.setMolTitleList([("benzene", oeMol, "Title for benzene")])
            oed.setDisplayOptions(labelAtomName=False, labelAtomCIPStereo=True, labelBondCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, bondDisplayWidth=1.0)
            oed.setGridOptions(rows=1, cols=1)
            oed.prepare()
            oed.write(imagePath)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteDepict():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(OeDepictTests("testDepictCCIdList"))
    suiteSelect.addTest(OeDepictTests("testDepictGrid"))
    suiteSelect.addTest(OeDepictTests("testDepictMultiSmall"))
    suiteSelect.addTest(OeDepictTests("testDepictMultiLarge"))
    suiteSelect.addTest(OeDepictTests("testDepictOneSDF"))
    suiteSelect.addTest(OeDepictTests("testDepictSMILES"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = suiteDepict()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
