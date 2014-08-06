#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import os
import re
import imp
import sys
import glob
import inspect

import depends_node


"""
A utility module for the Depends software.  Much of the functionality relates
to plugin loading, but string manipulation, software restarting, and file
sequence manipulation are all present as well.
"""


###############################################################################
## Utility
###############################################################################
def allClassChildren(inputClass):
	"""
	Returns a list of all a class' children and its childrens' children, using
	a while loop as its recursion method.
	"""
	subclasses = set()
	work = [inputClass]
	while work:
		parent = work.pop()
		for child in parent.__subclasses__():
			if child not in subclasses:
				subclasses.add(child)
				work.append(child)
	return list(subclasses)


def classTypeNamedFromModule(typeString, moduleName):
	"""
	Creates a node of a given type (string) from a loaded module specified by name.
	"""
	moduleMembers = inspect.getmembers(globals()[moduleName])
	classIndex = [i for i, t in enumerate(moduleMembers) if t[0] == typeString][0]
	defaultConstructedNode = (moduleMembers[classIndex][1])()
	return defaultConstructedNode


def allClassesOfInheritedTypeFromDir(fromDir, classType):
	"""
	Given a directory on-disk, dig through each .py module, looking for classes
	that inherit from the given classType.  Return a dictionary with class
	names as keys and the class objects as values.
	"""
	returnDict = dict()
	fileList = glob.glob(os.path.join(fromDir, "*.py"))
	for filename in fileList:
		basename = os.path.basename(filename)
		basenameWithoutExtension = basename[:-3]
		try:
			foo = imp.load_source(basenameWithoutExtension, filename)
		except Exception, err:
			print "Module '%s' raised the following exception when trying to load." % (basenameWithoutExtension)
			print '    "%s"' % (str(err))
			print "Skipping..."
			continue
		for x in inspect.getmembers(foo):
			name = x[0]
			data = x[1]
			if type(data) is type and data in allClassChildren(classType):
				returnDict[name] = data
	return returnDict


def namedFunctionFromPluginFile(filename, functionName):
	"""
	Load a Python module specified by its filename and return a function 
	matching the given function name.
	"""
	if not os.path.exists(filename):
		raise RuntimeError("Plugin file %s does not exist." % filename)
	try:
		basename = os.path.basename(filename)
		basenameWithoutExtension = basename[:-3]
		module = imp.load_source(basenameWithoutExtension, filename)
	except Exception, err:
		print "Module '%s' raised the following exception when trying to load." % (basenameWithoutExtension)
		print '    "%s"' % (str(err))
		print "Plugin is not loaded."
		return None
	for x in inspect.getmembers(module):
		name = x[0]
		function = x[1]
		if name == functionName:
			return function
	return None


def dagSnapshotDiff(snapshotLeft, snapshotRight):
	"""
	A function that detects differences in the "important" parts of a
	DAG snapshot.  Returns a tuple containing a list of modified nodes
	and a list of modified edges).
	"""
	modifiedNodes = list()
	if snapshotLeft['NODES'] != snapshotRight['NODES']:
		for node in snapshotRight['NODES']:
			if node not in snapshotLeft['NODES']:
				modifiedNodes.append(node['NAME'])
		for node in snapshotLeft['NODES']:
			if node not in snapshotRight['NODES']:
				modifiedNodes.append(node['NAME'])
	modifiedEdges = list()
	if snapshotLeft['EDGES'] != snapshotRight['EDGES']:
		for edge in snapshotRight['EDGES']:
			if edge not in snapshotLeft['EDGES']:
				modifiedEdges.append((edge['FROM'], edge['TO']))
		for edge in snapshotLeft['EDGES']:
			if edge not in snapshotRight['EDGES']:
				modifiedEdges.append((edge['FROM'], edge['TO']))
	return (modifiedNodes, modifiedEdges)


def restartProgram(newArgs):
	"""
	Restarts the current program.
	"""
	python = sys.executable
	os.execl(python, python, *newArgs)


