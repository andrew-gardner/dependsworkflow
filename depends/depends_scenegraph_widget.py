#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

from PySide import QtCore, QtGui

import depends_node
import depends_data_packet


"""
A QT graphics widget that displays the state of a given scenegraph.  The user
can also mouseover a given item, which emits a mouseover QT signal.
"""


###############################################################################
###############################################################################
class SceneGraphWidget(QtGui.QWidget):
    """
    A QT graphics widget that displays items in a given scenegraph and the 
    presence of each item's data.  It is also capable of highlighting a 
    collection of items if desired.
    """

    # Signals
    mouseover = QtCore.Signal(depends_node.DagNode)

    def __init__(self, parent=None):
        """
        """
        QtGui.QWidget.__init__(self, parent)
        
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)
        self.setMinimumWidth(400)
        
        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.tableWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tableWidget.setStyleSheet("QTableWidget::item:selected{ background-color: rgb(91, 114, 138); }")
        self.mainLayout.addWidget(self.tableWidget)


    def highlightRowsUsingNodes(self, dagNodes):
        """
        Given a list of dag nodes, highlight all the rows they live in.
        """
        if dagNodes is None:
            self.tableWidget.clearSelection()
            return
        for dagNode in dagNodes:
            for row in range(self.tableWidget.rowCount()):
                widget = self.tableWidget.cellWidget(row, 0)
                if widget.pointerToDataPacket.sourceNode is dagNode:
                    self.tableWidget.selectRow(row)


    def handleMouseover(self, dagNodes):
        """
        Highlight the row the mouse is over, and emit this class' mouseover signal.
        """
        self.highlightRowsUsingNodes(dagNodes)
        self.mouseover.emit(dagNodes)
        

    def rebuild(self, sceneGraph, selectedDagNode):
        """
        Rebuild the current widget, given a scene graph object and the selected
        dag node.  A value of None in the sceneGraph field clears the widget, and
        a value of none in the selectedDagNode field displays all nodes including
        the selected one.
        """
        if not sceneGraph:
            self.tableWidget.setRowCount(0)
            return
        
        # Count the number of rows
        rowCount = len([dp for dp in sceneGraph if dp.sourceNode != selectedDagNode])
        self.tableWidget.setRowCount(rowCount)

        index = 0
        for dataPacket in sceneGraph:
            if dataPacket.sourceNode == selectedDagNode:
                continue
            self.tableWidget.setRowHeight(index, 20)
            
            # If the selected dag node can't read the datatype, make it obvious
            disabled = False
            if selectedDagNode.dataPacketTypesAccepted() and type(dataPacket) not in selectedDagNode.dataPacketTypesAccepted():
                disabled = True

            # Add the text field with enhanced middle-button drag'n'drop functionality
            class DraggableTextWidget(QtGui.QLabel):
                # Signals
                mouseover = QtCore.Signal(depends_node.DagNode)

                def __init__(self, dataPacket, *args):
                    super(DraggableTextWidget, self).__init__(*args)
                    self.pointerToDataPacket = dataPacket
                    self.setStyleSheet("background:transparent;")
                
                def mousePressEvent(self, event):
                    #if event.buttons() != QtCore.Qt.MiddleButton:
                    #   return QtGui.QLabel().mousePressEvent(event)
                    mimeData = QtCore.QMimeData()
                    dragText = depends_data_packet.scenegraphLocationString(self.pointerToDataPacket)
                    mimeData.setText(dragText)
                    drag = QtGui.QDrag(self)
                    drag.setMimeData(mimeData)
                    drag.exec_(QtCore.Qt.CopyAction)
                    #QtGui.QLabel.mousePressEvent(self, event)
                    
                def enterEvent(self, event):
                    self.mouseover.emit([self.pointerToDataPacket.sourceNode])
                    QtGui.QLabel.enterEvent(self, event)
                    
                def leaveEvent(self, event):
                    self.mouseover.emit(None)
                    QtGui.QLabel.leaveEvent(self, event)
            textWidget = DraggableTextWidget(dataPacket)
            
            textWidget.setTextFormat(QtCore.Qt.RichText)
            colorString = "00aa00" if dataPacket.dataPresent() else "aa0000"
            if disabled:
                colorString = "868686"
            textWidget.setText("<html><font color=\"#%s\">&nbsp;%s</font> - %s</html>" % (colorString, dataPacket.typeStr(), depends_data_packet.shorthandScenegraphLocationString(dataPacket)))
            self.tableWidget.setCellWidget(index, 0, textWidget)

            # Chain the text edit mouseover signal out with property name and value
            textWidget.mouseover.connect(self.handleMouseover)
            index += 1

        # Unsure if this is really necessary, but it makes a difference
        self.repaint()
