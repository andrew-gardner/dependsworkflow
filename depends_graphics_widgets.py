#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import math

from PySide import QtCore, QtGui

import depends_node
import depends_undo_commands


"""
A collection of QT graphics widgets that displays and allows the user to 
manipulate a dependency graph.  From the entire scene, to the nodes, to the
connections between the nodes, to the nubs the connections connect to.
"""


###############################################################################
###############################################################################
class DrawNodeNub(QtGui.QGraphicsItem):
	"""
	A QGraphicsItem representing the small clickable nub at the end of a DAG
	node.  New connections can be created by clicking and dragging from this.
	"""
	
	Type = QtGui.QGraphicsItem.UserType + 3


	def __init__(self):
		"""
		"""
		QtGui.QGraphicsItem.__init__(self)

		self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
		self.setCacheMode(self.DeviceCoordinateCache)
		self.setZValue(-1)
		
		self.radius = 10


	def type(self):
		"""
		Assistance for the QT windowing toolkit.
		"""
		return DrawNodeNub.Type


	def boundingRect(self):
		"""
		Defines the clickable hit box.
		"""
		return QtCore.QRectF(-3, self.parentItem().height/2.0-2.0, 5.5, 5.5)
	

	def paint(self, painter, option, widget):
		"""
		Draw the nub.
		"""
		painter.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
		painter.setPen(QtGui.QPen(QtCore.Qt.yellow, 0))
		painter.drawPie(QtCore.QRectF(-2.5, self.parentItem().height/2.0-2.5, 5, 5), 16*180, 16*180)


	def mousePressEvent(self, event):
		"""
		Accept left-button clicks to create the new connection.
		"""
		tempEdge = DrawEdge(self.parentItem(), None, floatingDestinationPoint=event.scenePos())
		self.scene().addItem(tempEdge)
		self.ungrabMouse()
		tempEdge.dragging = True		# TODO: Probably better done with an DrawEdge function (still valid?)
		tempEdge.grabMouse()
		event.accept()
		return


