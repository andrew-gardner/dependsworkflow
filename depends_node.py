#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import re
import copy
import uuid

import depends_util
import depends_variables
import depends_data_packet


"""
A class defining a node in a workflow's dependency graph.  Each node contains
properties (inputs, outputs, and attributes), and the classes representing 
each are also defined here.  Related utility functions are also present, as 
well as functionality to automatically create read nodes for each registered
data type.  Finally, a collection of "built in" nodes are defined.

Defining one's own nodes consists of inheriting from the DagNode class and
overloading a series of functions that define the node's properties.  Each
inherited node should be as atomic as possible, performing one operation well.
"""


###############################################################################
## Utility
###############################################################################
def dagNodeTypes():
    """
    Return a list of node types presently loaded.
    """
    return DagNode.__subclasses__()


def cleanNodeName(name):
    """
    Return a cleaned version of a string, suitable for naming a node.
    Basically removes anything but alphanumeric characters and dots.
    """
    return re.sub(r'[^a-zA-Z0-9\n\.]', '_', name)   


###############################################################################
## Input/Output/Attribute classes
###############################################################################
# NOTE : If these get many more attributes, they may very well need to get their
#        own dicts of values, ranges, etc.
# NOTE : Sequence ranges are tuples containing two strings, the start and the end.
#

class DagNodeInput(object):
    """
    An input property of a DagNode.  Contains the datapacket type is accepts,
    a flag denoting if it's required or not, a name, and documentation.
    """

    def __init__(self, name, dataPacketType, required, docString=None):
        """
        """
        self.name = name
        self.value = ""
        self.seqRange = None
        self.docString = docString
        
        # Constants, not written to disk
        self.dataPacketType = dataPacketType
        self.required = required
    
    
    def allPossibleInputTypes(self):
        """
        Return a list of all possible DataPacket types this input accepts.
        This is interesting because inputs can accept DataPakcets of a type
        that is inherited from its base type.
        """
        inputTypeList = set([self.dataPacketType])
        inputTypeList |= set(depends_util.allClassChildren(self.dataPacketType))
        return inputTypeList
        

    # TODO: Should my dictionary keys be more interesting?
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return (self.name) == (other.name)


###############################################################################
###############################################################################
class DagNodeOutput(object):
    """
    An output property of a DagNode.  Contains its data packet type, a doc
    string, a name, and potentially a string containing a custom file dialog
    that pops open when a button is pressed.  Each sub-output in a given output
    must contain the exact number of files as the rest of the sub-outputs, thus
    a single sequence range is present for an entire output.
    """
    
    def __init__(self, name, dataPacketType, docString=None, customFileDialogName=None):
        """
        """
        self.name = name
        self.value = dict()
        self.seqRange = None
        self.docString = docString
        self.customFileDialogName = customFileDialogName

        # Constants, not written to disk
        self.dataPacketType = dataPacketType

        # Note: We add the largest possible set of attributes this node can have from 
        #       its datapacket and all the datapacket's children types
        allPossibleFileDescriptorNames = set()
        for tipe in self.allPossibleOutputTypes():
            for fdName in depends_data_packet.filenameDictForDataPacketType(tipe):
                allPossibleFileDescriptorNames.add(fdName)
        for fdName in allPossibleFileDescriptorNames:
            self.value[fdName] = ""
            self.seqRange = None


    def allPossibleOutputTypes(self):
        """
        Returns a list of all type data packet types this node can output.
        """
        outputTypeList = set([self.dataPacketType])
        outputTypeList |= set(depends_util.allClassChildren(self.dataPacketType))
        return outputTypeList


    def subOutputNames(self):
        """
        Return a list of the names of each of this output's data packet sub-types.
        """
        subList = list()
        for subName in self.value:
            subList.append(subName)
        return subList


    def getSeqRange(self):
        """
        Gets the single sequence range for this output.
        """
        if not self.seqRange:
            return None
        if self.seqRange[0] is None or self.seqRange[1] is None:
            return None
        if self.seqRange[0] == "" or self.seqRange[1] == "":
            return None
        return self.seqRange
        

    # TODO: Should my dictionary keys be more interesting?
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return (self.name) == (other.name)


