#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

from PySide import QtCore, QtGui

import depends_node
import depends_data_packet
import depends_file_dialog


"""
A QT graphics widget that displays the properties (attributes, outputs, and
inputs) of a given node.  Inputs can be modified with drag'n'drop, attributes
can be modified with keyboard input, and outputs are the same.
"""


###############################################################################
###############################################################################
class GeneralEdit(QtGui.QWidget):
    """
    An edit widget that displays a text field, two fields for the file sequence
    range, and an expansion button to hide the range fields by default.  It 
    allows tooltips to be added, modifiable bits to be set, file dialog buttons
    to be added, tighter formatting, and custom file dialogs.
    """

    # Signals
    valueChanged = QtCore.Signal(str, str, type)
    rangeChanged = QtCore.Signal(str, object, type)

    def __init__(self, label="Unknown", value="", enabled=True, isFileType=True, tighter=False, toolTip=None, customFileDialogName=None, parent=None):
        """
        """
        QtGui.QWidget.__init__(self, parent)

        self.customFileDialogName = customFileDialogName

        # The upper layout holds the label, the value, and the "expand" button
        upperLayout = QtGui.QHBoxLayout()
        upperLayout.setContentsMargins(0,5,0,5)
        #upperLayout.setSpacing(0)
        if tighter:
            upperLayout.setContentsMargins(0,0,0,0)

        self.label = QtGui.QLabel(label, self)
        if toolTip:
            self.label.setToolTip(toolTip)
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setMinimumWidth(150)
        self.lineEdit.setFixedHeight(25)
        self.lineEdit.setAlignment(QtCore.Qt.AlignRight)
        self.lineEdit.setEnabled(enabled)
        self.setValue(value)

        self.expandButton = QtGui.QPushButton(self)
        self.expandButton.setText(u'\u25be')
        self.expandButton.setMaximumWidth(30)
        self.expandButton.setFixedHeight(25)
        if not isFileType:
            self.expandButton.hide()

        upperLayout.addWidget(self.label)
        upperLayout.addWidget(self.lineEdit)
        upperLayout.addWidget(self.expandButton)

        # The lower layout holds the browse button, and the range fields
        lowerLayout = QtGui.QHBoxLayout()
        lowerLayout.setContentsMargins(0,0,0,0)
        rangeStartLabel = QtGui.QLabel("Range start", self)
        rangeEndLabel = QtGui.QLabel("end", self)
        self.rangeStart = QtGui.QLineEdit(self)
        self.rangeEnd = QtGui.QLineEdit(self)

        self.fileDialogButton = QtGui.QPushButton(self)
        self.fileDialogButton.setText("...")
        self.fileDialogButton.setMaximumWidth(30)
        self.fileDialogButton.setFixedHeight(25)

        lowerLayout.addWidget(rangeStartLabel)
        lowerLayout.addWidget(self.rangeStart)
        lowerLayout.addWidget(rangeEndLabel)
        lowerLayout.addWidget(self.rangeEnd)
        lowerLayout.addWidget(self.fileDialogButton)

        self.lowerContainer = QtGui.QWidget(self)
        self.lowerContainer.setLayout(lowerLayout)
        self.lowerContainer.hide()

        # Stick both layouts in a vertical layout wrapper
        outerLayout = QtGui.QVBoxLayout(self)
        outerLayout.setContentsMargins(0,0,0,0)
        outerLayout.addLayout(upperLayout)
        outerLayout.addWidget(self.lowerContainer)
        self.setLayout(outerLayout)

        # Chain signals out with property name and value
        self.lineEdit.editingFinished.connect(lambda: self.valueChanged.emit(self.label.text(), self.lineEdit.text(), depends_node.DagNodeAttribute))
        self.rangeStart.editingFinished.connect(lambda: self.rangeChanged.emit(self.label.text(), (self.rangeStart.text(), self.rangeEnd.text()), depends_node.DagNodeAttribute))
        self.rangeEnd.editingFinished.connect(lambda: self.rangeChanged.emit(self.label.text(), (self.rangeStart.text(), self.rangeEnd.text()), depends_node.DagNodeAttribute))
        self.expandButton.pressed.connect(self.expandButtonPressed)
        self.fileDialogButton.pressed.connect(self.fileDialogButtonPressed)


    def setValue(self, value):
        """
        A clean interface for setting the property value and emitting signals.
        """
        self.lineEdit.setText(value)
        self.lineEdit.editingFinished.emit()    # TODO: Is this necessary?  Might be legacy.
    
    
    def setRange(self, seqRange):
        """
        A clean interface for setting the range and emitting its signals.
        """
        if not seqRange:
            return
        self.rangeStart.setText(seqRange[0] if seqRange[0] else "")
        self.rangeEnd.setText(seqRange[1] if seqRange[1] else "")
        
    
    def expandButtonPressed(self):
        """
        Show any additional information hidden by default.
        """
        if self.lowerContainer.isVisible():
            self.lowerContainer.setVisible(False)
            self.expandButton.setText(u'\u25be')
        else:
            self.lowerContainer.setVisible(True)
            self.expandButton.setText(u'\u25b4')


    def fileDialogButtonPressed(self):
        """
        Display either the standard file dialog or a custom file dialog defined
        by the constructor.
        """
        selectedFile = None
        if self.customFileDialogName:
            selectedFile = depends_file_dialog.fileDialogOfType(self.customFileDialogName).browse()
        else:
            selectedFile = depends_file_dialog.fileDialogOfType("Standard Qt File Dialog").browse()
        if not selectedFile:
            return
        self.setValue(selectedFile)