###############################################################################
###############################################################################
class DrawNode(QtGui.QGraphicsItem):
	"""
	A QGraphicsItem representing a node in a dependency graph.  These can be
	selected, moved, and connected together with DrawEdges.
	"""
	
	Type = QtGui.QGraphicsItem.UserType + 1


	def __init__(self, dagNode):
		"""
		"""
		QtGui.QGraphicsItem.__init__(self)

		# The corresponding DAG node
		self.dagNode = dagNode

		# Input and output edges
		self.incomingDrawEdgeList = list()
		self.outgoingDrawEdgeList = list()

		self.nub = DrawNodeNub()
		self.nub.setParentItem(self)

		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
		self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
		self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
		self.setCacheMode(self.DeviceCoordinateCache)
		self.setZValue(-1)
		
		self.width = 150
		self.height = 20

		# For handling movement undo/redos of groups of objects
		# This is a little strange to be handled by the node itself 
		# and maybe can move elsewhere?
		self.clickSnap = None
		self.clickPosition = None

		if type(self.dagNode) == depends_node.DagNodeDot:
			self.width = 15
			self.height = 15

	def type(self):
		"""
		Assistance for the QT windowing toolkit.
		"""
		return DrawNode.Type


	def removeDrawEdge(self, edge):
		"""
		Removes the given edge from this node's list of edges.
		"""
		if edge in self.incomingDrawEdgeList:
			self.incomingDrawEdgeList.remove(edge)
		elif edge in self.outgoingDrawEdgeList:
			self.outgoingDrawEdgeList.remove(edge)
		else:
			raise RuntimeError("Attempting to remove drawEdge that doesn't exist from node %s." % self.dagNode.name)
			

	def addDrawEdge(self, edge):
		"""
		Add a given draw edge to this node.
		"""
		if edge.destDrawNode() == self:
			self.incomingDrawEdgeList.append(edge)
		elif edge.sourceDrawNode() == self:
			self.outgoingDrawEdgeList.append(edge)
		edge.adjust()


	def drawEdges(self):
		"""
		Return all incoming and outgoing edges in a list.
		"""
		return (self.incomingDrawEdgeList + self.outgoingDrawEdgeList)


	def incomingDrawEdges(self):
		"""
		Return only incoming edges in a list.
		"""
		return self.incomingDrawEdgeList


	def outgoingDrawEdges(self):
		"""
		Return only outgoing edges in a list.
		"""
		return self.outgoingDrawEdgeList


	def boundingRect(self):
		"""
		Defines the clickable hit-box.  Simply returns a rectangle instead of
		a rounded rectangle for speed purposes.
		"""
		# TODO: Is this the right place to put this?  Maybe setWidth (adjust) would be fine.
		#if len(self.dagNode.name)*10 != self.width:
		#	self.prepareGeometryChange()
		#	self.width = len(self.dagNode.name)*10
		#	if self.width < 9: 
		#		self.width = 9
		adjust = 2.0
		return QtCore.QRectF(-self.width/2  - adjust, 
							 -self.height/2 - adjust,
							  self.width  + 3 + adjust, 
							  self.height + 3 + adjust)

	def shape(self):
		"""
		The QT shape function.
		"""
		# TODO: Find out what this is for again?
		path = QtGui.QPainterPath()
		path.addRoundedRect(QtCore.QRectF(-self.width/2, -self.height/2, self.width, self.height), 5, 5)
		return path


	def paint(self, painter, option, widget):
		"""
		Draw the node, whether it's in the highlight list, selected or 
		unselected, is currently executable, and its name.  Also draws a 
		little light denoting if it already has data present and/or if it is
		in a "stale" state.
		"""
		inputsFulfilled = self.scene().dag.nodeAllInputsDataPresent(self.dagNode)
		
		# Draw the box
		gradient = QtGui.QLinearGradient(0, -self.height/2, 0, self.height/2)
		if option.state & QtGui.QStyle.State_Selected:
			gradient.setColorAt(0, QtGui.QColor(255, 255 if inputsFulfilled else 172, 0))
			gradient.setColorAt(1, QtGui.QColor(200, 128 if inputsFulfilled else 0, 0))
		else:
			topGrey = 200 if inputsFulfilled else 128
			bottomGrey = 96 if inputsFulfilled else 64
			gradient.setColorAt(0, QtGui.QColor(topGrey, topGrey, topGrey))
			gradient.setColorAt(1, QtGui.QColor(bottomGrey, bottomGrey, bottomGrey))

		# Draw a fat, bright outline if it's a highlighted node
		if self in self.scene().highlightNodes:
			highlightColor = QtGui.QColor(0, 128, 255)
			if self.scene().highlightIntensities:
				intensityIndex = self.scene().highlightIntensities[self.scene().highlightNodes.index(self)]
				highlightColor.setGreen(highlightColor.green() * intensityIndex)
				highlightColor.setBlue(highlightColor.blue() * intensityIndex)
			painter.setPen(QtGui.QPen(highlightColor, 3))
		else:
			painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
		painter.setBrush(QtGui.QBrush(gradient))
		fullRect = QtCore.QRectF(-self.width/2, -self.height/2, self.width, self.height)
		painter.drawRoundedRect(fullRect, 5, 5)

		# No lights or text for dot nodes
		if type(self.dagNode) == depends_node.DagNodeDot:
			return

		# The "data present" light
		painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.25))
		for output in self.dagNode.outputs():
			if self.scene().dag.nodeOutputDataPacket(self.dagNode, output).dataPresent():
				painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 0)))
			else:
				painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				break

		# The stale light overrides all
		if self.scene().dag.nodeStaleState(self.dagNode):
			painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 59, 174)))
		painter.drawRect(QtCore.QRectF(-self.width/2+5, -self.height/2+5, 5, 5))

		# Text (none for dot nodes)
		textRect = QtCore.QRectF(self.boundingRect().left() + 4,  self.boundingRect().top(),
								 self.boundingRect().width() - 4, self.boundingRect().height())
		font = painter.font()
		font.setPointSize(10)
		painter.setFont(font)
		painter.setPen(QtCore.Qt.black)
		painter.drawText(textRect, QtCore.Qt.AlignCenter, self.dagNode.name)


	def mousePressEvent(self, event):
		"""
		Help manage mouse movement undo/redos.
		"""
		# Note: This works without an 'if' because the only mouse button that 
		#       comes through here is the left
		QtGui.QGraphicsItem.mousePressEvent(self, event)
		
		# Let the QT parent class handle the selection process before querying what's selected
		self.clickSnap = self.scene().dag.snapshot(nodeMetaDict=self.scene().nodeMetaDict(), connectionMetaDict=self.scene().connectionMetaDict())
		self.clickPosition = self.pos()
		

	def mouseReleaseEvent(self, event):
		"""
		Help manage mouse movement undo/redos.
		"""
		# Don't register undos for selections without moves
		if self.pos() != self.clickPosition:
			currentSnap = self.scene().dag.snapshot(nodeMetaDict=self.scene().nodeMetaDict(), connectionMetaDict=self.scene().connectionMetaDict())
			self.scene().undoStack().push(depends_undo_commands.SceneOnlyUndoCommand(self.clickSnap, currentSnap, self.scene()))
		QtGui.QGraphicsItem.mouseReleaseEvent(self, event)


	def itemChange(self, change, value):
		"""
		If the node has been moved, update all of its draw edges.
		"""
		if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
			for edge in self.drawEdges():
				edge.adjust()
		return QtGui.QGraphicsItem.itemChange(self, change, value)


