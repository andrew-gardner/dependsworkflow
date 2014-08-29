*******************
Depends User Manual
*******************

Table of contents
=================
1. Installing Depends
  A) Requirements
  B) Gathering dependencies
  C) Installing Depends
  
2. Running Depends
  A) Program execution
  B) Commandline parameters
  C) Plugins & Environment variables

3. The User Interface
  A) The Dag Window
  B) The Scenegraph
  C) The Properties window
  D) The Variable Window

4. Creating And Working With a Depends Workflow
  A) Creating and Executing A Simple Dag
  B) Modifying workflows

5. Reference
  A) Menu items
  B) Keyboard shortcuts



********************************************************************************


1. Installing Depends
=====================
Depends is developed in the Python programming language and therefore has no
build procedure.  It relies on two external libraries at the moment, but
everything else is self-contained.  Read on for more information.



A) Requirements
---------------
Depends is known to run in Python 2.6.6 under CentOS Linux.  Though other
  operating systems should work as well, CentOS is the only one the development
  team has used.
System requirements are very low, as very little data is loaded into memory
  during a Depends workflow management session.

It uses the PySide bindings for QT 4.8 and a BSD-licensed dependency graph 
  library named Networkx.
These Python modules must be installed before running Depends.



B) Gathering dependencies
-------------------------
The Python programming language can be found at https://www.python.org/ 
The QT 4.8 library can be found at http://qt-project.org/
The Pyside bindings for QT can be found at http://qt-project.org/wiki/pyside
The Networkx Python module can be found at https://networkx.github.io/
Each site contains information on how to install the library or module for
  nearly any operating system.  Please consult the pages for info.



C) Installing Depends
---------------------
Since Depends is a python script and set of accompanying modules, installation
  consists of copying the source to a convenient location, adding the directory
  to your system path, and simply running the executable script "depends".
Environment variables can be set that control the software's execution, but are
  not required to run the program.  These are described further in section 2D.
  


********************************************************************************


2. Running Depends
==================
Starting depends is simply a matter of running the executable script "depends" 
  from the commandline.



A) Program execution
--------------------
Depends is primaritly a GUI program, but there is also a flag that lets one run
  it from the commandline only in a headless mode.
To run in headless mode, one must specify a workflow to load and a node name to
  execute.
Further details are below in section 2B.



B) Commandline parameters
-------------------------
All commandline parameters work when prefixed by a single dash '-' or a double
  dash '--'.  Parameters that take an additional option should be followed by
  a space, then the option.

Running Depends with the following commandline options do the following:
  "-help" : Brings up a list of command line options.
  "-workflow FILENAME" : load the specified file directly into Depends.
  "-nogui" : Run Depends without its graphical user interface.  Must be used in
             conjunction with -node flag.
  "-node" : Specify a node in the given scenegraph, by name, to execute.  Only 
            works when the -nogui flag is given.
  "-style" : Specify a graphics stylesheet other than the default one named
             darkorange.  Information on creating stylesheets for QT apps can be
	     found here: http://qt-project.org/doc/qt-4.8/stylesheet.html
  "-vsub" : Specify a value for a variable in the workflow that is to be loaded
            into Depends.  The variables and their values must be specified as
	    VARIABLE_NAME=VALUE - no spaces between the = and the variable name
	    and new value.
  "-evalpath" : Often used in conjunction with the -nogui flag, this specifies
                where the results of the workflow evaluation get written.
		Depends will echo where the file is created.  This value 
		currently defaults to '/tmp'.
  "-recipe" : Specify the execution recipe by name from the commandline.  This
              allows the user to decide which execution recipe will be used for
	      the new Depends wokflow session.



C) Plugins & Environment Variables
----------------------------------
Plugins come in four flavors: Nodes, Data Packets, Output Recipes, and File
  Dialogs.
Each is loaded from a variable in the current workflow, namely NODE_PATH, 
  DATA_PACKET_PATH, OUTPUT_RECIPE_PATH, and FILE_DIALOG_PATH respectively.
These variables default to the Depends 'binary' work path (DEPENDS_DIR), plus 
  a subdirectory under that.
The subdirectories are 'nodes', 'data_packets', 'output_recipes', and
  'file_dialogs.'
These can be overridden when starting Depends by setting environment variables 
  in your shell.  The environment variables are named the same as the Depends
  variables, but with a "DEPENDS_" preceding each.  In other words, 
  $DEPENDS_NODE_PATH, $DEPENDS_DATA_PACKET_PATH, $DEPENDS_OUTPUT_RECIPE_PATH, 
  and $DEPENDS_FILE_DIALOG_PATH.
