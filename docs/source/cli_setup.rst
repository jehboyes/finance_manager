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

1. Open a command line terminal
1. *Optional* Activate the virtual environment you are installing the package on. 
2. Install the package from pypi using pip with the following shell command ``pip install finance_manager``

Local configuration
^^^^^^^^^^^^^^^^^^^

The CLI relies on a local file named 'config.ini' to provide credentials for accessing the various databases referenced 
within the CLI. 
A blank 'config.ini' will be generted the first time the application is run, with blank values for the connection parameters required. 

You're ready to start using the CLI! See :doc:`cli_usage` for more instructions. 
