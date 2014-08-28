#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

import os
import tempfile
import subprocess

import depends_output_recipe


"""
This is an example module/plugin for how to ship execution recipes off to the
target of your choice.  It generates bash shell scripts and can be eaisly modified
to write others such as 'batch' or 'tcsh'.
"""


################################################################################
################################################################################
class BashOutputRecipe(depends_output_recipe.OutputRecipe):
    """
    """
    def __init__(self):
        depends_output_recipe.OutputRecipe.__init__(self)


    def name(self):
        return "Bash Output Recipe"


    def generate(self, executionRecipe, destFileOrDir, executeImmediately=False):
        """
        Create a bash script from the given execution recipe into a temporary file in 
        the given dir or directly to a given path.
        """
        pathName = None
        if os.path.isdir(destFileOrDir):
            (osJunk, pathName) = tempfile.mkstemp(prefix="bashExecutionRecipe_", suffix=".sh", dir=destFileOrDir)
        else:
            pathName = destFileOrDir
        
        fp = open(pathName, 'w')
        print "WRITING SHELL SCRIPT HERE:", pathName
        for item in executionRecipe:
            if item[1]:
                fp.write("# Node '%s' generated the following line...\n" % item[0])
                fp.write(" ".join(item[1]))
                fp.write("\n\n")
        fp.close()
    
        if executeImmediately:
            print "Executing bash script as a subprocess of this application..."
            runme = subprocess.Popen(['bash', pathName], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            out, err = runme.communicate()
