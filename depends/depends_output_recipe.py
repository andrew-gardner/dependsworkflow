#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import depends_util


"""
A class and collection of functions that assist in loading output recipe
plugins.  Creating one's own output recipe consists of inheriting from the 
OutputRecipe class, setting a unique name, and overloading the generate 
function.
"""


###############################################################################
## Utility
###############################################################################
def outputRecipeTypes():
    """
    Return a list of available output recipe types.
    """
    return OutputRecipe.__subclasses__()


###############################################################################
## Base recipe class
###############################################################################
class OutputRecipe(object):
    """
    A simple parent class that new output recipe plugins can inherit from.
    Each method must be overridden with unique code in order to make the plugin
    accessible to the Depends plugin system.
    """

    def __init__(self):
        pass


    def name(self):
        return "Empty Base Output Recipe"


    def generate(self, executionRecipe, destFileOrDir, executeImmediately=False):
        """
        Given a list of tuples with ("Node name", [list of commandline arguments
        needed to execute program]) and a directory with which to write to, this
        function generates a script capable of executing the requested programs
        or passing them off to an execution engine of some sort.  An optional
        flag can be specified to execute the script from within the Depends 
        user interface.
        
        Note: The parameters to this function may need to be enhanced for 
              complex render farm managers to properly parallelize everything.
        """
        raise RuntimeError("Attempting to execute Output Recipe base class.")


########### FUNCTION TO IMPORT PLUGIN RECIPES INTO THIS NAMESPACE  ############
def loadChildRecipesFromPaths(pathList):
    """
    Given a list of directories, import all classes that reside in modules in those
    directories into the node namespace. TODO better docs
    """
    for path in pathList:
        recipeClassDict = depends_util.allClassesOfInheritedTypeFromDir(path, OutputRecipe)
        for rc in recipeClassDict:
            globals()[rc] = recipeClassDict[rc]
