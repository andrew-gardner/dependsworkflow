#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import depends_node
import depends_data_packet


"""
"""


###############################################################################
## Nodes useful in the VCL
###############################################################################
class DagNodeLightprobeReduce(depends_node.DagNode):
    """
    """
    def _defineInputs(self):
        """
        """
        doc = ("A series of lightprobes to be reduced to a unique, new set.")
        return [depends_node.DagNodeInput('Lightprobe', depends_data_packet.DataPacketLightprobe, True, docString=doc)]
    
        
    def _defineOutputs(self):
        """
        """
        return [depends_node.DagNodeOutput('Lightprobe', depends_data_packet.DataPacketLightprobe)] 


    def _defineAttributes(self):
        """
        """
        doc = ("The resulting number of lightprobes.")
        return [depends_node.DagNodeAttribute('resultCount', "", docString=doc)] 


    def executeList(self, dataPacketDict, splitOperations=False):
        """
        Returns a list of arguments that executes a command that reduces 
        lightprobes in a volume.
        """
        # Simplifications
        inputLightprobeDp = dataPacketDict[self.inputNamed('Lightprobe')]
        inputLightprobes = inputLightprobeDp.fileDescriptorNamed('filename')
        inputTransforms = inputLightprobeDp.fileDescriptorNamed('transform')

        appList = list()

        outputImages = self.outputFramespec('Lightprobe', 'filename')
        outputTransforms = self.outputFramespec('Lightprobe', 'transform')
        appList.extend(['reduceLightprobes'])
        if inputLightprobes.startFrame:
            appList.extend(['-t %d-%d' % (inputLightprobes.startFrame, inputLightprobes.endFrame)])
        appList.extend(['-probe', inputLightprobes.filename])
        appList.extend(['-transform', inputTransforms.filename])
        appList.extend(['-resultCount', self.attributeValue('resultCount')])
        appList.extend(['-output', outputImages.filename])
        appList.extend(['-outputTransforms', outputImages.filename])
        return appList


###############################################################################
###############################################################################
class DagNodeStructureFromMotion(depends_node.DagNode):
    """
    """
    def _defineInputs(self):
        """
        """
        doc = ("A sequence of images to generate geometry from.")
        return [depends_node.DagNodeInput('ImageTypes', depends_data_packet.DataPacketImage, True, docString=doc)]
    
        
    def _defineOutputs(self):
        """
        """
        return [depends_node.DagNodeOutput('Pointcloud', depends_data_packet.DataPacketPointcloud)] 
        
    
    def _defineAttributes(self):
        """
        """
        doc = ("General command-line parameters for this node.")
        return [depends_node.DagNodeAttribute('parameters', "", docString=doc)] 


    def executeList(self, dataPacketDict, splitOperations=False):
        """
        """
        pass
    

###############################################################################
###############################################################################
class DagNodeColorspaceApply(depends_node.DagNode):
    """
    """
    def _defineInputs(self):
        """
        """
        doc = ("A sequence or a single image to transform into a new colorspace.")
        return [depends_node.DagNodeInput('ImageTypes', depends_data_packet.DataPacketImage, True, docString=doc)]
    
        
    def _defineOutputs(self):
        """
        """
        return [depends_node.DagNodeOutput('ImageTypes', depends_data_packet.DataPacketImage)] 


    def _defineAttributes(self):
        """
        """
        doc = ("The colorspace curve file to apply.")
        return [depends_node.DagNodeAttribute('colorCurveFile', "", isFileType=True, docString=doc)] 


    def executeList(self, dataPacketDict, splitOperations=False):
        """
        """
        # Simplifications
        inputImageDp = dataPacketDict[self.inputNamed('ImageTypes')]
        inputImages = inputImageDp.fileDescriptorNamed('filename')
        outputImages = self.outputFramespec('ImageTypes', 'filename')

        # Create a range command if there are multiple frames
        appList = list()
        if inputImages.frames():
            appList.extend(['range', '-t %d-%d' % (inputImages.startFrame, inputImages.endFrame)])
        appList.extend(['colorspaceApply'])
        appList.extend(['-in', inputImages.filename])
        appList.extend(['-colorspace', self.attributeValue('colorCurveFile')])
        appList.extend(['-out', outputImages.filename])
        return appList


    def isEmbarrassinglyParallel(self):
        return True
    

