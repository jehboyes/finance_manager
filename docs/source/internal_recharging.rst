Internal Recharges
==================

Some transactions describe financial interactions between different areas of the institution, 
in that they have no cash impact but serve to give a more accurate picture of how the 
institution functions. 

These transactions must always have an equal and opposite transaction to be included in the finances, 
to prevent showing artificial income or expenditure.  

Internal Recharges fall into one of the three following categories.

Manual Recharges
----------------

These are transactions added by end-users that 
relate to specific services or funds provided by one department to another. 

Examples include:

- Accounting for staff working between different departments (on a short term basis)
- Distributing money raised externally by the central fundraising department to other specific beneficiary departments

In the App these transactions are referred to internal non-pay (which also includes inter-company recharges, 
which are not regarded as proper internal transactions). 

These transactions appear on the Internal Expenditure line in the :term:`SOCI`. 

Specific Automatic Recharges
----------------------------

These are transactions which are calculated whenever a set's finances are saved. 

Currently, the only transactions generated in this way are 
those that expend a small proportion of HE fee income (incurred in each HE pathway) to the Access and Participation
cost centre. 

These transactions appear on the Internal Expenditure line in the :term:`SOCI`. 

General Automatic Recharges
---------------------------

These are transactions which are generated after all finances have been calculated, and are *not* included in the 
actual finances (e.g. those that would be included in a finance export). These transactions basically 
recharge any net deficits at cost centre level to income-generating cost centres. They therefore represent 
the 'internal economy' of the institution.   

The f_set_costing table is used to manually specify where a loss-making set should be costed. It is defined by set
(rather than by cost centre) to recognise that these costings could vary for sets being worked on simultaneously 
(e.g. a forecast and a budget). 

If a set does not appear in the f_set_costing table, it is instead costed between the HE pathways proportionally 
by the pathways' income.  


