Pay Calculations
================

.. note::
    
    This section details how pay costs are calculated in Finance Manager, where the aim 
    is to estimate costs accurately; actual calculations may vary.  
     
Claims
------

The claim pay calculations are defined in the view ``v_calc_claims``.  

.. automodule:: finance_manager.database.views.v_calc_claim
    :members:

.. _claim-pay-hourly:

Example Hourly Rate
~~~~~~~~~~~~~~~~~~~

The actual hourly rate an employee is paid is calculated as follows:

.. math::
    
    \text{actual hourly pay} = \text{Basic hourly rate} \times \text{Holiday accrual} \times \text{Rate modifier}
    
For example, if a member of academic staff on the new contract (see :term:`Age of Contract`) and with a *basic* hourly rate of £21.52 
(the academic staff average)  
was to put in a teaching claim (hence invoking the :term:`Teaching Uplift`), the *actual* hourly rate would be: 

.. math::

    £21.52 \times \frac{1931.4}{1613.2} \times 1.3214 = £34.04

On top of this, the employer's :term:`National Insurance Contribution` (up to 13.2% depending on the hours worked) 
and :term:`Pension Contribution` (up to 16.2% depending on the employee's pension scheme and time of year) increase 
the cost accordingly: 

.. math:: 

    £34.04 \times 13.2\% \times 16.2\% = £44.77

So in summary, the actual hourly rate of pay can be up to 58\% higher than the basic rate, 
and the hourly cost to the conservatoire can be up to 108\% higher (more than double) the basic hourly rate. 

.. _fractional-pay:

Fractional Academic Pay
-----------------------

Fractional Academic salaries are probably the most complex. Skip to the :ref:`fractional-pay-hourly` section 
for a summary of the impact. 

Full calculation
~~~~~~~~~~~~~~~~

Due to a rounding error in the historic calculation of a :term:`Fractional Academic`'s FTE, fractional salaries 
are very slightly higher than a non-fractional salary at the same point in the pay framework. 

We first define the following variables: 

.. math::

    a &:= \text{Total hours to be worked, from the fractional contract} \\
    b &:= \text{Full time hours according to employee's contract of employment} \\
    c &:= \text{Holiday hours according to employee contract} \\
    d &:= \text{Employee's pro rata salary, i.e. salary if FTE was 1.0}

The important derivates are: 

.. math::

    \gamma &= \text{Historic full-term-time hours} \\
            &= 1110 + 1110\frac{c}{b} \\
            &= 1110 (1 + \frac{c}{b}) \\
    \\
    \beta  &= \text{Paid hours (worked hours plus holiday accrual)} \\ 
            &= a (1 + \frac{c}{b}) \\
    \\
    \delta &= \text{Modifier used for rounding in old calculation} \\
            &= 0.499999 \\
    \\
    \theta &= \text{Historic term-time FTE (explained above)} \\ 
            &= \frac{100\beta}{\gamma} + \delta \\
    

The historic salary calculation is defined as follows: 

.. math::

    \text{Salary} = \frac{\text{fraction}}{100} \times \text{FTE} \times \frac{\text{Full-term-time-hours}}{\text{Contract work} + \text{Contract holiday}}

Using the above abbreviations, we can represent and subsequently decompose it accordingly: 

.. math::

    \text{Salary} &= \frac{\theta}{100} \times d \times \frac{\gamma}{b + c} \\
    &= \frac{(\frac{100(1+\frac{c}{b})a}{\gamma} + \delta)d\gamma}{100(b+c)}  \\
    &= \left(\frac{a(b+c)}{b(b+c)}+\frac{\delta \gamma}{100(b+c)}\right) d \\
    &= \left(\frac{a}{b}+\frac{1110\delta(1+\frac{c}{b})}{193140}\right) d

We can then define the fixed part of the error term explicitly to give a simpler representation of the salary calculation, 
and calculate the actual terms for each type of contract:

.. math::

    \epsilon &= \frac{1110\delta}{193140} \\
                &= 0.002873557 \text{(exactly)}  \\
    \\
    \text{Salary} &= \left(\frac{a}{b} + \left(1+\frac{c}{b}\right)\epsilon\right)\delta \\
    &= \frac{a+(b+c)\epsilon}{b}d \\
    &= \begin{cases}
    (\frac{a}{b}+0.0035)d,  &  \text{Old contract} \\
    (\frac{a}{b}+0.0034)d,  &  \text{New contract} 
    \end{cases}
    
This result is intuitively correct: it shows that a fractional FTE is the number of hours 
worked as a proportion of the maximum number of hours workable (the :math:`\frac{a}{b}` term), 
plus a small extra from the error term, which is equivalent to about :math:`5\frac{1}{2}` hours additional work. 
In financial terms, this translates to 
an absolute increase in salary of between £100 and £200 per member of fractional staff. 

The calculation shown above is contained by the function ``udfFracFTE``. 

.. _fractional-pay-hourly:

Example Fractional Salary
~~~~~~~~~~~~~~~~~~~~~~~~~

Fractional contract salary is calculated as follows:

.. math::
    
    \text{Basic hourly rate} \times \text{Holiday accrual} \times \text{Hours Worked} + \text{FTE Salary} \times \text{Error term} 

Consider a member of academic staff on the new contract (see :term:`Age of Contract`) with a *basic* 
hourly rate of £21.52 (the academic staff average) and therefore a full-time equivalent salary of £41,526. This member of staff 
has 5 contracted hours of teaching (which incurrs preparation time, as per the :term:`Teaching Uplift`) 
per week for 20 weeks, and therefore they have :math:`5\times1.3214\times20=132` total contracted hours. 

The salary is then calculated as follows:

.. math::

    £21.52 \times \frac{1931.4}{1613.2} \times 132 + £41,526 \times 0.0034 = £3,542

The actualy hourly rate for the teaching is therefore :math:`£3,542\div(5\times20)=£35.42`. 
Note that this is higher than the hourly rate would be if the same work was done 'on claim' (see :ref:`claim-pay-hourly` above).  
