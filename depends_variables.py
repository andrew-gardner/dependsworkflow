#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import os
import re


"""
A holder for the global workflow variable dictionary (variableSubstitutions)
and functions to manipulate it.
"""


###########################################################################
###########################################################################
# A "static" dict of environment variables, each containing a tuple with 
# the variable definition string and a "Read Only" boolean
# TODO: It's likely someone should own this since it would enable multiple
#       projects to be loaded at once, but this is a non-issue for now.
variableSubstitutions = dict()


###########################################################################
## Variable substitution
###########################################################################
def add(variable):
	"""
	Add a variable that doesn't exist in variableSubstitutions.
	"""
	if variable not in variableSubstitutions:
		variableSubstitutions.update({variable : ("", False)})
	else:
		raise RuntimeError("Variable %s already exists in substitution dictionary." % variable)
	
	
def remove(variable):
	"""
	Remove a variable that exists in variableSubstitutions.
	"""
	if variable in variableSubstitutions:
		variableSubstitutions.pop(variable, None)
	else:
		raise RuntimeError("Variable %s does not exist in substitution dictionary." % variable)
	
	
def setx(variable, value, readOnly=False):
	"""
	Set a variable that exists in variableSubstituions to a given value.
	Can also set the "read only" bit while doing so.  (The function is named 
	'setx' to avoid conflicts with the built-in keyword 'set')
	"""
	if variable in variableSubstitutions:
		variableSubstitutions.update({variable : (value, readOnly)})
	else:
		raise RuntimeError("Variable %s does not exist in substitution dictionary." % variable)


def names():
	"""
	Return a list of all variables present.
	"""
	return list(variableSubstitutions.keys())


def value(variable):
	"""
	Return a variable's value if it exists.
	"""
	if variable in variableSubstitutions:
		return variableSubstitutions[variable][0]
	else:
		raise RuntimeError("Variable %s does not exist in substitution dictionary." % variable)


def changeableList():
	"""
	Returns a list of dictionaries containing the variable name and its value for all
	variables that aren't read only.
	"""
	variables = list()
	for v in variableSubstitutions:
		if not variableSubstitutions[v][1]:
			variables.append({"NAME":v,
							  "VALUE":variableSubstitutions[v][0]})
	return variables
	

def present(incomingString):
	"""
	Return a tuple containing a list of all single-dollar and a list of all 
	double-dollar variables present in the given string.
	"""
	# Build a list of single-dollar-signed variables without duplicates
	presentSingleList = list()
	singleDollars = re.compile(r"((?<!\\)(?<!\$)\${1}(?!\$)[A-Z0-9_]*)")
	for match in singleDollars.finditer(incomingString):
		variableName = match.group()[1:]
		presentSingleList.append(variableName)
	presentSingleList = list(set(presentSingleList))

	# Build a list of double-dollar-signed variables without duplicates
	presentDoubleList = list()
	doubleDollars = re.compile(r"((?<!\\)(?<!\$)\${2}(?!\$)[A-Z0-9_]*)")
	for match in doubleDollars.finditer(incomingString):
		variableName = match.group()[2:]
		presentDoubleList.append(variableName)
	presentDoubleList = list(set(presentDoubleList))

	return (presentSingleList, presentDoubleList)
	

def substitute(incomingString):
	"""
	Find and substitute all variables present in a given string.
	Returns a new string.
	"""
	newString = incomingString

	# Replace all the single-dollar-signed strings with values from our variableSubstitution dictionary
	singleDollars = re.compile(r"((?<!\\)(?<!\$)\${1}(?!\$)[A-Z0-9_]*)")
	for match in singleDollars.finditer(newString):
		variableName = match.group()[1:]
		if variableName in variableSubstitutions:
			substitution = variableSubstitutions[variableName][0]
			newString = newString[:match.start()] + substitution + newString[match.end():]
			
	# Replace all the double-dollar-signed strings with values from our variableSubstitution dictionary
	doubleDollars = re.compile(r"((?<!\\)(?<!\$)\${2}(?!\$)[A-Z0-9_]*)")
	for match in doubleDollars.finditer(newString):
		variableName = match.group()[2:]
		if variableName in os.environ:
			substitution = os.environ[variableName]
			newString = newString[:match.start()] + substitution + newString[match.end():]

	newString = newString.replace('\$', '$')
	return newString
