**********************************************
Depends Plugin and Software Development Manual
**********************************************

Table of contents
=================
1. Extending Depends with plugins
  A) Creating new node types
  B) Creating new data packet types
  C) Creating new file dialogs
  D) Creating new output recipes

2. Depends architecture overview
  A) Theory and practice
  B) Practical considerations




********************************************************************************


1. Extending Depends with plugins
=================================
There are many types of plugins.
Each is written using Python.
Depends looks for each type of plugin in a subdirectory under depends binary, 
  but can be expanded with environment variables for each plugin type (see user
  manual).
Each plugin is created by inheriting from an existing Depends data type, and 
  therefore docs exist for each function that can and/or should be overloaded.
Example plugins come bundled in the default plugin subdirectories in the Depends
  download.



A) Creating new node types
--------------------------
All node types must inherit from the Depends DagNode class.
Importing the depends_node module is necessary.  It is guaranteed to be in the 
  Python module path, so just "import depends_node".
If you want to make a new dag node, you currently must name it DagNodeXXX 
  (where XXX is a camel-caps styled type for the dag node).  YUCK!  This will
  change.
Inherit as so: class DagNodeDirectoryList(depends_node.DagNode)
Four functions *must* be overloaded to insure proper operation:
  def _defineInputs(self):
    This function returns a list of depends_node.DagNodeInput objects that
      represent all the inputs the node can take.
    DagNodeInput objects have names (identifier and visible in the UI)
    DagNodeInput objects have a defined data packet type they accept (note 
      inheritance and its powers in "Creating new data packet types" section).
    DagNodeInput objects have a flag stating if they're required or not.
    DagNodeInput objects have a documentation string that pops up on mouseover.
  
  def _defineOutputs(self):
    This function returns a list of depends_node.DagNodeOutput objects that
      represent all the data this node can output.  BUT BE CAREFUL!  Just return
      a list one-element long (for now).
    DagNodeOutput objects have names (identifier and visible in the UI).
    DagNodeOutput objects have a defined data packet type they create.
    DagNodeOutput objects have a documentation string that pops up on mouseover.
    DagNodeOutput objects have a named custom file dialog if it's desired that
      the standard dialog doesn't pop up when clicking the 'browse' button.
  
  def _defineAttributes(self):
    This function returns a lit of depends_node.DagNodeAttribute objects that
      represent all the user-specifiable parameters this node can take.
    DagNodeAttribute objects have a default value
    DagNodeAttribute objects have a flag stating if it's a file (file dialog
      selector appears in the UI if so).
    DagNodeAttribute objects have a documentation string that shows on mouseover.
    DagNodeAttribute objects have a named custom file dialog if it's desired 
      that the standard dialog doesn't pop up when clicking the 'browse' button.
  
  def executeList(self, dataPacketDict, splitOperations=False):
    Given a dict of input dataPackets, return a list of commandline arguments
      that are easily digested by an execution recipe.
    The splitOperations parameter is passed to nodes that are embarrassingly 
      parallel.  Nodes that execute with their operations split should return 
      a list of lists of commandline arguments that basically run entire frame 
      sequences as separate commands.
    This is a little painful at the moment, but various functions exist to help
      out.  outputFramespec, attributeValue, etc

Four functions *may* be inherited:
  def preProcess(self, dataPacketDict):
    Behaves just like executeList, but runs an operation immediately preceeding
      what is defined in executeList.
  
  def postProcess(self, dataPacketDict):
    Behaves just like executeList, but runs an operation immediately following
      what is defined in executeList.
  
  def validate(self):
    Raise a RuntimeError if something isn't set as you would like it.
    Attribute values being set as desired is a common validation routine.
  
  def isEmbarrassinglyParallel(self):
    If this node can operate on all files one after another and can be 
      run all at once, return True from this function.  It lets the execution
      recipe do funky things.



B) Creating new data packet types
---------------------------------
Data packet types are simply collections of string data that point to files on
  disk.
Be sure to name your type DataPacket(Whatever) since that's how things are done
  for now (YUCK!  This will change).
The only other thing that is necessary is to override the base class' 
  self.filenames dictionary with your own.  Some examples:
    self.filenames['filename'] = ""
    self.filenames['boundingBox'] = ""
    self.filenames['transform'] = ""

Inheritance note: A datapacket type can inherit from another type.  This makes
  it possible for a node that takes the parent data packet type to automatically
  take its children as well.
So normally you inherit as so: 
  class DataPacketImage(depends_data_packet.DataPacket):
But if you want a more interesting image (eg. with a transform), inherit as so:
  class DataPacketLightprobe(DataPacketImage):
See the Lightprobe data packet type as an example.


C) Creating new file dialogs
----------------------------
File dialogs are simple to create.
Create a new class inherited from the Depends FileDialog class:
  class QtFileDialog(depends_file_dialog.FileDialog)
Then overload the name function:
  def name(self):
    return "Standard Qt File Dialog"
And finally overload the browse function (return either a string to a filename
  of None if nothing is chosen).
    def browse(self):
      return QtGui.QFileDialog.getOpenFileName()[0]
Any Pyside code can be used to create this dialog as long as it is closed by
  the time the browse function returns.
The parent Qt App will be present for you.
Node attributes and outputs can use the file dialog you've created by specifying
  its name (as returned by the name function) when they're constructed/defined.



D) Creating new output recipes
------------------------------
New output recipes are inherited from the Depends OutputRecipe class as such:
  class BashOutputRecipe(depends_output_recipe.OutputRecipe)
Overloading the name function is required:
  def name(self)
Then the meat occurs in the must-override generate function:
  def generate(self, executionRecipe, destFileOrDir, executeImmediately=False)
  This funciton takes a list of tuples with ("Node name", [list of commandline
    arguments needed to execute program]), a destination file or directory to
    write data to, and an optional flag that allows depends to run the recipe
    immediately.
  The idea is you take the commandline arguments in the order they're given to
    you and execute them.  The current infrastructure doesn't allow for much
    interesting to happen with parallelization, so this can be enhanced in the
    future when some render farm manager is incorporated.


********************************************************************************


2. Depends architecture overview
================================
Depends is open source
This part of the document attempts to explain some of the decisions made when
  originally developing depends
It's organized by file and may be a little haphazard, but much of the info is
  important.


  
A) Theory and practice
----------------------
Todo.


B) Practical considerations
---------------------------
Todo.