###############################################################################
###############################################################################
class DagNodeAttribute(object):
    """
    An attribute property of a DagNode.  These contain a name, default value,
    a doc string, a potential custom file dialog specifier, and a flag stating
    if it's a file type or not.  The data is stored as a string, so whatever
    the user needs can be placed in here.
    """
    
    def __init__(self, name, defaultValue, isFileType=False, docString=None, customFileDialogName=None):
        """
        """
        self.name = name
        self.value = defaultValue
        self.seqRange = None
        self.docString = docString
        self.customFileDialogName = customFileDialogName

        # Constants, not written to disk
        self.isFileType = isFileType


    # TODO: Should my dictionary keys be more interesting?
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return (self.name) == (other.name)


###############################################################################
## Base class
###############################################################################
class DagNode(object):
    """
    The base class from which all dependency graph nodes are created.  This
    class contains a custom dictionary to store its properties (inputs, 
    outputs, and attributes), a UUID insuring nodes do not get confused with
    eachother, and a name.  A series of property accessors exists, as well as 
    some general functionality.  When creating a new node, please refer to
    the section labeled "Children must inherit these" and "Children may 
    inherit these" as overloading these functions are how nodes distinguish
    themselves.
    """

    def __init__(self, name="", nUUID=None):
        """
        """
        self.setName(name)
        self._properties = dict()
        self.uuid = nUUID if nUUID else uuid.uuid4()
        
        # Give the inputs, outputs, and attributes a place to live in the storage dict
        for input in self._defineInputs():
            self._properties[self._inputNameInPropertyDict(input.name)] = input
        for output in self._defineOutputs():
            self._properties[self._outputNameInPropertyDict(output.name)] = output
        for attribute in self._defineAttributes():
            self._properties[attribute.name] = attribute
            

    def __str__(self):
        """
        For printing.
        """
        return "DagNode - name:%s  type:%s  uuid:%s" % (self.name, type(self).__name__, str(self.uuid))


    def __lt__(self, other):
        """
        For sorting.
        """
        return self.name < other.name
    

    def __eq__(self, other):
        """
        The UUIDs are the basis for equivalence.
        """
        if isinstance(other, DagNode):
            return self.uuid == other.uuid
        return NotImplemented
    

    def __ne__(self, other):
        """
        Mirror of __eq__
        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


    def __hash__(self):
        """
        For adding to dictionaries.
        """
        return hash(self.uuid)


    def _inputNameInPropertyDict(self, inputName):
        """
        The property dict stores inputs with an interesting key.  Compute it.
        """
        INPUT_ATTR_PREFIX = "INPUT"
        return INPUT_ATTR_PREFIX+"@"+inputName


    def _outputNameInPropertyDict(self, outputName):
        """
        The property dict stores outputs with an interesting key.  Compute it.
        """
        OUTPUT_ATTR_PREFIX = "OUTPUT"
        return OUTPUT_ATTR_PREFIX+"@"+outputName


    ###########################################################################
    ## Input functions
    ###########################################################################
    def inputs(self):
        """
        Return a list of all input objects.
        """
        inputList = list()
        for x in self._properties:
            if type(self._properties[x]) is DagNodeInput:
                inputList.append(self._properties[x])
        return inputList


    def setInputValue(self, inputName, value):
        """
        Set an input named the given name to the given string.
        """
        self.inputNamed(inputName).value = value


    def setInputRange(self, inputName, newRange):
        """
        Set the range of an input named the given name to the given range 
        tuple (string, string).
        """
        self.inputNamed(inputName).seqRange = newRange


    def inputNamed(self, inputName):
        """
        Return an input object for the given name.
        """
        fullInputName = self._inputNameInPropertyDict(inputName)
        if fullInputName not in self._properties:
            raise RuntimeError('Input %s does not exist in node %s.' % (inputName, self.name))
        return self._properties[fullInputName]
    

    def inputValue(self, inputName, variableSubstitution=True):
        """
        Return a value string for the given input name.  Workflow variables are
        substituted by default.
        """
        value = self.inputNamed(inputName).value
        if variableSubstitution:
            value = depends_variables.substitute(value)
        return value
        
    
    def inputRange(self, inputName, variableSubstitution=True):
        """
        Return a range tuple (string, string) for the given input name.  Workflow
        variables are substituted by default.
        """
        seqRange = self.inputNamed(inputName).seqRange
        if seqRange and seqRange[0] and seqRange[1] and variableSubstitution:
            seqRange = (depends_variables.substitute(seqRange[0]), depends_variables.substitute(seqRange[1]))
        return seqRange

    
    ###########################################################################
    ## Output functions
    ###########################################################################
    def outputs(self):
        """
        Return a list of all output objects.
        """
        outputList = list()
        for x in self._properties:
            if type(self._properties[x]) is DagNodeOutput:
                outputList.append(self._properties[x])
        return outputList


    def setOutputValue(self, outputName, subOutputName, value):
        """
        Set an output named the given name to the given string.
        """
        self.outputNamed(outputName).value[subOutputName] = value


    def setOutputRange(self, outputName, newRange):
        """
        Set the range of an output named the given name to the given range 
        tuple (string, string).
        """
        self.outputNamed(outputName).seqRange = newRange


    def outputNamed(self, outputName):
        """
        Return an output object for the given name.
        """
        fullOutputName = self._outputNameInPropertyDict(outputName)
        if fullOutputName not in self._properties:
            raise RuntimeError('Output %s does not exist in node %s.' % (outputName, self.name))
        return self._properties[fullOutputName]
    
    
    def outputValue(self, outputName, subOutputName, variableSubstitution=True):
        """
        Return a value string for the given output name and sub-name.  Workflow
        variables are substituted by default.
        """
        value = self.outputNamed(outputName).value[subOutputName]
        if variableSubstitution:
            value = depends_variables.substitute(value)
        return value


    def outputRange(self, outputName, variableSubstitution=True):
        """
        Return a range tuple (string, string) for the given output name.  
        Workflow variables are substituted by default.
        """
        seqRange = self.outputNamed(outputName).seqRange
        if seqRange and seqRange[0] and seqRange[1] and variableSubstitution:
            seqRange = (depends_variables.substitute(seqRange[0]), depends_variables.substitute(seqRange[1]))
        return seqRange


    def outputFramespec(self, outputName, subOutputName):
        """
        Return a framespec object for the given output name and sub-name.
        Workflow variables are always substituted in this function.
        """
        filename = self.outputValue(outputName, subOutputName)
        seqRange = self.outputRange(outputName)
        return depends_util.framespec(filename, seqRange)
    

    ###########################################################################
    ## Attribute functions
    ###########################################################################
    def attributes(self):
        """
        Return a list of all attribute objects.
        """
        attributeList = list()
        for x in self._properties:
            if type(self._properties[x]) is DagNodeAttribute:
                attributeList.append(self._properties[x])
        return attributeList


    def setAttributeValue(self, attrName, value):
        """
        Set an attribute named the given name to the given string.
        """
        self.attributeNamed(attrName).value = value


    def setAttributeRange(self, attrName, newRange):
        """
        Set the range of an attribute named the given name to the given range
        tuple (string, string).
        """
        self.attributeNamed(attrName).seqRange = newRange


    def attributeNamed(self, attrName):
        """
        Return an attribute object for the given name.
        """
        if attrName not in self._properties:
            raise RuntimeError('Attribute %s does not exist in node %s.' % (attrName, self.name))
        return self._properties[attrName]


    def attributeValue(self, attrName, variableSubstitution=True):
        """
        Return a value string for the given attribute name.  Workflow variables
        are substituted by default.
        """
        value = self.attributeNamed(attrName).value
        if variableSubstitution:
            value = depends_variables.substitute(value)
        return value


    def attributeRange(self, attrName, variableSubstitution=True):
        """
        Return a range tuple (string, string) for the given attribute name.  
        Workflow variables are substituted by default.
        """
        seqRange = self.attributeNamed(attrName).seqRange
        if variableSubstitution:
            seqRange = (depends_variables.substitute(seqRange[0]), depends_variables.substitute(seqRange[1]))
        return seqRange


    #def attributeFramespec(self, attrName):
    #   """
    #   """


    ###########################################################################
    ## General
    ###########################################################################
    def typeStr(self):
        """
        Returns a human readable type string with CamelCaps->spaces.
        """
        # TODO: MAKE EXPLICIT!
        return re.sub(r'(?!^)([A-Z]+)', r' \1', type(self).__name__[len('DagNode'):])
    
    
    def setName(self, name):
        """
        Set the name value, converting all special characters (and spaces) into
        underscores.
        """
        processedName = cleanNodeName(name)
        self.name = processedName


    def duplicate(self, nameExtension):
        """
        Return a duplicate of this node, but insure the parameters that need to be
        different to co-exist in a DAG are different (name, uuid, etc)
        """
        dupe = type(self)(name=self.name+nameExtension)
        for attribute in self.attributes():
            dupe._properties[attribute.name] = copy.deepcopy(attribute)
        for output in self.outputs():
            fullOutputName = self._outputNameInPropertyDict(output.name)
            dupe._properties[fullOutputName] = copy.deepcopy(output)
        return dupe
        

    def dataPacketTypesAccepted(self):
        """
        Return a list of DataPacket types this node can find useful as inputs.
        Includes all input types and their child types.
        """
        acceptedTypes = set()
        for input in self.inputs():
            acceptedTypes.update(input.allPossibleInputTypes())
        return list(acceptedTypes)
    

    def inputRequirementsFulfilled(self, dataPackets):
        """
        Determine if all the data necessary to run is present.
        """
        dpInputs = [x[0] for x in dataPackets]
        return set(self.inputs()).issubset(set(dpInputs))


    def sceneGraphHandle(self, specializationDict=None):
        """
        Handle this node in the context of the dependency engine scene graph.
        If the output is specialized to an inherited type, pass a dictionary
        in containing the specializations.  Currently multiple outputs exist
        for each node, so return a list of all data packets generated by this
        node.
        """
        # TODO: This loops over all outputs and works now because only a single
        #       output exists (see usages in dag.py).  This may be inadvisable.
        
        # (specialization is a dict keying off outputName, containing outputType)
        dpList = list()
        for output in self.outputs():
            outputType = output.dataPacketType
            # If a specializationDict has been supplied, use the given type
            if specializationDict and output.name in specializationDict:
                outputType = specializationDict[output.name]
            # Create the new datapacket and populate its attributes.
            newDataPacket = outputType(self, output.name)
            for fdName in newDataPacket.filenames:
                newDataPacket.setFilename(fdName, self.outputValue(output.name, fdName))
                # TODO: This happens multiple times right now.  Once the UI is fixed, it won't
                newDataPacket.setSequenceRange(self.outputRange(output.name, fdName))
            dpList.append(newDataPacket)
        return dpList


    def inputAffectingOutput(self, output):
        """
        Returns the one input that affects the given output.
        """
        # TODO: Is this really a singular thing?
        # TODO: Guessing is a bit too implicit for my tastes!
        for input in self.inputs():
            if input.dataPacketType == output.dataPacketType:
                return input
        return None
        
        
    def outputAffectedByInput(self, input):
        """
        Returns the output that is affected by the given input.
        """
        # TODO: Is this really a singular thing?
        # TODO: Guessing is a bit too implicit for my tastes!
        for output in self.outputs():
            if output.dataPacketType == input.dataPacketType:
                return output
        return None
        

    ###########################################################################
    ## Children must inherit these
    ###########################################################################
    def _defineInputs(self):
        """
        Defines the list of input objects for the node.
        """
        print "Empty Define Inputs function called in parent 'DagNode' class."
        return list()
    
    
    def _defineOutputs(self):
        """
        Defines the list of output objects for the node.
        """
        print "Empty Define Outputs function called in parent 'DagNode' class."
        return list()
    
    
    def _defineAttributes(self):
        """
        Defines the list of attribute objects for the node.
        """
        print "Empty Define Attributes function called in parent 'DagNode' class."
        return list()
    
    
    def executeList(self, dataPacketDict, splitOperations=False):
        """
        Given a dict of input dataPackets, return a list of commandline arguments
        that are easily digested by an execution recipe.
        The splitOperations parameter is passed to nodes that are embarrassingly parallel.
        Nodes that execute with their operations split should return a list of
        lists of commandline arguments that basically run entire frame sequences
        as separate commands.
        """
        print "Empty Execute function in parent 'DagNode' class."
        return list()


    ###########################################################################
    ## Children may inherit these
    ###########################################################################
    def preProcess(self, dataPacketDict):
        """
        This runs *before* the executeList function is executed.
        Given a dict of input dataPackets (often times not used), create a list
        of commandline arguments that can be run by the subprocess module.
        """
        return list()


    def postProcess(self, dataPacketDict):
        """
        This runs *after* the executeList function is executed.
        Given a dict of input dataPackets (often times not used), create a list
        of commandline arguments that can be run by the subprocess module.
        """
        return list()


    def validate(self):
        """
        Each node is capable of setting their own validation routines that can
        do whatever the user wants, from verifying input parameters fall within
        a range to insuring files exist on disk.  Raising a runtime error is
        the preferred method of erroring out, but returning False is also a
        valid alarm.
        """
        return True
    
    
    def isEmbarrassinglyParallel(self):
        """
        Nodes that can process each input independently of the other inputs can
        overload this function and return True.  This gives the execution engine
        a hint that a single node or entire groups of nodes' can be parallelized.
        """
        return False
        

