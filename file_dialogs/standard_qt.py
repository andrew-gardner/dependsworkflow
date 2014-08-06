#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

from PySide import QtCore, QtGui, QtOpenGL

import depends_file_dialog


"""
This is an example plugin for replacing the file dialogs in Depends.
It runs a standard QT file dialog that lets the user choose their file.
"""


################################################################################
################################################################################
class QtFileDialog(depends_file_dialog.FileDialog):
	"""
	"""
	def __init__(self):
		depends_file_dialog.FileDialog.__init__(self)


	def name(self):
		return "Standard Qt File Dialog"


	def browse(self):
		"""
		Open a Qt file dialog and return the chosen file (or None).
		"""
		return QtGui.QFileDialog.getOpenFileName()[0]