###############################################################################
###############################################################################
class InputEdit(QtGui.QWidget):
    """
    An edit widget that only allows for dropping "dag location strings" onto it.
    This edit holds an input, dag node, and dag so it can manage and display
    different information from what is stored inside.
    """
    
    # Signals
    valueChanged = QtCore.Signal(str, str, type)
    rangeChanged = QtCore.Signal(str, object, type)
    mouseover = QtCore.Signal(depends_node.DagNode)
    
    def __init__(self, input=None, dagNode=None, dag=None, parent=None):
        """
        """
        QtGui.QWidget.__init__(self, parent)
        self.dag = dag
        self.dagNode = dagNode
        self.input = input

        # A strange hack to make sure messages get passed properly
        # Can be removed if requirements are met (see comments below)
        self.inputHasBeenChangedTo = ""

        # The upper layout holds the label, the value, and the "expand" button
        upperLayout = QtGui.QHBoxLayout()
        upperLayout.setContentsMargins(0,5,0,5)
        #upperLayout.setSpacing(0)
        
        self.label = QtGui.QLabel(input.name, self)
        self.label.setToolTip(input.docString)
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setMinimumWidth(150)
        self.lineEdit.setFixedHeight(25)
        self.lineEdit.setAcceptDrops(False)
        self.lineEdit.setAlignment(QtCore.Qt.AlignRight)
        self.lineEdit.setReadOnly(True)
        #self.originalLineEditPalette = QtGui.QPalette(self.lineEdit.palette())
        self.setValue(input.value)

        self.expandButton = QtGui.QPushButton(self)
        self.expandButton.setText(u'\u25be')
        self.expandButton.setMaximumWidth(30)
        self.expandButton.setFixedHeight(25)

        upperLayout.addWidget(self.label)
        upperLayout.addWidget(self.lineEdit)
        upperLayout.addWidget(self.expandButton)

        # The lower layout holds the browse button, and the range fields
        lowerLayout = QtGui.QHBoxLayout()
        lowerLayout.setContentsMargins(0,0,0,0)
        #lowerLayout.setSpacing(0)
        rangeStartLabel = QtGui.QLabel("Range start", self)
        rangeEndLabel = QtGui.QLabel("end", self)
        self.rangeStart = QtGui.QLineEdit(self)
        self.rangeStart.setAcceptDrops(False)
        self.rangeEnd = QtGui.QLineEdit(self)
        self.rangeEnd.setAcceptDrops(False)
        
        self.removeInputButton = QtGui.QPushButton(self)
        self.removeInputButton.setText(u'\u2716')
        self.removeInputButton.setMaximumWidth(30)
        self.removeInputButton.setFixedHeight(25)
        
        lowerLayout.addWidget(rangeStartLabel)
        lowerLayout.addWidget(self.rangeStart)
        lowerLayout.addWidget(rangeEndLabel)
        lowerLayout.addWidget(self.rangeEnd)
        lowerLayout.addWidget(self.removeInputButton)
        
        self.lowerContainer = QtGui.QWidget(self)
        self.lowerContainer.setLayout(lowerLayout)
        self.lowerContainer.hide()

        # Stick both layouts in a vertical layout wrapper
        outerLayout = QtGui.QVBoxLayout(self)
        outerLayout.setContentsMargins(0,0,0,0)
        outerLayout.addLayout(upperLayout)
        outerLayout.addWidget(self.lowerContainer)
        self.setLayout(outerLayout)

        # Enable connections to be dragged, then dropped on this guy
        self.setAcceptDrops(True)

        # The lineEdit gets a textChanged signal since editingFinished never occurs with the read-only field
        self.lineEdit.textChanged.connect(lambda: self.valueChanged.emit(self.label.text(), self.inputHasBeenChangedTo, depends_node.DagNodeInput))
        self.rangeStart.editingFinished.connect(lambda: self.rangeChanged.emit(self.label.text(), (self.rangeStart.text(), self.rangeEnd.text()), depends_node.DagNodeInput))
        self.rangeEnd.editingFinished.connect(lambda: self.rangeChanged.emit(self.label.text(), (self.rangeStart.text(), self.rangeEnd.text()), depends_node.DagNodeInput))
        self.expandButton.pressed.connect(self.expandButtonPressed)
        self.removeInputButton.pressed.connect(self.removeInputButtonPressed)


    ###########################################################################
    ## Drag and drop
    ###########################################################################
    def highlightIfMatching(self, dagNodeList):
        """
        Change the background color of our line edit if our input is in the
        given list of dag nodes.
        """
        if dagNodeList is None:
            self.lineEdit.setStyleSheet("")
            #self.lineEdit.setPalette(self.originalLineEditPalette)
            return
        connectionUuid = depends_data_packet.uuidFromScenegraphLocationString(self.input.value)
        for dagNode in dagNodeList:
            if dagNode.uuid == connectionUuid:
                self.lineEdit.setStyleSheet("background-color: rgb(91, 114, 138)")
                #pal = QtGui.QPalette(self.lineEdit.palette())
                #pal.setColor(QtGui.QPalette.Text, QtGui.QColor(162, 209, 255))
                #self.lineEdit.setPalette(pal)
                
    
    def enterEvent(self, event):
        """
        When the mouse enters the dialog, let the world know which dagNode 
        you are referring to by emitting a mouseover signal.
        """
        idString = self.input.value
        connectedDagNode = self.dag.node(nUUID=depends_data_packet.uuidFromScenegraphLocationString(idString))
        if (connectedDagNode):
            self.mouseover.emit([connectedDagNode])
        QtGui.QWidget.enterEvent(self, event)
        
        
    def leaveEvent(self, event):
        """
        Emit a mouseover event stating you have left the dialog.
        """
        self.mouseover.emit(None)
        QtGui.QWidget.leaveEvent(self, event)


    def dragEnterEvent(self, event):
        """
        If the user is dragging a valid text object (correct DAG path format),
        let QT know it is okay to drop it (also, show a cute icon stating as much)
        """
        if event.mimeData().hasFormat("text/plain"):
            outputType = self.dag.nodeOutputType(*depends_data_packet.nodeAndOutputFromScenegraphLocationString(event.mimeData().text(), self.dag))
            if outputType not in self.dagNode.dataPacketTypesAccepted():
                QtGui.QWidget.dragEnterEvent(self, event)
                return
            event.acceptProposedAction()
        QtGui.QWidget.dragEnterEvent(self, event)
        
        
    def dropEvent(self, event):
        """
        Already having vetted the data in dragEnterEvent, let the user set the
        input based on the dropped text.
        """
        self.setValue(event.mimeData().text())
        event.acceptProposedAction()
        

    ###########################################################################
    ## Interface
    ###########################################################################
    def setValue(self, value):
        """
        Set the value of this edit's input object to the given string and 
        handle the messages appropriately.
        """
        # The only way to get the shorthand location string is to set the existing
        # input to the new full ID and request the string.  This means that when
        # we send the valueChanged signal, it was getting an "old value" identical
        # to the new value.  Setting the input's value to what it used to be before
        # emitting the message has provided a temporary bandaid.
        oldValue = self.input.value
        self.input.value = value
        self.inputHasBeenChangedTo = value 
        if self.input.value != "":
            dataPacketForInput = self.dag.nodeInputDataPacket(self.dagNode, self.input)
            self.input.value = oldValue
            self.lineEdit.setText(depends_data_packet.shorthandScenegraphLocationString(dataPacketForInput))
        else:
            self.lineEdit.setText("")
        
        # Code to color based on whether the input data is present or not.
        #incomingDataPacket =  self.dag.nodeInputDataPacket(self.node, self.input)
        #if x.dataPresent():
        #   pal.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 255, 162))
        #else:
        #   pal.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 0, 162))
        #self.lineEdit.setPalette(pal)


    def setRange(self, seqRange):
        """
        Set either the low and the high ends of the range.
        """
        if not seqRange:
            return
        self.rangeStart.setText(seqRange[0] if seqRange[0] else "")
        self.rangeEnd.setText(seqRange[1] if seqRange[1] else "")

        # Code to clamp sequence ranges.  Need to put this in the callback for text editing
        #incomingDataPacket = self.dag.nodeOutputDataPacket(*depends_data_packet.nodeAndOutputFromScenegraphLocationString(self.input.value, self.dag))
        #incomingRange = incomingDataPacket.sequenceRange
        #if incomingRange:
        #   if incomingRange[0] and int(incomingRange[0]) > int(seqRange[0]):
        #       seqRange = (incomingRange[0], seqRange[1])
        #   if incomingRange[1] and int(incomingRange[1]) < int(seqRange[1]):
        #       seqRange = (seqRange[0], incomingRange[1])

    
    def expandButtonPressed(self):
        """
        Show the range and removeInput buttons hidden by default.
        """
        if self.lowerContainer.isVisible():
            self.lowerContainer.setVisible(False)
            self.expandButton.setText(u'\u25be')
        else:
            self.lowerContainer.setVisible(True)
            self.expandButton.setText(u'\u25b4')
    
    
    def removeInputButtonPressed(self):
        """
        Is the user removing this input?
        """
        self.setValue("")
        # TODO: Range as well?
        self.mouseover.emit(None)