Multiple paths can be specified in the environment variable by separating them
  with a colon like so: /tmp:/foo/bar:/home/depends/nodes

Plugins can be developed by a somewhat-experienced Python programmer.
Documentation for their creation is available in DEPENDS_DIR/doc/development.txt


********************************************************************************


3. The Depends User Interface
=============================
Depends contains 4 primary windows.  
  The Dag window (or Dependency graph window) is the primary window and will 
    never go away.
  The remaining four windows are dockable and can be hidden by toggling their 
    status in the Window menu option, right clicking on the title bar and 
    toggling their status, or clicking the little x in their corner.
  The windows and their functions are described below.
  


A) The Dag Window
-----------------
The Dag Window lets you create, navigate, and view dependency graphs.
This window can be panned by middle-mouse-clicking and dragging.
It can be zoomed by dialing the scroll wheel forward and backward (the zoom
  centers around the point your mouse is pointing at).
Items can be selected by single-left-clicking each individually.  Holding the
  CTRL key will toggle selected items.
Left-click-dragging will select a group of nodes, and holding CTRL will place
  the selection mode in a toggle state.
Clicking on Dag nodes and dragging them around will move the nodes.
Clicking on the small yellow nub under a node will begin creating a connection
  between nodes.
Letting go of this connection on a new node will connect the nodes together.
Letting go of this connection elsewhere will destroy the connection.
Clicking on a connections' arrowhead and dragging will disconnect the connection
  from the node it is connected to and allow you to either connect it to another
  or drop the connection in space to delete it.
Right clicking brings up a "Create node" dialog, letting you create a new node
  of the selected type.
Pressing the "f" keyboard key frames all items in the current Dag.  Pressing it
  when something is selected frames only what is selected.
Selecting a Dag node and pressing and holding the "space" key shows a collection
  of all nodes the current node depends on.  This is colored most intensely for
  nodes that are close to the current one and dimmest for those far away.



B) The Scenegraph
-----------------
The Scenegraph window displays which data packets are available to a given node
  at a given point in the Dag.
Each entry contains a data packet type which is colored red if the data is not
  yet on disk, or green if it is.
The type is followed by a "short name" that uniquely describes the data packet
  in the Dag.  This is used internally by Depends, but should not concern the
  user much.
Hoovering the mouse over an entry lights up a node in the Dag, showing where the
  packet came from.
If the data packet is being used by the currently-selected node as an input, it
  will also light up in the input field.



C) The Properties window
------------------------
The properties window lets you edit the properties of a node.
There are Input properties, Attribute properties, and Output Properties.
Help may be available for each property by hoovering your mouse over the 
  property name.

Input properties show which incoming data packet has been selected by this node
  as the data it will ingest.
Setting an Input property requires dragging a data packet out of the Scenegraph
  window, onto the Input field.
Each Input can specify its range as a subset of the range coming out of the
  incoming data packet.
Pressing the 'x' button next to the range entry fields clears the Input.
Hoovering the mouse over an Input that has been set will visually alert the user
  in both the Scenegraph window and the Dag window, which node and data packet
  is specified in the input.

Attribute properties are a list of the attributes defined in the node 
  definition.
These vary per node, and can contain many types of information.  
File dialogs may be available for attributes that specify them.

Output properties are a list of the files this node writes to disk.
They are always filenames, and may contain single files or ranges of files.
A single range, however, is applied to all files in the output.  This means
  all files in a single output must have the same number of files *except* in
  the case of single files.  This allows for a single description file to be 
  written alongside a series of files it describes.



D) The Variable Window
----------------------
The Variable window shows a collection of all the variables defined for the 
  current workflow.
The user can define a new variable by entering its name in the last row of the
  table and its value by entering it next to the name.
Variables that already exist can be modified by double-clicking their value 
  field and typing a new value.
Some variables, however, are read-only.  These cannot be edited by 
  double-clicking their value field.
All variables can be referred to in any Attribute edit field by prefixing their
  name with a '$'.  So 'FOO' in the variable window can be used in an attribute
  for scale, for example, by simply entering '$FOO' in the attribute value 
  field.



********************************************************************************


4. Creating And Working With a Depends Workflow
===============================================
Creating a workflow Dag in Depends is a relatively straightforward task.
Depends excels after the Dag has been created and small modifications are made
  to the existing work.



A) Creating and Executing A Simple Dag
--------------------------------------
The logistics of this are outlined in section 3A, "The Dag Window."
The general idea, however, is that you want to create a chain of events that
  depend on eachother.
Creating a node that reads images off disk, then creating a node that modifies
  the images is a logical step.
