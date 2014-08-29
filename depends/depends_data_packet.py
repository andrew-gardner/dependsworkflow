#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import os
import re
import uuid

import depends_node
import depends_util


"""
A data packet is the absolute minimum amount of information needed to represent
a knowable-thing on disk.  Each datapacket can represent a single item or a
sequence of items.

Only file information is transferred in a DataPacket, and only file information
should ever be transferred.  Other values that should be shared between nodes
should happen through the variable substitution mechanisms.
"""


###############################################################################
## Utility
###############################################################################
def filenameDictForDataPacketType(dataPacketType):
    """
    Return a dict of fileDescriptors for a given DataPacket type.
    """
    foo = dataPacketType(None, None)
    return foo.filenames


def scenegraphLocationString(dataPacket):
    """
    Given a datapacket, return a string representing its location in the 
    scenegraph. (::UUID:OUTPUT)
    """
    return "::"+str(dataPacket.sourceNode.uuid)+":"+dataPacket.sourceOutputName


def shorthandScenegraphLocationString(dataPacket):
    """
    Given a datapacket, return a "human-readable" string representing its name
    in the scenegraph.  (::NAME:OUTPUT)
    """
    return "::"+dataPacket.sourceNode.name+":"+dataPacket.sourceOutputName


def uuidFromScenegraphLocationString(string):
    """
    Returns a UUID object for a given scenegraph location string.
    """
    if string == "":
        return None
    if not string.startswith("::"):
        return None
    uuidString = string.split(":")[2]
    return uuid.UUID(uuidString)


def nodeAndOutputFromScenegraphLocationString(string, dag):
    """
    Returns a tuple containing the node defined in a location string and its 
    corresponding Output.
    """
    try:
        outputNodeUUID = uuidFromScenegraphLocationString(string)
        outputNode = dag.node(nUUID=outputNodeUUID)
        outputNodeOutputName = string.split(":")[3]
        return (outputNode, outputNode.outputNamed(outputNodeOutputName))
    except:
        return(None, None)
    

# TODO: A function to get the type name without needing to create the class?


###############################################################################
## DataPacket base class
###############################################################################
class DataPacket(object):
    """
    The minimal amount of data needed to convey an object.
    The user may inherit from this class to define her own formats of data to
    pass around the DAG.  Adding members to the filenames dictionary is all
    that is needed to make effective new DataPackets.
    """
    def __init__(self, sourceNode, sourceOutputName):
        self.filenames = dict()
        self.sourceNode = sourceNode
        self.sourceOutputName = sourceOutputName
        self.sequenceRange = None

        
    # TODO: Be more explicit in this function name
    def typeStr(self):
        """
        Returns a human-readable type string with CamelCaps->spaces.
        """
        # TODO: MAKE EXPLICIT!
        return re.sub(r'(?!^)([A-Z]+)', r' \1', type(self).__name__[len('DataPacket'):])


    def setFilename(self, descriptorName, filename):
        """
        Set the value of one of the files|sequences in this datapacket.
        """
        if descriptorName not in self.filenames:
            raise RuntimeError("DataPacket %s does not contain a file descriptor named %s." % (shorthandScenegraphLocationString(self), descriptorName))
        self.filenames[descriptorName] = filename


    def setSequenceRange(self, rangeTuple):
        """
        Set the range for this datapacket.  Takes a tuple containing start
        and end strings or ints.  All ranges are stored internally as ints.
        """
        # All sequence ranges are converted to integers here
        self.sequenceRange = None
        if rangeTuple:
            lowValue = int(rangeTuple[0]) if rangeTuple[0] else None
            highValue = int(rangeTuple[1]) if rangeTuple[1] else None
            self.sequenceRange = (lowValue, highValue)


    def fileDescriptorNamed(self, descriptorName):
        """
        Return a framespec object derived from the information in the given
        descriptor.
        """
        if descriptorName not in self.filenames:
            raise RuntimeError("DataPacket %s does not contain a file descriptor named %s." % (shorthandScenegraphLocationString(self), descriptorName))
        return depends_util.framespec(self.filenames[descriptorName], self.sequenceRange)
    

    def dataPresent(self, specificFileDescriptorName=None):
        """
        Returns if all data is present for the current DataPacket.  Individual
        file descriptors in the data packet can be specified to retrieve more 
        detailed information.
        """
        fdNameList = list()
        if specificFileDescriptorName:
            fdNameList.append(specificFileDescriptorName)
        else:
            fdNameList = self.filenames.keys()
        for fileDescriptor in fdNameList:
            if not self._filesExist(depends_util.framespec(self.filenames[fileDescriptor], self.sequenceRange)):
                return False
        return True

    
    def _filesExist(self, framespecObject):
        """
        Check if all files exist in a given framespec object.
        """
        numFilesInList = len(framespecObject.frames())
        if numFilesInList == 0:
            return False
        for file in framespecObject.frames():
            if not os.path.exists(file):
                return False
        return True


######## FUNCTION TO IMPORT PLUGIN DATA PACKETS INTO THIS NAMESPACE  ##########
def loadChildDataPacketsFromPaths(pathList):
    """
    Given a list of directories, import all classes that inherit from DataPacket
    in those directories into the data_packet namespace.
    """
    for path in pathList:
        dpClassDict = depends_util.allClassesOfInheritedTypeFromDir(path, DataPacket)
        for dpc in dpClassDict:
            globals()[dpc] = dpClassDict[dpc]
