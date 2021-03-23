.. _cli_usage:

Using the CLI
=============

Overview
--------

The command line interface is a set of nested commands used in a shell/terminal. It was built using the excellent `Click <https://click.palletsprojects.com/en/7.x/>`_ package. 

The entry point/parent command group is ``fm``; all sub-commands include a ``--help`` option, which will print the relevant part of the below 
documentations to the command line. 

The command hierarchy is visible in the navigation pane on the left.  

.. click:: finance_manager.cli:fm
    :prog: fm
    :nested: full