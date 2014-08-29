#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

from PySide import QtGui


"""
A collection of QUndoCommand objects that are managed by the QT undo manager.
"""


###############################################################################
###############################################################################
class SceneOnlyUndoCommand(QtGui.QUndoCommand):
    """
    An undo command that only tracks the state of the user interface 
    QGraphicsScene.  No internal dependency graph info is tracked here.
    """
    
    def __init__(self, oldSnap, newSnap, scene, parent=None):
        """
        """
        QtGui.QUndoCommand.__init__(self, parent)
        self.scene = scene
        self.oldSnap = oldSnap
        self.newSnap = newSnap
        self.first = True
        
    
    def id(self):
        """
        Required for commands that are capable of merging themselves.
        """
        return (0xbeef + 0x0000)


    def undo(self):
        """
        Restore the old state of the user interface.
        """
        self.scene.restoreSnapshot(self.oldSnap)
        
        
    def redo(self):
        """
        Restore the new state of the user interface.
        The 'first' flag is used to stifle a double-apply when the command is
        first executed.
        """
        if not self.first:
            self.scene.restoreSnapshot(self.newSnap)
        self.first = False


###############################################################################
###############################################################################
class DagAndSceneUndoCommand(QtGui.QUndoCommand):
    """
    An undo command that tracks the state of the user interface as well as the
    state of the given dependency graph.
    """

    def __init__(self, oldSnap, newSnap, dag, scene, propertyWidget=None, parent=None):
        """
        """
        QtGui.QUndoCommand.__init__(self, parent)
        self.dag = dag
        self.scene = scene
        self.propertyWidget = propertyWidget
        self.oldSnap = oldSnap
        self.newSnap = newSnap
        self.first = True
        
    
    def id(self):
        """
        Required for commands that are capable of merging themselves.
        """
        return (0xbeef + 0x0002)


    def undo(self):
        """
        Restore the old state of the user interface and dependency graph.
        Rebuild the property widget if it was provided as well.
        """
        self.dag.restoreSnapshot(self.oldSnap)
        self.scene.restoreSnapshot(self.oldSnap)
        if self.propertyWidget:
            selectedDrawNodes = self.scene.selectedItems()
            selectedDagNodes = [sdn.dagNode for sdn in selectedDrawNodes]
            self.propertyWidget.rebuild(self.dag, selectedDagNodes)
        
        
    def redo(self):
        """
        Restore the new state of the user interface and dependency graph.
        Rebuild the property widget if it was provided as well.  The 'first' 
        flag is used to stifle a double-apply when the command is first executed.
        """
        if not self.first:
            self.dag.restoreSnapshot(self.newSnap)
            self.scene.restoreSnapshot(self.newSnap)
            if self.propertyWidget:
                selectedDrawNodes = self.scene.selectedItems()
                selectedDagNodes = [sdn.dagNode for sdn in selectedDrawNodes]
                self.propertyWidget.rebuild(self.dag, selectedDagNodes)
        self.first = False
