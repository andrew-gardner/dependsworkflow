
import tempfile
import subprocess

import depends_output_recipe


class CmdOutputRecipe(depends_output_recipe.OutputRecipe):
    """Implement bash_recipe.py equivalent for Windows"""

    def __init__(self):
        depends_output_recipe.OutputRecipe.__init__(self)

    def name(self):
        return "Cmd Output Recipe"

    def generate(self,
                 executionRecipe,
                 destFileOrDir,
                 executeImmediately=False):
        """Generate bat-file from the given execution recipe"""

        # Passed `destFileOrDir` always returns /tmp which doesn't
        # apply on Windows platforms. Bypassing it here.
        #
        # Todo: Clean-up temporary files. Couldn't do it directly
        # after execution, possibly due to delayed usage of file
        # by Depends. (Interpreter complains about file being in use)

        root = tempfile.mkdtemp()
        osJunk, pathName = tempfile.mkstemp(prefix="bashExecutionRecipe_",
                                            suffix=".bat", dir=root)

        with open(pathName, 'w') as fp:
            for item in executionRecipe:
                if not item[1]:
                    continue

                fp.write("# Node '%s' generated the "
                         "following line...\n" % item[0])
                fp.write(" ".join(item[1]))
                fp.write("\n\n")

        if executeImmediately:
            print ("Executing command as a subprocess "
                   "of this application...")
            command = ['cmd', '/C', pathName]
            runme = subprocess.Popen(command,
                                     stderr=subprocess.STDOUT,
                                     stdout=subprocess.PIPE)
            out, err = runme.communicate()
