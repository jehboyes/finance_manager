Common Tasks
============

Listed below are explanations of some of the more 
common administrative tasks, and the commands 
used to complete them. 

A comprehensive list of all the commands and their 
syntax is in the :doc:`Full CLI reference <cli_auto>`, along with the 
extensive help documentation within the app (accessed by running any command with 
the ``--help`` option. 

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
    Although the finance save process can be restricted to individual cost centres, this creates the risk of 
    creating inconsistent internal transactions, and so a general save should always be run before finances 
    are exported or used internally for any analysis. 

The command to save finances is as follows: 

.. click:: finance_manager.cli.finance.save:save
    :prog: fm finance save
    :nested: full 

Setting up a forecast
---------------------

There are a few steps in setting up the forecast:

Obtaining up-to-date actuals 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An export of all general ledger transactions for the year is taken from the Finance system. Filtering up to the current period is 
done within Finance Manager. This data is then uploaded with the ``load`` function, with 
the forecast's :py:attr:`finance_manager.database.spec.f_set_cat` and :term:`Academic Year`: 

.. click:: finance_manager.cli.finance.load:load
    :prog: fm finance load
    :nested: full 

Configure the forecast
~~~~~~~~~~~~~~~~~~~~~~

Each instance of set_cat_id and acad_year requires an entry in :py:attr:`finance_manager.database.spec.conf_forecast` 
to function. Use the ``crud create`` function on the ``conf_forecast`` table 
to create a record if required (using the ``-v`` option to set the values of each of the fields): 

.. click:: finance_manager.cli.db.crud:crud
    :prog: fm db crud 
    :nested: full

Create the sets
~~~~~~~~~~~~~~~

Use the following command to create sets for each eligible cost centre using the set_cat_id and acad_year: 

.. click:: finance_manager.cli.ops.newset:newset
    :prog: fm ops newset
    :nested: full