###############################################################################
###############################################################################
class DagNodeLightfieldRasterize(depends_node.DagNode):
    """
    """
    def _defineInputs(self):
        """
        """
        probeDoc = ("A sequence of light probes to be rasterized into a lightfield")
        boxDoc = ("A box to bound the volume of the resulting lightfield")
        return [depends_node.DagNodeInput('Lightprobe', depends_data_packet.DataPacketLightprobe, True, docString=probeDoc), 
                depends_node.DagNodeInput('BoundingBox', depends_data_packet.DataPacketBoundingBox, True, docString=boxDoc)]


    def _defineOutputs(self):
        """
        """
        return [depends_node.DagNodeOutput('Lightfield', depends_data_packet.DataPacketLightfield)] 


    def _defineAttributes(self):
        """
        """
        bDoc = ("?")
        threadsDoc = ("Number of threads to run.")
        gDoc = ("?")
        probeSamplerDoc = ("One of the following: UNIFORMPROBESAMPLER, ?, ?.")
        projectorDoc = ("One of the following: 3DRGBLINEDRAWING, ?, ?.")
        dimsDoc = ("Three integers representing the final lightfield dimensions.")
        return [depends_node.DagNodeAttribute('b', 'O', docString=bDoc),
                depends_node.DagNodeAttribute('threads', '4', docString=threadsDoc),
                depends_node.DagNodeAttribute('g', '', docString=gDoc),
                depends_node.DagNodeAttribute('probeSampler', 'UNIFORMPROBESAMPLER', docString=probeSamplerDoc),
                depends_node.DagNodeAttribute('projector', '3DRGBLINEDRAWING', docString=projectorDoc),
                depends_node.DagNodeAttribute('dims', '256 256 256', docString=dimsDoc)]


    def executeList(self, dataPacketDict, splitOperations=False):
        """
        """
        # Simplifications
        bboxInputDp = dataPacketDict[self.inputNamed('BoundingBox')]

        inputLightprobeDp = dataPacketDict[self.inputNamed('Lightprobe')]
        inputLightprobeList = inputLightprobeDp.fileDescriptorNamed('filename')
    
        # TODO: How should we handle programs that don't let you specify the actual output filename?
        outputIlf = self.outputValue('Lightfield', 'filename')
    
        # Generate a retracer "ilf" settings file
        (osJunk, settingsPathname) = tempfile.mkstemp(prefix="depends_ilfRetracer_", suffix=".ilf", dir='/tmp')
        fp = open(settingsPathname, 'w')
        fp.write('b %s\n' % self.attributeValue('b'))
        fp.write('t %s\n' % self.attributeValue('threads'))
        fp.write('s %s\n' % self.attributeValue('probeSampler'))
        fp.write('p %s %s %s\n' % (bboxInputDp.fileDescriptors['filename'] if bboxInputDp else "none.obj", 
                                   self.attributeValue('projector'), 
                                   self.attributeValue('dims')))
        if self.attributeValue('g') != "":
            fp.write('g %s\n' % self.attributeValue('g'))
        fp.close()
    
        appList = list()
        appList.extend(['Retracer'])
        appList.extend([settingsPathname])
        appList.extend([os.path.dirname(outputIlf)])
        return appList


    def postProcess(self, dataPacketDict):
        """
        """
        # The countFilesToBooger script sets the BOOGER environment variable, 
        # which can be picked up later down the DAG:
        #   #!/bin/bash
        #   FOO=`ls /tmp | wc -l`
        #   export BOOGER=$FOO
        return ['source', '~/countFilesToBooger']


###############################################################################
###############################################################################
class DagNodeImageTransform(depends_node.DagNode):
    """
    """
    def _defineInputs(self):
        """
        """
        doc=("Images to be transformed")
        return [depends_node.DagNodeInput('ImageTypes', depends_data_packet.DataPacketImage, True, docString=doc)]
    
        
    def _defineOutputs(self):
        """
        """
        return [depends_node.DagNodeOutput('ImageTypes', depends_data_packet.DataPacketImage)] 
    

    def _defineAttributes(self):
        """
        """
        doc = ("Enter a non-1.0 value here to scale the image.")
        return [depends_node.DagNodeAttribute('scale', '100', docString=doc)] 


    def executeList(self, dataPacketDict, splitOperations=False):
        """
        """
        # Simplifications
        imageInputDp = dataPacketDict[self.inputNamed('ImageTypes')]
        inputImages = imageInputDp.fileDescriptorNamed('filename')

        outputImages = self.outputFramespec('ImageTypes', 'filename')

        # This should *always* be the case with embarassingly parallel nodes
        # Move this code out to the validation phase of MainWindow
        #if len(inputImages.frames()) != len(outputImages.frames()):
        #   appList.extend(['# INPUT/OUTPUT FRAME COUNTS DO NOT MATCH FOR %s.' % self.name])
        #   return appList

        appList = list()
        if not splitOperations:
            appList.extend(['nuke'])
            if inputImages.startFrame and inputImages.endFrame:
                appList.extend(['-t', '%d-%d' % (inputImages.startFrame, inputImages.endFrame)])
            appList.extend(['-infile', inputImages.filename])
            appList.extend(['-scale', str(float(self.attributeValue('scale')) / 100.0)])
            appList.extend(['-outfile', outputImages.filename])
        else:
            for inFrame, outFrame in zip(inputImages.frames(), outputImages.frames()):
                singleRunList = list()
                singleRunList.extend(['nuke'])
                singleRunList.extend(['-infile', inFrame])
                singleRunList.extend(['-scale', str(float(self.attributeValue('scale')) / 100.0)])
                singleRunList.extend(['-outfile', outFrame])
                appList.append(singleRunList)
        return appList


    def isEmbarrassinglyParallel(self):
        return True

