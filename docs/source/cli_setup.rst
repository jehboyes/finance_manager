.. _setupcli:

Setting up the CLI
==================

This section covers getting started with the command line interface, used for administrative tasks. 

Eventually, the CLI will be distributed as an executable file. For the time being however 
- whilst it is still under development - it is only available via the source code, which is what 
the rest of this section describes. 

System Requirements
-------------------

* Python 3.6 or above

Setting up
----------

.. note::
   
   The shell commands are written for PCs, and some will differ for Macs 


1.  Create a folder that will house the application's code
2.  In a shell, navigate to that folder with `cd [filepath]`
3.  Clone the github repository to that folder
4.  Create a virtual environment by typing `py venv venv`
5.  Activate that virtual environment by typing `venv\scripts\activate`. `(venv)` should appear at the start of your shell. 
6.  Type `pip install -r requirements.txt`, which will install the required libraries in the virtual environment. 
7.  Type `pip install . --editable`, which will install the package. 

You're ready to go! 