###############################################################################
## Read node generation
###############################################################################
def readNodeClassFactory(dataPacketType):
    """
    Create a new DagNode...Read node from a given dataPacket type.
    """
    dataType = dataPacketType.__name__[len("DataPacket"):]
    NewClassType = type('DagNode'+dataType+'Read', (DagNode,), {})

    # Create the new DagNode's init function
    def init(self, name=""):
        DagNode.__init__(self, name)
    NewClassType.__init__ = init
    
    # Create the new DagNode's defineInputs function
    def _defineInputs(self):
        return list()
    NewClassType._defineInputs = _defineInputs
    
    # Create the new DagNode's defineOutputs function
    def _defineOutputs(self):
        return [DagNodeOutput(dataPacketType.__name__[len('DataPacket'):], dataPacketType)]
    NewClassType._defineOutputs = _defineOutputs
    
    # Create the new DagNode's defineAttributes function
    def _defineAttributes(self):
        return list()
    NewClassType._defineAttributes = _defineAttributes
    
    # Create the executeList function
    def executeList(self, dataPacketDict, splitOperations=False):
        pass
    NewClassType.executeList = executeList

    # Create the validate function
    def validate(self):
        # Calling sceneGraphHandle without a specialized type works because we are just
        # checking the presence of data; not whether its type matches or anything else fancy.
        for output in self.outputs():
            if not self.sceneGraphHandle()[0].dataPresent(): # TODO: sceneGraphHandle should not return an array (see other yadda yaddas)
                raise RuntimeError("Data is not present for %s output." % output.name)
        return True
    NewClassType.validate = validate

    return NewClassType


