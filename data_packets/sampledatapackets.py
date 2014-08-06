#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import depends_data_packet


"""
"""

###############################################################################
###############################################################################
class DataPacketTextFile(depends_data_packet.DataPacket):
	"""
	A simple text file.
	"""
	def __init__(self, sourceNode, sourceOutputName):
		depends_data_packet.DataPacket.__init__(self, sourceNode, sourceOutputName)
		self.filenames['filename'] = ""