Connecting the reader to the modifier (from, to) is the next logical step.
Selecting the modifier, finding the data packet from the reader and dragging it
  to the modifier's input works well next.
Selecting the input node and setting its output files to point to files on disk
  (file ranges can be specified with padding by using ###s and values in the
  range field hidden under the dialog - this is done in the "Nuke style" of 
  frame numbering) will turn its light in the Dag window to green and similarly
  its data packet display in the scene graph to green.
Setting the output files for the modifier node to a valid path on disk is a good
  next step.
Setting some attributes on the modifier node that do something to the input is
  nice.
Finally, selecting the modifier node and clicking the Execute menu's "Write
  Recipe" function will do a validation check on your Dag and write an execution
  recipe to /tmp.
Open this recipe with a text editor of your choice and examine its contents.
If the "Bash Output Recipe" is selected, you should have a shell script that
  can be executed by typing "sh '/tmp/scriptnamehere'" and looking for the
  results in the location your modifier node specified.



B) Modifying workflows
----------------------
If the above operation completed successfully, both nodes should have little
  green lights on their left side.  This means the data their outputs point to
  exists on disk.
Try changing the input node's output filename to something different.  Make sure
  the file exists on disk, though.
See how the modifier node's light went from green to blue?  This means the data
  in this node is stale.
The definition is stale is that the data on disk that the modifier node points
  to exists, but is not what the Dag has generated.
If you change the output filename of the modifier node, the stale light goes to
  red (presuming you changed it to a file that doesn't exist).  This means that
  you are ready to execute the Dag again.
Two tools exist to assist in this process.  The Execute menu's "Wipe stale 
  status" simply clears the stale status and lets you overwrite the existing
  file on disk.  The "Version Up Outputs" dialog changes the filenames of all
  output files in the node with a newer version number and lets you execute the
  node to generate new results.  Try each out to see what they do!
This is just one of the many powerful tools the Depends Dag workflow management
  system presents.  Others are described elsewhere in this document.


********************************************************************************


5. Reference
============
An in-depth exploration of what each menu item does in the Depends user 
  interface.



A) Menu items
-------------
File menu:
  "Open DAG..."
  Brings up a file dialog where you select which Dag to load.
  
  "Save DAG"
  Saves the current Dag in-place.  Asks for a filename if there isn't one
    already set.
    
  "Save DAG Version Up"
  Saves the current Dag with an incremented version number.
  
  "Save DAG As..."
  Brings up a file dialog to let you save as a different filename.
  
  "Quit..."
  Exit Depends.  Brings up a dialog asking to save if there are modifications to
    the current workflow.

Edit menu:
  "Undo / Redo"
  Depends features a fully-functional undo/redo tool.  Currently, however, 
    setting variable values cannot be undone.

  "Create Node"
  Brings up a sub-menu of nodes that can be created in this Depends session.

  "Delete Node(s)"
  Deletes the selected nodes and all incoming and outgoing connections.

  "Shake Node(s)"
  Remove a node from its incoming and outgoing connections without destroying
    association information downstream nor deleting the selected node.

  "Duplicate Node(s)"
  Duplicate the selected nodes, with attributes but without inputs and outputs.

  "Group Nodes"
  Group the selected nodes into a parallel execution group.

  "Ungroup Nodes"
  Remove the given nodes from their group.

Execute Menu:
  "Write Recipe"
  Writes an execution script to disk for the selected Dag node.  Uses the recipe
    selected in "Output Recipe" below.

  "Execute Selected Node"
  Writes an execution script for the selected Dag node and immediately executes
    it as a subprocess of Depends.  "This could take awhile..."

  "Output Recipe"
  Pops up a sub menu to let you choose which execution recipe plugin you would
    like to use the next time you execute "Write Recipe" or "Execute Selected
    Node."

  "Wipe Stale Status"
  Clears the stale status of a selected node or nodes without changing any
    file output names.  Do this if you are sure you want to overwrite the files
    that are present the next time you execute a recipe.

  "Version Up Outputs"
  Increment the filename version for all outputs of all selected nodes.  Also
    clears the stale status of the given node.  Do this as a shortcut to 
    changing filenames individually when something was modified upstream.

  "Reload Plugins"
  A development helper for when you want to reload a plugin that is in 
    development.  Actually shuts down Depends, but starts the user interface 
    again with the exact workflow and settings loaded.



B) Keyboard shortcuts
---------------------
Dag Window
  "F"
  Frame all items in the Dag or the selected ones only.

  "Space"
  Display all dependencies for a selected node.  The closest is the brightest,
    the furthest away, the dimmest.

(All other keyboard shortcuts are described in the menu pulldown for their
  respective actions)
