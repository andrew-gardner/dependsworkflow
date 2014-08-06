#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import depends_util


"""
A class and collection of functions that assist in loading file dialog plugins.
Creating one's own file dialog consists of inheriting from the FileDialog 
class, setting a unique name, and overloading the browse function.
"""


###############################################################################
## Utility
###############################################################################
def fileDialogTypes():
	"""
	Return a list of available file dialog types.
	"""
	return FileDialog.__subclasses__()


def fileDialogOfType(typeName):
	"""
	"""
	for fdt in fileDialogTypes():
		if fdt().name() == typeName:
			return fdt()
	raise RuntimeError("Custom file dialog of type '%s' is not loaded in this session." % typeName)
	return None


###############################################################################
## FileDialog base class
###############################################################################
class FileDialog(object):
	"""
	A simple parent class that new file dialog plugins can inherit from.
	Each method must be overridden with unique code in order to make the plugin
	accessible to the Depends plugin system.
	"""
	
	def __init__(self):
		pass


	def name(self):
		return "Empty Base File Dialog"


	def browse(self):
		"""
		Open a file dialog and return the chosen file's pathname
		or None if no file is specified.
		"""
		raise RuntimeError("Attempting to execute File Dialog base class.")


######### FUNCTION TO IMPORT PLUGIN FILE DIALOGS INTO THIS NAMESPACE  #########
def loadChildFileDialogsFromPaths(pathList):
	"""
	Given a list of directories, import all classes that reside in modules in those
	directories into the node namespace. TODO better docs
	"""
	for path in pathList:
		nodeClassDict = depends_util.allClassesOfInheritedTypeFromDir(path, FileDialog)
		for nc in nodeClassDict:
			globals()[nc] = nodeClassDict[nc]