######################### GENERATE READ DAG NODES #############################
def generateReadDagNodes():
    """
    Construct a collection of dag nodes for each type of data packet loaded in
    the current session.
    """
    for packetType in depends_util.allClassChildren(depends_data_packet.DataPacket):
        # Create a new class based on all child objects of DataPacket
        NewClassType = readNodeClassFactory(packetType)
        # Install class into current module
        globals()[NewClassType.__name__] = NewClassType
        del NewClassType


############ FUNCTION TO IMPORT PLUGIN NODES INTO THIS NAMESPACE  #############
def loadChildNodesFromPaths(pathList):
    """
    Given a list of directories, import all classes that reside in modules in those
    directories into the node namespace.
    """
    for path in pathList:
        nodeClassDict = depends_util.allClassesOfInheritedTypeFromDir(path, DagNode)
        for nc in nodeClassDict:
            globals()[nc] = nodeClassDict[nc]


###############################################################################
## Built-in nodes
###############################################################################
class DagNodeMaya(DagNode):
    """
    A node that handles communication with the external program, Maya.
    """
    
    # TODO : Currently this node is extremely rough.  The theory is sound, though,
    #        and it can be fleshed out as time goes on.
    
    def __init__(self, name=""):
        DagNode.__init__(self, name)
        # Special members
        self.comms = None


    def _defineInputs(self):
        """
        """
        doc = ("This node can take any data packet as input and display it in the Maya user interface.")
        return [DagNodeInput('Any', depends_data_packet.DataPacket, True, docString=doc)]
    
        
    def _defineOutputs(self):
        """
        """
        return [] 


    def _defineAttributes(self):
        """
        """
        exeDoc = ("The name of the executable that launches maya.")
        portDoc = ("The port to talk to the maya listener on.")
        return [DagNodeAttribute('executable', 'maya', docString=exeDoc),
                DagNodeAttribute('talkPort', '6002', docString=portDoc)]


    def executeList(self, dataPacketDict):
        """
        """
        if self.comms is None:
            raise RuntimeError("Communication port not present")
        
        # Test for an external maya server.
        self.comms.setBroadcastPort(int(self.attributeValue('talkPort')))
        self.comms.sendString('Test message')
        print "Node reports message sent successfully."
        
        # Push the requested data over to maya.
        for dp in dataPackets:
            dataPacket = dp[1]
            dataPacketType = dataPacket.typeStr()
            if dataPacketType == "Lightfield":
                print "Sending message to Maya to load lightfield."
                message = "LOAD <--> %s %s <--> %s %s" % (dataPacket.fileDescriptors['filename'].value, dataPacket.fileDescriptors['transform'].value, 
                                                          dataPacket.sourceNode.uuid, dataPacket.sourceNode.name)
                print message
            elif dataPacketType == "Pointcloud":
                print "Sending message to Maya to load pointcloud."
                message = "LOAD <--> %s %s <--> %s %s" % (dataPacket.fileDescriptors['filename'].value, dataPacket.fileDescriptors['transform'].value, 
                                                          dataPacket.sourceNode.uuid, dataPacket.sourceNode.name)
                print message
            else:
                print "The Maya DAG node is unsure what to do with a datapacket of type %s." % dataPacket.typeStr()
                continue
            self.comms.sendString(message)

        # Wait patiently.
        

###############################################################################
###############################################################################
class DagNodeDot(DagNode):
    """
    A dot node is a node that simply collects connections and passes them on.
    It's mostly for the benefit of the user interface.
    """
    # TODO
    def __init__(self, name=""):
        DagNode.__init__(self, name)

    def _defineInputs(self):
        return []
        
    def _defineOutputs(self):
        return [] 

    def _defineAttributes(self):
        return []

    def executeList(self, dataPacketDict):
        pass


###############################################################################
###############################################################################
class DagNodeCoalesce(DagNode):
    """
    The coalesce node takes a variety of inputs and collates them into a single
    sequence.  This is done by creating symlinks in a temporary location on disk.
    """
    # TODO
    def __init__(self, name=""):
        DagNode.__init__(self, name)

    def _defineInputs(self):
        return []
        
    def _defineOutputs(self):
        return [] 

    def _defineAttributes(self):
        return []

    def executeList(self, dataPacketDict):
        pass
