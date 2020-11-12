Setting up the CLI
==================

This section covers getting started with the Command Line Interface, used for administrative tasks. 

Eventually, the CLI will be distributed as an executable file. For the time being however 
- whilst it is still under development - it is only available via the source code, which is what 
the rest of this section describes. 

System Requirements
-------------------

* Python 3.6 or above

Setting up
----------

Initial setup
^^^^^^^^^^^^^

.. note::
   
   The shell commands are written for PCs, and some will differ for Macs. 


1.  Create a folder that will house the application's code.
2.  Clone the `github repository <https://github.com/jehboyes/finance_manager>`_ to that folder.
3.  Open Powershell in that folder.  
4.  Create a virtual environment by typing `py venv venv`.
5.  Activate that virtual environment by typing `venv\scripts\activate`. `(venv)` should appear at the start of your shell. 
6.  Type `pip install -r requirements.txt`, which will install the required libraries in the virtual environment. 
7.  Type `pip install . --editable`, which will install the package. 

You're ready to start using the CLI! See the :ref:`usage page <cli_usage>` for more instructions. 

Local configuration
^^^^^^^^^^^^^^^^^^^

The CLI relies on a local config.ini file to provide credentials for accessing the various databases referenced within the CLI. 
A blank config.ini will be generted the first time the application is run. 
