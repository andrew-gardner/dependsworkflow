#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import depends_node
import depends_data_packet

###############################################################################
## Sample nodes used for demonstration purposes
###############################################################################
class DagNodeLs(depends_node.DagNode):
	"""
	"""
	def _defineInputs(self):
		"""
		"""
		return []
	
		
	def _defineOutputs(self):
		"""
		"""
		return [depends_node.DagNodeOutput('File', depends_data_packet.DataPacketTextFile)] 


	def _defineAttributes(self):
		"""
		"""
		docPath = ("A path to do a unix 'ls' command on.")
		docLong = ("Add the -la argument to the ls command.")
		return [depends_node.DagNodeAttribute('listPath', "", docString=docPath),
		      depends_node.DagNodeAttribute('long', "True", docString=docLong)] 


	def executeList(self, dataPacketDict, splitOperations=False):
		"""
		Returns a list of arguments that executes a command that reduces 
		lightprobes in a volume.
		"""
		appList = list()

		outputTextFile = self.outputFramespec('File', 'filename')
		appList.extend(['ls'])
		if self.attributeValue('long').lower() != "false":
		    appList.extend(['-la'])
		appList.extend(['>', outputTextFile.filename])
		return appList


################################################################################
################################################################################
class DagNodeAwk(depends_node.DagNode):
	"""
	"""
	def _defineInputs(self):
		"""
		"""
		doc = ("A file or files to run awk on.")
		return [depends_node.DagNodeInput('File', depends_data_packet.DataPacketTextFile, True, docString=doc)]
	
		
	def _defineOutputs(self):
		"""
		"""
		return [depends_node.DagNodeOutput('File', depends_data_packet.DataPacketTextFile)] 


	def _defineAttributes(self):
		"""
		"""
		docCommand = ("The awk command(s) to execute.")
		return [depends_node.DagNodeAttribute('command', "", docString=docCommand)] 


	def executeList(self, dataPacketDict, splitOperations=False):
		"""
		Returns a list of arguments that executes a command that reduces 
		lightprobes in a volume.
		"""
		appList = list()

		inputFileDatapacket = dataPacketDict[self.inputNamed('File')]
		outputTextFile = self.outputFramespec('File', 'filename')
		appList.extend(['awk'])
		appList.extend(["'"+self.attributeValue('command')+"'"])
		appList.extend([inputFileDatapacket.fileDescriptorNamed('filename').filename])
		appList.extend(['>', outputTextFile.filename])
		return appList


