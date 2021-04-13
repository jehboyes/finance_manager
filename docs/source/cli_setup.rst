Setting up the CLI
==================

This section covers getting started with the Command Line Interface, used for administrative tasks. 

Eventually, the CLI will be distributed as an executable file. For the time being however - whilst 
it is still under development - it is available either from the source code 
on the `Github repository <https://github.com/jehboyes/finance_manager>`_ for the most 
up-to-date version, 
or by installing it from `PyPI <https://pypi.org/>`_. The latter is described below.  

System Requirements
-------------------

* Python 3.6 or above

Setting up
----------

Initial setup
^^^^^^^^^^^^^

.. note::
   
   The shell commands are written for PCs, and may differ for other operating systems. 


The finance manager package is best installed into a `virtual environment <https://www.python.org/dev/peps/pep-0405/>`_, 
the creation of which is included in the below instructions . 

1. Open a command line terminal (e.g. Powershell on Windows).
2. Navigate to a folder to create the virtual environment in (using the ``cd`` command).
3. Check the virtual environment package is installed with ``python -m pip install venv``.
4. Create the virtual environment with ``python -m venv venv``. 
5. Activate the new virtual environment with ``venv\scripts\activate``. This will add the name 
   of the environment ('venv') to the command.   
6. Install the package using pip with ``pip install finance_manager``.

So the complete set of instructions::

   PS C:\Users\username\documents> cd projects\example
   PS C:\Users\username\documents\projects\example> python -m pip install virtualenv
   PS C:\Users\username\documents\projects\example> python -m venv venv
   PS C:\Users\username\documents\projects\example> venv\scripts\activate
   (venv) PS C:\Users\username\documents\projects\example> pip install finance_manager

To check it's installed properly, try bringing up the in-app help by typing ``fm --help``. 
In the unintended event that running this command produces a ``ModuleNotFoundError``, 
use ``pip install [given name of missing module]`` to try and install it, 
and try the ``fm --help`` command again. 



.. _config-instruction:

Local configuration
^^^^^^^^^^^^^^^^^^^

The CLI relies on a local file named 'config.ini' to provide credentials for accessing the various databases referenced 
within the CLI. 
A blank 'config.ini' will be generated the first time the application is run, 
with blank values for the connection parameters required. Either open the config.ini file in any text editor and add the relevant 
parameters, or ask a colleague (who already has access) for help/a copy of their config.ini file. 

You're ready to start using the CLI! See :doc:`cli_usage` for more instructions. 
