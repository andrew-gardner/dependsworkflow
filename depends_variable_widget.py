#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

from PySide import QtCore, QtGui


"""
A QT graphics widget that displays a table containing all the local variables 
for the given workflow.  All variables are editable except for read-only ones.
"""


###############################################################################
###############################################################################
class VariableWidget(QtGui.QWidget):
	"""
	An edit widget that shows a table of variables and allows the user to edit
	each one (save for read only variables).
	"""

	# Signals
	addVariable = QtCore.Signal(str)
	removeVariable = QtCore.Signal(str)
	setVariable = QtCore.Signal(str, str)

	DATA_FIELD = 0
	DEFINITION_FIELD = 1

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
		self.tableWidget.setColumnCount(2)
		self.tableWidget.setHorizontalHeaderLabels(['Variable', 'Value'])
		self.tableWidget.horizontalHeader().resizeSection(0, 170)
		self.tableWidget.horizontalHeader().setStretchLastSection(True)
		self.tableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
		self.tableWidget.horizontalHeader().setHighlightSections(False)
		self.tableWidget.verticalHeader().hide()
		self.tableWidget.setFocusPolicy(QtCore.Qt.NoFocus)
		self.tableWidget.itemChanged.connect(self.signalRouter)
		# TODO: I would like the enter key to be accepted here as an edit trigger, but the centralWidget is hogging it right now...
		#self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.EditKeyPressed)
		self.mainLayout.addWidget(self.tableWidget)


	def signalRouter(self, item):
		"""
		Main routing function for variable changes.
		"""
		if item.tableType == self.DEFINITION_FIELD:
			if item.oldText != "":
				# If it's already in the dictionary, remove it
				self.removeVariable.emit(item.oldText)
			if item.text() != "":
				# If it's not there, set, and backup the old variable name
				self.addVariable.emit(item.text())
				item.oldText = item.text()
				self.setVariable.emit(item.text(), item.dataField.text())
		elif item.tableType == self.DATA_FIELD:
			if item.definitionField.text() != "":
				# If there is a valid variable definition, set away.
				self.setVariable.emit(item.definitionField.text(), item.text())
				
		# Add an extra row if necessary
		if self.tableWidget.item(self.tableWidget.rowCount()-1, 0).text() != "":
			self._insertBlankRowAtEnd()


	def _newRow(self, definition, data):
		"""
		Creates two new elements for this table & hooks them together so our
		signals work properly.  Initializes the definition and data colums with what's given.
		"""
		definitionField = QtGui.QTableWidgetItem(definition)
		definitionField.tableType = self.DEFINITION_FIELD
		definitionField.oldText = definitionField.text()
		dataField = QtGui.QTableWidgetItem(data)
		dataField.tableType = self.DATA_FIELD
		definitionField.dataField = dataField
		dataField.definitionField = definitionField
		return (definitionField, dataField)


	def _insertBlankRowAtEnd(self):
		"""
		Insert a blank row at the end of the table.
		"""
		(definitionField, dataField) = self._newRow("", "")
		self.tableWidget.insertRow(self.tableWidget.rowCount())
		self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0, definitionField)
		self.tableWidget.setItem(self.tableWidget.rowCount()-1, 1, dataField)
		

	def rebuild(self, variableDict):
		"""
		Completely rebuild the contents of the widget.
		"""
		# Only refresh once at the very end
		self.tableWidget.blockSignals(True)
		
		# Count the number of rows
		rowCount = len(variableDict)
		self.tableWidget.setRowCount(rowCount)

		index = 0
		for variable in variableDict:
			(definitionField, dataField) = self._newRow(variable, variableDict[variable][0])
			self.tableWidget.setItem(index, 0, definitionField)
			self.tableWidget.setItem(index, 1, dataField)

			# Set to be read-only if it's a read-only variable.
			if variableDict[variable][1] is True:
				flags = self.tableWidget.item(index, 0).flags()
				#flags &= ~(QtCore.Qt.ItemIsSelectable)
				flags &= ~(QtCore.Qt.ItemIsEditable)
				self.tableWidget.item(index, 0).setFlags(flags)
				flags = self.tableWidget.item(index, 1).flags()
				#flags &= ~(QtCore.Qt.ItemIsSelectable)
				flags &= ~(QtCore.Qt.ItemIsEditable)
				self.tableWidget.item(index, 1).setFlags(flags)
				#self.tableWidget.setStyleSheet("QTableWidget::item{ background-color: rgb(240, 240, 240); }")
			index += 1

		self._insertBlankRowAtEnd()
		self.tableWidget.blockSignals(False)
		self.repaint()