###############################################################################
###############################################################################
class OutputEdit(QtGui.QWidget):
    """
    An edit widget that shows a single output type as a collection of general
    edits.  Outputs only have one frame range for all filenames (locked 
    together), so only a single general edit has a file rollout.  This widget
    is made slightly interesting by the fact that an output type can change
    based on its inputs.
    """

    # Signals
    valueChanged = QtCore.Signal(str, str, type)
    rangeChanged = QtCore.Signal(str, object, type)

    def __init__(self, output=None, dagNode=None, dag=None, parent=None, tighter=True):
        """
        """
        QtGui.QWidget.__init__(self, parent)
        self.dag = dag
        self.dagNode = dagNode
        self.output = output
        self.subGroups = dict()
        self.currentSubGroup = None

        # Make all possible widget collections
        for outputType in self.output.allPossibleOutputTypes():
            subGroup = QtGui.QGroupBox("%s (Type: %s)" % (output.name, outputType.__name__[len("DataPacket"):]))
            subLayout = QtGui.QVBoxLayout()
            subOutputs = depends_data_packet.filenameDictForDataPacketType(outputType)
            i = 0
            for subOutputName in subOutputs:
                newThing = GeneralEdit(label=subOutputName, 
                                       tighter=True, 
                                       isFileType=True if i == len(subOutputs)-1 else False, 
                                       toolTip=self.output.docString, 
                                       customFileDialogName=self.output.customFileDialogName, 
                                       parent=subGroup)
                i += 1
                newThing.setValue(dagNode.outputValue(output.name, subOutputName, variableSubstitution=False))
                newThing.setRange(dagNode.outputRange(output.name, variableSubstitution=False))
                newThing.valueChanged.connect(self.valueChangedStub)
                newThing.rangeChanged.connect(self.rangeChangedStub)
                subLayout.addWidget(newThing)
            subGroup.setLayout(subLayout)
            self.subGroups[outputType] = subGroup

        # Ask the DAG what's really going through this node and set the group accordingly
        outputType = self.dag.nodeOutputType(self.dagNode, self.output)
        self.currentSubGroup = self.subGroups[outputType]
        self.outputLayout = QtGui.QVBoxLayout()
        self.outputLayout.addWidget(self.currentSubGroup)
        parent.setLayout(self.outputLayout)


    def valueChangedStub(self, subName, value, type):
        """
        A stub function for combining the output name and its subname for
        emitting the valueChanged message.
        """
        # Try to resist converting this into a lambda, as it seems chaining lambdas causes
        # some issues (segfault) when Qt cleans up after itself on close.
        self.valueChanged.emit(self.output.name+"."+subName, value, depends_node.DagNodeOutput)


    def rangeChangedStub(self, subName, seqRange, type):
        """
        A stub function for changing the range.
        """
        # TODO: Might not be needed anymore (legacy)?
        #Try to resist converting this into a lambda, as it seems chaining lambdas causes
        #some issues (segfault) when Qt cleans up after itself on close.
        self.rangeChanged.emit(self.output.name, seqRange, depends_node.DagNodeOutput)


    def refresh(self):
        """
        Handle the small complications of refreshing an entire output edit.
        """
        # Clear
        self.outputLayout.removeWidget(self.currentSubGroup)
        self.currentSubGroup.setParent(None)
        
        # Add
        outputType = self.dag.nodeOutputType(self.dagNode, self.output)
        self.currentSubGroup = self.subGroups[outputType]
        self.outputLayout.addWidget(self.currentSubGroup)

        # Set
        for edit in self.currentSubGroup.findChildren(GeneralEdit):
            self.blockSignals(True)
            edit.setValue(self.dagNode.outputValue(self.output.name, edit.label.text(), variableSubstitution=False))
            edit.setRange(self.dagNode.outputRange(self.output.name, variableSubstitution=False))
            self.blockSignals(False)


