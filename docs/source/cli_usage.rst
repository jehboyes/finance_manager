Using the CLI
=============

.. note::
    For any of the CLI commands to function correctly, the local config file must be 
    correctly configured (see the :ref:`config instructions <config-instruction>`). 

Creating sets
-------------

The process of setting up a new round of sets, for a given set category and academic year. It is 
handled by a single command: 

.. click:: finance_manager.cli.ops.newset:newset
    :prog: fm ops newset
    :nested: full

So to create sets for the 2025 year, with set category ID 'ABC', curriculum ID 42 and student number usage 'Actual', 
that allows student numbers to be changed through the interface, the command would be::

    fm ops newset --change_sn ABC 2025 42 Actual



Copying forward set contents
----------------------------

This is useful for populating the input tables of sets that are meant to be iterations on previous sets. This is handled 
by a single command: 

.. click:: finance_manager.cli.ops.copyset:copyset
    :prog: fm ops copyset
    :nested: full 

So to copy forward to the contents of input tables to 2026 BBB sets from 2026 AAA sets, 
and mark the 2026 AAA sets as closed, the command would be::

    fm ops copyset --close 2026 BBB 2026 AAA


Saving finances
---------------

There is an intentional disconnect between the Finance Manager's input tables 
(those edited in the :doc:`PowerApp <powerapp_guide>`) and the financial data stored. The data from the input 
tables has to undergo a computationally-heavy process to be converted into this final finance data, and so 
is manually triggered. 

.. warning::
    Although the finance save process canbe restricted to individual cost centres, this creates the risk of 
    creating inconsistent internal transactions, and so a general save should always be run before finances 
    are exported or used internally for any analysis. 

The command to save finances is as follows: 

.. click:: finance_manager.cli.finance.save:save
    :prog: fm finance save
    :nested: full 

