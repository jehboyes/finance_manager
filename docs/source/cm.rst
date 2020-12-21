Curriculum Model Interaction
============================

The Finance Manager system uses the Curriculum Model as a basis for calculating teaching costs. 

Unlike previous mechanisms for prospectively costing courses, this system is completely empirical, 
containing no assumptions or estimates. Academic management have control of all of the variables in the 
calculations. 

Furthermore, the curriculum delivery specified in the Curriculum Model is also used as the basis for timetabling, 
which both ensures its accuracy, and reduces the amount of work required from :term:`Academic Management`.


Process
-------

Currently, the Curriculum Model's database and the Finance Manager's database are distinct, but have the ability to communicate 
with each other. This is achieved by having both databases reside on the same server. 

The Curriculum Model contains several curricula, and each curricula is configured to use a particular type of student numbers. 
For example, the curriculum for the next academic year will use thea specific set of prospective student numbers for that year. 
These student numbers are also stored in the curriculum model database. 
The Curriculum Model uses the curriculum specifications and its student numbers 
to calculate the total number of hours required to deliver the curriculum (including module calculation). 

The Finance Manager takes this total delivery time, subtracts the amount of time the academic management spend 
delivering the curriculum, and distribute the remainder between :term:`Fractional Academic` staff, using their given 
FTE as a means of distributing the hours.   

.. note::

   In addition to the work calculated here, fractional contracts also have a static increase; see :term:`Fractional Academic Salary` 
   for more information. 


Implementation
--------------

Because of the hours being inaccessible to the finance manager users (in that a finance manager *database* user can't access the 
curriculum model database), a static copy of the total number of hours on a curriculum is kept in the ``f_set`` table. This can  
be updated either by running the command ``fm cm curriculum`` command, or by pressing refresh on the staffing list in the powerapp.  

The ``v_calc_staff_fte`` view uses the user defined function ``udfFracFTE`` to calculate FTEs for fractional staff, 
based on the actual amount of curriculum delivery to be done. 
 