###############################################################################
###############################################################################
class AttrEdit(GeneralEdit):
    """
    An edit widget that is basically a general edit, but also stores the 
    attribute object, dagNode we're associated with, and dag the node is a 
    member of.
    """

    def __init__(self, attribute=None, dagNode=None, dag=None, parent=None):
        """
        """
        GeneralEdit.__init__(self, 
                             label=attribute.name, 
                             isFileType=attribute.isFileType, 
                             toolTip=attribute.docString, 
                             customFileDialogName=attribute.customFileDialogName, 
                             parent=parent)
        self.dag = dag
        self.dagNode = dagNode
        self.attribute = attribute


    def fileDialogButtonPressed(self):
        """
        Display either the standard file dialog or a custom file dialog defined
        by the constructor.
        """
        # TODO: Plugin file dialog (copy from above)!
        selectedFile = QtGui.QFileDialog.getOpenFileName()
        if not selectedFile[0]:
            return
        self.setValue(selectedFile[0])


###############################################################################
###############################################################################
class PropWidget(QtGui.QWidget):
    """
    The full graphics view containing general edits for the object name and 
    type, and input, attribute, and output edits for all the node's properties.
    """

    # Signals
    attrChanged = QtCore.Signal(depends_node.DagNode, str, str, type)
    rangeChanged = QtCore.Signal(depends_node.DagNode, str, object, type)
    mouseover = QtCore.Signal(depends_node.DagNode)

    def __init__(self, parent=None):
        """
        """
        QtGui.QWidget.__init__(self, parent)
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.scrollArea = QtGui.QScrollArea()
        self.mainLayout.addWidget(self.scrollArea)
        self.foo = QtGui.QWidget(self)
        self.scrollAreaLayout = QtGui.QVBoxLayout(self.foo)
        self.scrollAreaLayout.setAlignment(QtCore.Qt.AlignTop)
        self.foo.setLayout(self.scrollAreaLayout)
        self.scrollArea.setWidget(self.foo)
        self.setLayout(self.mainLayout)
        self.scrollArea.setWidgetResizable(True)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        
        self.dagNode = None


    def highlightInputs(self, dagNodeList):
        """
        Given a list of dag nodes, highlight any inputs that may contain links
        to the nodes.
        """
        allInputEdits = self.findChildren(InputEdit)
        for ie in allInputEdits:
            ie.highlightIfMatching(dagNodeList)


    def rebuild(self, dag, dagNodes):
        """
        Completely reconstruct the entire widget from a dag and a list of 
        nodes.
        """
        # Clear out all existing widgets
        for child in self.foo.children():
            if type(child) is not type(QtGui.QVBoxLayout()):
                self.scrollAreaLayout.removeWidget(child)
                child.setParent(None)
                child.deleteLater()

        # We only allow one node to be selected so far
        if not dagNodes or len(dagNodes) > 1:
            return
        
        # Helpers
        self.dagNode = dagNodes[0]
        attrChangedLambda = lambda propName, newValue, type, func=self.attrChanged.emit: func(self.dagNode, propName, newValue, type)
        rangeChangedLambda = lambda propName, newRange, type, func=self.rangeChanged.emit: func(self.dagNode, propName, newRange, type)

        # Populate the UI with name and type
        nameWidget = GeneralEdit("Name", self.dagNode.name, isFileType=False, parent=self)
        nameWidget.valueChanged.connect(attrChangedLambda)
        self.scrollAreaLayout.addWidget(nameWidget)
        self.scrollAreaLayout.addWidget(GeneralEdit("Type", self.dagNode.typeStr(), enabled=False, isFileType=False, parent=self))

        # Add the inputs
        if self.dagNode.inputs():
            inputGroup = QtGui.QGroupBox("Inputs")
            inputLayout = QtGui.QVBoxLayout()
            for input in self.dagNode.inputs():
                newThing = InputEdit(input=input, dagNode=self.dagNode, dag=dag, parent=inputGroup)
                newThing.mouseover.connect(self.mouseover)
                newThing.setValue(self.dagNode.inputValue(input.name, variableSubstitution=False))
                newThing.setRange(self.dagNode.inputRange(input.name, variableSubstitution=False))
                inputLayout.addWidget(newThing)
                newThing.valueChanged.connect(attrChangedLambda)
                newThing.rangeChanged.connect(rangeChangedLambda)
            inputGroup.setLayout(inputLayout)
            self.scrollAreaLayout.addWidget(inputGroup)
        
        # Add the attributes (don't show any attributes that begin with input/output keywords)
        if self.dagNode.attributes():
            attributeGroup = QtGui.QGroupBox("Attributes")
            attributeLayout = QtGui.QVBoxLayout()
            for attribute in self.dagNode.attributes():
                newThing = AttrEdit(attribute=attribute, dagNode=self.dagNode, dag=dag, parent=attributeGroup)
                newThing.setValue(self.dagNode.attributeValue(attribute.name, variableSubstitution=False))
                newThing.setRange(self.dagNode.attributeRange(attribute.name, variableSubstitution=False))
                attributeLayout.addWidget(newThing)
                newThing.valueChanged.connect(attrChangedLambda)
                newThing.rangeChanged.connect(rangeChangedLambda)
            attributeGroup.setLayout(attributeLayout)
            self.scrollAreaLayout.addWidget(attributeGroup)
        
        # Add the outputs
        if self.dagNode.outputs():
            outputGroup = QtGui.QGroupBox("Outputs")
            outputLayout = QtGui.QVBoxLayout()
            for output in self.dagNode.outputs():
                newThing = OutputEdit(output=output, dagNode=self.dagNode, dag=dag, parent=outputGroup)
                outputLayout.addWidget(newThing)
                newThing.valueChanged.connect(attrChangedLambda)
                newThing.rangeChanged.connect(rangeChangedLambda)
            outputGroup.setLayout(outputLayout)
            self.scrollAreaLayout.addWidget(outputGroup)


    def refresh(self):
        """
        Refresh the values of all the input, output, and attribute fields
        without a full reconstruction of the widget.
        """
        groupBoxes = self.findChildren(QtGui.QGroupBox)
        inputBox = None
        attributeBox = None
        outputBox = None
        for gb in groupBoxes:
            title = gb.title()
            if title == "Inputs": inputBox = gb
            elif title == "Attributes": attributeBox = gb
            elif title == "Outputs": outputBox = gb
        
        if inputBox:
            inputEdits = inputBox.findChildren(InputEdit)
            for inputEdit in inputEdits:
                inputEdit.blockSignals(True)
                inputName = inputEdit.label.text()
                inputEdit.setValue(self.dagNode.inputValue(inputName, variableSubstitution=False))
                inputEdit.setRange(self.dagNode.inputRange(inputName, variableSubstitution=False))
                inputEdit.blockSignals(False)
        if attributeBox:
            attributeEdits = attributeBox.findChildren(AttrEdit)
            for attrEdit in attributeEdits:
                attrEdit.blockSignals(True)
                attributeName = attrEdit.label.text()
                attrEdit.setValue(self.dagNode.attributeValue(attributeName, variableSubstitution=False))
                attrEdit.setRange(self.dagNode.attributeRange(attributeName, variableSubstitution=False))
                attrEdit.blockSignals(False)
        if outputBox:
            outputEdits = outputBox.findChildren(OutputEdit)
            for outputEdit in outputEdits:
                outputEdit.refresh()
                
                