def nextFilenameVersion(filename):
	"""
	Given an existing filename, return a string representing the next 'version' of that
	filename.  All versions are presumed to be 3-zero padded, and if the version doesn't
	yet exist, one will be added.
	"""
	(path, baseName) = os.path.split(filename)
	splitBase = baseName.split('.')

	# VersionIndex identifies which segment of the split string [should] contains a version number
	versionIndex = -1
	if len(splitBase) > 1:
		versionIndex = -2
	
	# Ignore all trailing ".[#+]."s
	for i in range(len(splitBase)):
		minusIndex = -(i+1)
		if all(p == '#' for p in splitBase[minusIndex]):
			versionIndex = minusIndex-1
	
	# If there are still #s or _s hanging onto the end of the versionIndex string, remove them for now
	poundCount = 0
	if splitBase[versionIndex].find('#') != -1:
		poundCount = len(splitBase[versionIndex]) - splitBase[versionIndex].find('#')
		splitBase[versionIndex] = splitBase[versionIndex][:-poundCount]
	trailingUnderscores = len(splitBase[versionIndex]) - len(splitBase[versionIndex].rstrip('_'))
	if trailingUnderscores:
		splitBase[versionIndex] = splitBase[versionIndex][:-trailingUnderscores]
	
	# Match all ending digits and strip them off
	versionNumber = 0
	numberString = '000'
	matchObj = re.match(r'.*?(\d+)$', splitBase[versionIndex])
	if matchObj:
		numberString = matchObj.group(1)
		versionNumber = int(numberString)
		splitBase[versionIndex] = splitBase[versionIndex][:-len(numberString)]
	
	# Increment and attach the number string to the end again
	versionNumber += 1
	splitBase[versionIndex] += "%s" % (str(versionNumber).zfill(len(numberString)))
	if poundCount:
		splitBase[versionIndex] += '_'
		splitBase[versionIndex] += "_"*(trailingUnderscores-1)
		splitBase[versionIndex] += "#"*poundCount
	
	newBase = '.'.join(splitBase)
	return os.path.join(path, newBase)
	
	
def generateUniqueNameSimiarToExisting(prefix, existingNames):
	"""
	Given a name prefix known to exist in a list of existing names, figure out
	a new name that doesn't exist in the existing list yet is similar to the
	rest.  This is primarily accomplished by appending a 2-zero-padded number 
	to the end of the prefix.
	"""
	nameIndices = list()
	for en in existingNames:
		numberLop = en[len(prefix):]
		nameIndices.append(int(numberLop))
	nameIndices.sort()
	if not nameIndices or min(nameIndices) != 1:
		return "%s%02d" % (prefix, 1)
	for i in range(len(nameIndices)):
		if len(nameIndices) == i+1:
			return "%s%02d" % (prefix, nameIndices[i]+1)
		if nameIndices[i+1] != nameIndices[i]+1:
			return "%s%02d" % (prefix, nameIndices[i]+1)
	

class framespec(object):
	"""
	This class defines a sequence of files on disk as a filename containing 
	one or more "#" characters, a start frame integer, and an end frame integer.
	It is valid to set a start frame or end frame to "None".  Escaping #s allows
	them to pass through as # characters.
	This is done in the "Nuke" style, meaning the following substitutions will
	occur:
		FILENAME        FRAME NUM     RESULT
		foo.#.txt       1             foo.1.txt
		foo.##.txt      1             foo.01.txt
		foo.#.txt       100           foo.100.txt
		foo\#.#.txt     5             foo#.5.txt
	"""
	
	def __init__(self, fileString, fileRange):
		"""
		"""
		self.filename = fileString
		self.startFrame = None
		self.endFrame = None
		
		if fileRange:
			self.setFramerange(*fileRange)


	def setFramerange(self, startFrame, endFrame):
		"""
		Set the start and end frames given two strings or ints.
		"""
		self.startFrame = int(startFrame) if startFrame else None
		self.endFrame = int(endFrame) if endFrame else None
		

	def frames(self):
		"""
		Return a complete list of filenames this framespec object represents.
		"""
		frameList = list()
		if self.startFrame is None or self.endFrame is None:
			return [self.filename]
		for i in range(self.startFrame, self.endFrame+1):
			frameList.append(self.replaceFrameSymbols(self.filename, i))
		return frameList


	@staticmethod
	def hasFrameSymbols(checkString):
		"""
		Return a boolean stating whether or not the given string contains 
		known frame symbols ('#').
		"""
		matchObj = re.finditer(r'((?<!\\)\#+)', checkString)
		i = next(matchObj, None)
		if not i:
			return False
		return True
		

	@staticmethod
	def replaceFrameSymbols(replaceString, frameNumber):
		"""
		This function replaces Nuke-style frame sequence markers in a string 
		with a given frame number.  Meaning, any string of # characters gets 
		padded to the number of #s.  Escaped #s with a backslash (\#) will be 
		replaced with a single # character in this function.
		"""
		matchObj = re.finditer(r'((?<!\\)\#+)', replaceString)
		i = next(matchObj, None)
		while i:
			padString = "%s" % str(frameNumber).zfill(len(i.group(0)))
			replaceString = replaceString[:i.start()] + padString + replaceString[i.end():]
			matchObj = re.finditer(r'((?<!\\)\#+)', replaceString)
			i = next(matchObj, None)
		replaceString = replaceString.replace('\#', '#')
		return replaceString