###############################################################################
###############################################################################
class DrawEdge(QtGui.QGraphicsItem):
	"""
	A QGraphicsItem representing a connection between two DAG nodes.  These can
	be clicked and dragged to change, add, or remove connections between nodes.
	"""

	TwoPi = 2.0 * math.pi
	Type = QtGui.QGraphicsItem.UserType + 2


	def __init__(self, sourceDrawNode, destDrawNode, floatingDestinationPoint=0.0):
		"""
		"""
		QtGui.QGraphicsItem.__init__(self)

		self.arrowSize = 5.0
		self.sourcePoint = QtCore.QPointF()
		self.destPoint = QtCore.QPointF()
		self.horizontalConnectionOffset = 0.0
		self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)

		self.setZValue(-2)

		self.source = sourceDrawNode
		self.dest = destDrawNode
		if not self.dest:
			self.floatingDestinationPoint = floatingDestinationPoint
		self.source.addDrawEdge(self)
		if self.dest:
			self.dest.addDrawEdge(self)
		self.adjust()

		# MouseMoved is a little hack to get around a bug where clicking the mouse and not dragging caused an error
		self.mouseMoved = False
		self.dragging = False


	def type(self):
		"""
		Assistance for the QT windowing toolkit.
		"""
		return DrawEdge.Type


	def sourceDrawNode(self):
		"""
		Simple accessor.
		"""
		return self.source


	def setSourceDrawNode(self, drawNode):
		"""
		Set the edge's source draw node and adjust the edge's representation.
		"""
		self.source = drawNode
		self.adjust()


	def destDrawNode(self):
		"""
		Simple accessor.
		"""
		return self.dest


	def setDestDrawNode(self, drawNode):
		"""
		Set the edge's destination draw node and adjust the edge's representation.
		"""
		self.dest = drawNode
		self.adjust()


	def adjust(self):
		"""
		Recompute where the line is pointing.
		"""
		if not self.source:
			return

		if self.dest:
			line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0), self.mapFromItem(self.dest, 0, 0))
		else:
			line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0), self.floatingDestinationPoint)
		length = line.length()

		if length == 0.0:
			return

		self.prepareGeometryChange()
		self.sourcePoint = line.p1() + QtCore.QPointF(0, (self.sourceDrawNode().height/2) + 1)
		if self.dest:
			self.destPoint = line.p2() - QtCore.QPointF(0, self.destDrawNode().height/2)
			self.destPoint += QtCore.QPointF(self.horizontalConnectionOffset, 0.0)
		else:
			self.destPoint = line.p2()


	def boundingRect(self):
		"""
		Hit box assistance.  Only let the user click on the tip of the line.
		"""
		if not self.source:  # or not self.dest:
			return QtCore.QRectF()
		penWidth = 1
		extra = (penWidth + self.arrowSize) / 2.0
		return QtCore.QRectF(self.sourcePoint,
							 QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
										   self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)


	def shape(self):
		"""
		The QT shape function.
		"""
		# Setup and stroke the line
		path = QtGui.QPainterPath(self.sourcePoint)
		path.lineTo(self.destPoint)
		stroker = QtGui.QPainterPathStroker()
		stroker.setWidth(2)
		stroked = stroker.createStroke(path)
		# Add a square at the tip
		stroked.addRect(self.destPoint.x()-10, self.destPoint.y()-10, 20, 20)
		return stroked
		

	def paint(self, painter, option, widget):
		"""
		Draw a line with an arrow at the end.
		"""
		if not self.source:  # or not self.dest:
			return

		# Draw the line
		line = QtCore.QLineF(self.sourcePoint, self.destPoint)
		if line.length() == 0.0:
			return
		painter.setPen(QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
		painter.drawLine(line)

		# Draw the arrows if there's enough room.
		angle = math.acos(line.dx() / line.length())
		if line.dy() >= 0:
			angle = DrawEdge.TwoPi - angle
		destArrowP1 = self.destPoint + QtCore.QPointF(math.sin(angle - math.pi / 3) * self.arrowSize,
													  math.cos(angle - math.pi / 3) * self.arrowSize)
		destArrowP2 = self.destPoint + QtCore.QPointF(math.sin(angle - math.pi + math.pi / 3) * self.arrowSize,
													  math.cos(angle - math.pi + math.pi / 3) * self.arrowSize)
		painter.setBrush(QtCore.Qt.white)
		painter.drawPolygon(QtGui.QPolygonF([line.p2(), destArrowP1, destArrowP2]))


	def mousePressEvent(self, event):
		"""
		Accept left-button clicks to drag the arrow.
		"""
		event.accept()
		self.dragging = True
		#QtGui.QGraphicsItem.mousePressEvent(self, event)


	def mouseMoveEvent(self, event):
		"""
		Node head dragging.
		"""
		if self.dragging:
			self.mouseMoved = True
			self.floatingDestinationPoint = event.scenePos()
			if self.destDrawNode():
				# Disconnect an edge from a node
				preSnap = self.scene().dag.snapshot(nodeMetaDict=self.scene().nodeMetaDict(), connectionMetaDict=self.scene().connectionMetaDict())
				
				self.destDrawNode().removeDrawEdge(self)
				self.scene().nodesDisconnected.emit(self.sourceDrawNode().dagNode, self.destDrawNode().dagNode)
				self.setDestDrawNode(None)

				currentSnap = self.scene().dag.snapshot(nodeMetaDict=self.scene().nodeMetaDict(), connectionMetaDict=self.scene().connectionMetaDict())
				self.scene().undoStack().push(depends_undo_commands.DagAndSceneUndoCommand(preSnap, currentSnap, self.scene().dag, self.scene()))
			self.adjust()
			# TODO: Hoover-color nodes as potential targets
		QtGui.QGraphicsItem.mouseMoveEvent(self, event)


	def mouseReleaseEvent(self, event):
		"""
		Dropping the connection onto a node connects it to the node and emits 
		an appropriate signal.  Dropping the connection into space deletes the
		connection.
		"""
		if self.dragging and self.mouseMoved:
			self.dragging = False
			
			# A little weird - seems to be necessary when passing mouse control from the nub to here
			self.ungrabMouse()
			
			# Hits?
			nodes = [n for n in self.scene().items(self.floatingDestinationPoint) if type(n) == DrawNode]
			if nodes:
				topHitNode = nodes[0]
				duplicatingConnection = self.sourceDrawNode().dagNode in self.scene().dag.nodeConnectionsIn(topHitNode.dagNode)
				if topHitNode is not self.sourceDrawNode() and not duplicatingConnection:
					# Connect an edge to a node
					preSnap = self.scene().dag.snapshot(nodeMetaDict=self.scene().nodeMetaDict(), connectionMetaDict=self.scene().connectionMetaDict())
					
					self.setDestDrawNode(topHitNode)
					self.dest.addDrawEdge(self)
					self.horizontalConnectionOffset = (event.pos() - self.mapFromItem(self.dest, 0, 0)).x()
					self.scene().nodesConnected.emit(self.sourceDrawNode().dagNode, self.destDrawNode().dagNode)
					self.adjust()

					currentSnap = self.scene().dag.snapshot(nodeMetaDict=self.scene().nodeMetaDict(), connectionMetaDict=self.scene().connectionMetaDict())
					self.scene().undoStack().push(depends_undo_commands.DagAndSceneUndoCommand(preSnap, currentSnap, self.scene().dag, self.scene()))
					return QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

			# No hits?  Delete yourself (You have no chance to win!)
			self.sourceDrawNode().removeDrawEdge(self)
			self.scene().removeItem(self)
		
		self.mouseMoved = False
		QtGui.QGraphicsItem.mouseReleaseEvent(self, event)


###############################################################################
###############################################################################
class DrawGroupBox(QtGui.QGraphicsItem):
	"""
	A simple box that draws around groups of DrawNodes.  Denotes which nodes
	are grouped together.
	"""
	
	Type = QtGui.QGraphicsItem.UserType + 4
	
	
	def __init__(self, initialBounds=QtCore.QRectF(), name=""):
		"""
		"""
		QtGui.QGraphicsItem.__init__(self)
		self.name = name
		self.bounds = initialBounds
		self.setZValue(-3)


	def type(self):
		"""
		Assistance for the QT windowing toolkit.
		"""
		return DrawGroupBox.Type


	def boundingRect(self):
		"""
		Hit box assistance.
		"""
		return self.bounds


	def paint(self, painter, option, widget):
		"""
		Simply draw a grey box behind the nodes it encompasses.
		"""
		# TODO: This box is currently not dynamically-sizable.  Fix!
		painter.setBrush(QtGui.QColor(62, 62, 62))
		painter.setPen(QtCore.Qt.NoPen)
		painter.drawRect(self.bounds)
		

###############################################################################
###############################################################################
class SceneWidget(QtGui.QGraphicsScene):
	"""
	The QGraphicsScene that contains the contents of a given dependency graph.
	"""
	
	# Signals
	nodesDisconnected = QtCore.Signal(depends_node.DagNode, depends_node.DagNode)
	nodesConnected = QtCore.Signal(depends_node.DagNode, depends_node.DagNode)

	def __init__(self, parent=None):
		"""
		"""
		QtGui.QGraphicsScene.__init__(self, parent)

		# Call setDag() when setting the dag to make sure everything is cleaned up properly
		self.dag = None
		
		# The lists of highlight nodes and their matching intensities.
		self.highlightNodes = list()
		self.highlightIntensities = list()


	def undoStack(self):
		"""
		An accessor to the application's global undo stack, guaranteed to be created
		by the time it's needed.
		"""
		return self.parent().parent().undoStack


	def drawNodes(self):
		"""
		Returns a list of all drawNodes present in the scene.
		"""
		nodes = list()
		for item in self.items():
			if type(item).__name__ == 'DrawNode':
				nodes.append(item)
		return nodes
	

	def drawNode(self, dagNode):
		"""
		Returns the given dag node's draw node (or None if it doesn't exist in
		the scene).
		"""
		for item in self.items():
			if type(item).__name__ != 'DrawNode':
				continue
			if item.dagNode == dagNode:
				return item
		return None
		

	def drawEdges(self):
		"""
		Return a list of all draw edges in the scene.
		"""
		edges = list()
		for item in self.items():
			if type(item).__name__ == 'DrawEdge':
				edges.append(item)
		return edges


	def drawEdge(self, fromDrawNode, toDrawNode):
		"""
		Returns a drawEdge that links a given draw node to another given draw
		node.
		"""
		for item in self.items():
			if type(item).__name__ != 'DrawEdge':
				continue
			if item.source == fromDrawNode and item.dest == toDrawNode:
				return item
		return None


	def setDag(self, dag):
		"""
		Sets the current dependency graph and refreshes the scene.
		"""
		self.clear()
		self.dag = dag
	
	
	def addExistingDagNode(self, dagNode, position):
		"""
		Adds a new draw node for a given dag node at a given position.
		"""
		newNode = DrawNode(dagNode)
		self.addItem(newNode)
		newNode.setPos(position)
		return newNode
	

	def addExistingConnection(self, fromDagNode, toDagNode):
		"""
		Adds a new draw edge for given from and to dag nodes.
		"""
		fromDrawNode = self.drawNode(fromDagNode)
		toDrawNode = self.drawNode(toDagNode)
		if not fromDrawNode:
			raise RuntimeError("Attempting to connect node %s which is not yet registered to QGraphicsScene." % fromDagNode.name)
		if not toDrawNode:
			raise RuntimeError("Attempting to connect node %s which is not yet registered to QGraphicsScene." % toDagNode.name)
		newDrawEdge = DrawEdge(fromDrawNode, toDrawNode)
		self.addItem(newDrawEdge)
		return newDrawEdge


	def addExistingGroupBox(self, name, groupDagNodeList):
		"""
		Add a group box from a given list of dag nodes & names it with a string.
		"""
		drawNodes = [self.drawNode(dn) for dn in groupDagNodeList]
		bounds = QtCore.QRectF()
		for drawNode in drawNodes:
			bounds = bounds.united(drawNode.sceneBoundingRect())
		adjust = bounds.width() if bounds.width() > bounds.height() else bounds.height()
		adjust *= 0.05
		bounds.adjust(-adjust, -adjust, adjust, adjust)
		newGroupBox = DrawGroupBox(bounds, name)
		self.addItem(newGroupBox)


	def removeExistingGroupBox(self, name):
		"""
		Removes a group box with a given name.
		"""
		boxes = [n for n in self.items() if type(n) == DrawGroupBox]
		for box in boxes:
			if box.name == name:
				self.removeItem(box)
				return
		raise RuntimeError("Group box named %s does not appear to exist in the QGraphicsScene." % name)
	

	def refreshDrawNodes(self, dagNodes):
		"""
		Refresh the draw nodes representing a given list of dag nodes.
		"""
		for drawNode in [self.drawNode(n) for n in dagNodes]:
			drawNode.update()
	

	def setHighlightNodes(self, drawNodes, intensities=None):
		"""
		Set which nodes are highlighted by giving a list of drawNodes and an
		optional list of intensities.
		"""
		self.highlightIntensities = intensities
		oldHighlightNodes = self.highlightNodes
		self.highlightNodes = drawNodes
		for drawNode in drawNodes+oldHighlightNodes:
			drawNode.update()
	
	
	def setCascadingHighlightNodesFromOrderedDependencies(self, dagNodeOrigin):
		"""
		Recover a list of ordered dependencies for a given dag node, and 
		highlight each of the nodes it depends on.
		"""
		highlightDrawNodesDarkToLight = [self.drawNode(n) for n in self.dag.orderedNodeDependenciesAt(dagNodeOrigin, onlyUnfulfilled=False)]
		intensities = list()
		nodeCount = len(highlightDrawNodesDarkToLight)
		if nodeCount > 1:
			for i in range(nodeCount):
				intensities.append(0.65 + (0.35 * float(i)/float(nodeCount-1)))
		else:
			intensities = [1.0]
		self.setHighlightNodes(highlightDrawNodesDarkToLight, intensities)
	

	def mousePressEvent(self, event):
		"""
		Stifles a rubber-band box when clicking on a node and moving it.
		"""
		# This allows an event to propagate without actually doing what it wanted to do 
		# in the first place (draw a rubber band box for all click-drags - including middle mouse)
		# (http://www.qtcentre.org/threads/36953-QGraphicsItem-deselected-on-contextMenuEvent)
		if event.button() != QtCore.Qt.LeftButton:
			event.accept()
			return
		QtGui.QGraphicsScene.mousePressEvent(self, event)
		
	
	def nodeMetaDict(self):
		"""
		Returns a dictionary containing meta information for each of the draw 
		nodes in the scene.
		"""
		nodeMetaDict = dict()
		nodes = [n for n in self.items() if type(n) == DrawNode]
		for n in nodes:
			nodeMetaDict[str(n.dagNode.uuid)] = dict()
			nodeMetaDict[str(n.dagNode.uuid)]['locationX'] = str(n.pos().x())
			nodeMetaDict[str(n.dagNode.uuid)]['locationY'] = str(n.pos().y())
		return nodeMetaDict


	def connectionMetaDict(self):
		"""
		Returns a dictionary containing meta information for each of the draw
		edges in the scene.
		"""
		connectionMetaDict = dict()
		connections = [n for n in self.items() if type(n) == DrawEdge]
		for c in connections:
			if not c.sourceDrawNode() or not c.destDrawNode():
				continue
			connectionString = "%s|%s" % (str(c.sourceDrawNode().dagNode.uuid), str(c.destDrawNode().dagNode.uuid))
			connectionMetaDict[connectionString] = dict()
			connectionMetaDict[connectionString]['horizontalConnectionOffset'] = str(c.horizontalConnectionOffset)
		return connectionMetaDict


	def restoreSnapshot(self, snapshotDict):
		"""
		Given a dictionary that contains dag information and meta information 
		for the dag, construct all draw objects and register them with the 
		current scene.
		"""
		# Clear out the drawnodes and connections, then add 'em all back in.
		selectedItems = self.selectedItems()
		self.blockSignals(True)
		for dn in self.drawNodes():
			self.removeItem(dn)
		for de in self.drawEdges():
			self.removeItem(de)
		for dagNode in self.dag.nodes():
			newNode = self.addExistingDagNode(dagNode, QtCore.QPointF(0,0))
			if selectedItems and dagNode in [x.dagNode for x in selectedItems]:
				newNode.setSelected(True)
		for connection in self.dag.connections():
			newDrawEdge = self.addExistingConnection(connection[1], connection[0])
		self.blockSignals(False)
		
		# DrawNodes get their locations set from this meta entry
		expectedNodeMeta = snapshotDict["NODE_META"]
		if expectedNodeMeta:
			for dagNode in self.dag.nodes():
				drawNode = self.drawNode(dagNode)
				nodeMeta = expectedNodeMeta[str(dagNode.uuid)]
				if 'locationX' in nodeMeta:
					locationX = float(nodeMeta['locationX'])
				if 'locationY' in nodeMeta:
					locationY = float(nodeMeta['locationY'])
				drawNode.setPos(QtCore.QPointF(locationX, locationY))
				
		# DrawEdges	get their insertion points set here
		expectedConnectionMeta = snapshotDict["CONNECTION_META"]
		if expectedConnectionMeta:
			for connection in self.dag.connections():
				connectionIdString = "%s|%s" % (str(connection[1].uuid), str(connection[0].uuid))
				connectionMeta = expectedConnectionMeta[connectionIdString]
				if 'horizontalConnectionOffset' in connectionMeta:
					# TODO: This code is a little verbose...
					drawEdge = self.drawEdge(self.drawNode(self.dag.node(nUUID=connection[1].uuid)), 
											 self.drawNode(self.dag.node(nUUID=connection[0].uuid)))
					drawEdge.horizontalConnectionOffset = float(connectionMeta['horizontalConnectionOffset'])
					drawEdge.adjust()
		

###############################################################################
###############################################################################
class GraphicsViewWidget(QtGui.QGraphicsView):
	"""
	The QGraphicsView into a QGraphicsScene it owns.  This object handles the
	mouse and board behavior of the dependency graph inside the view.
	"""
	
	# Signals
	createNode = QtCore.Signal(type, QtCore.QPointF)

	def __init__(self, parent=None):
		"""
		"""
		QtGui.QGraphicsView.__init__(self, parent)

		# Setup our own Scene Widget and assign it to the View.
		scene = SceneWidget(self)
		scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
		scene.setSceneRect(-20000, -20000, 40000, 40000)
		self.setScene(scene)
		
		# Mouse Interaction
		self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
		self.setRenderHint(QtGui.QPainter.Antialiasing)
		self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

		# Hide the scroll bars
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		# Window properties
		self.setWindowTitle(self.tr("Depends"))
		self.setMinimumSize(200, 200)
		self.scale(1.0, 1.0)
		
		# Context menu hookups
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)
		
		self.boxing = False
		self.modifierBoxOrigin = None
		self.modifierBox = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)


	def centerCoordinates(self):
		"""
		Returns a QPoint containing the scene location the center of this view 
		is pointing at.
		"""
		topLeft = QtCore.QPointF(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
		topLeft += self.geometry().center()
		return topLeft
		
		
	def frameBounds(self, bounds):
		"""
		Frames a given bounding rectangle within the viewport.
		"""
		if bounds.isEmpty():
			return
		widthAdjust = bounds.width() * 0.2
		heightAdjust = bounds.height() * 0.2
		bounds.adjust(-widthAdjust, -heightAdjust, widthAdjust, heightAdjust)
		self.fitInView(bounds, QtCore.Qt.KeepAspectRatio)		
		
		
	def showContextMenu(self, menuLocation):
		"""
		Pop up a node creation context menu at a given location.
		"""
		contextMenu = QtGui.QMenu()
		menuActions = self.parent().createCreateMenuActions()
		for action in menuActions:
			action.setData((action.data()[0], self.mapToScene(menuLocation)))
			contextMenu.addAction(action)
		contextMenu.exec_(self.mapToGlobal(menuLocation))
		
	
	def keyPressEvent(self, event):
		"""
		Stifles autorepeat and handles a few shortcut keys that aren't 
		registered as functions in the main window.
		"""
		# This widget will never process auto-repeating keypresses so ignore 'em all
		if event.isAutoRepeat():
			return
		
		# Frame selected/all items
		if event.key() == QtCore.Qt.Key_F:
			itemList = list()
			if self.scene().selectedItems():
				itemList = self.scene().selectedItems()
			else:
				itemList = self.scene().items()
			bounds = QtCore.QRectF()
			for item in itemList:
				bounds |= item.sceneBoundingRect()
			self.frameBounds(bounds)
			
		# Highlight each node upstream that affects the selected node
		elif event.key() == QtCore.Qt.Key_Space:
			sel = self.scene().selectedItems()
			if len(sel) != 1:
				return
			self.scene().setCascadingHighlightNodesFromOrderedDependencies(sel[0].dagNode)


	def keyReleaseEvent(self, event):
		"""
		Stifle auto-repeats and handle letting go of the space bar.
		"""
		# Ignore auto-repeats
		if event.isAutoRepeat():
			return

		# Clear the highlight list if you just released the space bar
		if event.key() == QtCore.Qt.Key_Space:
			self.scene().setHighlightNodes([], intensities=None)


	def mousePressEvent(self, event):
		"""
		Special handling is needed for a drag-box that toggles selected 
		elements with the CTRL button.
		"""
		# Handle CTRL+MouseClick box behavior
		if event.modifiers() & QtCore.Qt.ControlModifier:
			itemUnderMouse = self.itemAt(event.pos().x(), event.pos().y())
			if not itemUnderMouse:
				self.modifierBoxOrigin = event.pos()
				self.boxing = True
				event.accept()
				return
		QtGui.QGraphicsView.mousePressEvent(self, event)


	def mouseMoveEvent(self, event):
		"""
		Panning the viewport around and CTRL+mouse drag behavior.
		"""
		# Panning
		if event.buttons() & QtCore.Qt.MiddleButton:
			delta = event.pos() - self.lastMousePos
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
			self.lastMousePos = event.pos()
		else:
			self.lastMousePos = event.pos()
		
		# Handle Modifier+MouseClick box behavior
		if event.buttons() & QtCore.Qt.LeftButton and event.modifiers() & QtCore.Qt.ControlModifier:
			if self.boxing:
				self.modifierBox.setGeometry(QtCore.QRect(self.modifierBoxOrigin, event.pos()).normalized())
				self.modifierBox.show()
				event.accept()
				return

		QtGui.QGraphicsView.mouseMoveEvent(self, event)


	def mouseReleaseEvent(self, event):
		"""
		The final piece of the CTRL+drag box puzzle.
		"""
		# Handle Modifier+MouseClick box behavior
		if self.boxing:
			# Blocking the scene's signals insures only a single selectionChanged
			# gets emitted at the very end.  This was necessary since the way I
			# have written the property widget appears to freak out when refreshing
			# twice instantaneously (see MainWindow's constructor for additional details).
			nodesInHitBox = [x for x in self.items(QtCore.QRect(self.modifierBoxOrigin, event.pos()).normalized()) if type(x) is DrawNode]
			self.scene().blockSignals(True)
			for drawNode in nodesInHitBox:
				drawNode.setSelected(not drawNode.isSelected())
			self.scene().blockSignals(False)
			self.scene().selectionChanged.emit()
			self.modifierBox.hide()
			self.boxing = False
		QtGui.QGraphicsView.mouseReleaseEvent(self, event)


	def wheelEvent(self, event):
		"""
		Zooming.
		"""
		self.scaleView(math.pow(2.0, event.delta() / 240.0))


	def drawBackground(self, painter, rect):
		"""
		Filling.
		"""
		sceneRect = self.sceneRect()
		painter.fillRect(rect.intersect(sceneRect), QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
		painter.drawRect(sceneRect)


	def scaleView(self, scaleFactor):
		"""
		Zoom helper function.
		"""
		factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
		if factor < 0.07 or factor > 100:
			return
		self.scale(scaleFactor, scaleFactor)
