Glossary
========

.. glossary::
    :sorted:
    
    On-costs

        These are the costs of employment beyond basic salary. Typically, in addition to paying an employee's 
        hourly rate for the number of hours worked, 
        the institution will also pay **National Insurance** contributions, **Pension** contributions 
        (which are distinct from the *employee*\ 's NI and Pension contributions, 
        paid by the employee along with income tax) and 
        the smaller `Apprenticeship Levy <https://www.gov.uk/government/publications/apprenticeship-levy/apprenticeship-levy>`_.

        In the cases of :term:`Fractional Academic` posts and Casual posts, there is also a 'holiday accrual' on-cost: 
        this is an increase to the hourly rate derived from the amount of holiday pay 
        that an employee would have recieved, had the work been contracted. 
        
        Additionally, Fractional staff also incur the :term:`Teaching Uplift` (for when they are teaching), which is 
        often considered to be an on-cost. 
        Holiday Accrual and the Teaching Uplift can be a source of confusion and mis-perception of the 
        hourly rate of 'Fractional' staff, because it is sometimes stated as the amount *before* the application of 
        holiday accrual or the teaching uplift. In reality, all work done by 'Fractional' staff incurs the holiday accrual, 
        and most of it incurs the teaching uplift.  
 
    Teaching Uplift

        An employee's hourly rate is increased when they are teaching, on the premise that on average, 
        each hour of teaching incurs 19 minutes and 17 seconds minutes of preparation time. 
        Therefore, an employee's hourly rate is increased by 32.14% when they are teaching (but not assessing). 

        The 19 minutes and 17 seconds is usually rounded to 20 minutes in communications, but this is only a shorthand: 
        the 32.14% uplift is what is actually applied. 


    Academic Year

        Throughout this project, 'academic year' refers to the calendar year in which an academic year begins. 
        It crops in several tables and views and is **always** a four-digit integer. For example, 
        the 'value' of the academic year for the 20/21 academic year would be 2020. 

        Enforcing this not only assures consistency throughout the project, but also allows for simple arithmetic with years, 
        and avoids use of the often-contentious '/' character.


    Full-Time-Equivalent

        A number between zero and one, which indicates the number of hours worked in a year: an FTE of 0 indicates a post with 
        no contracted hours (a.k.a. a 'zero-hours' contract); an FTE of 1 indicates a post with the maximum number of 
        workable hours in a year. 

        The number of hours that constitutes an FTE of 1.0 varies according to an employee's contract. 
        For the majority of staff, 
        an FTE of 1.0 is equivalent to working 1,613.2 hours across the year, whilst for a small number of staff 
        (on an older contract) an FTE of 1.0 is equivalent to working 1,576.2 hours across the year. 

    Fractional Academic

        This is a type of post that has a new 'Fractional Contract' each year, which details what the post will teach or assess in that year. 

        Though fractional academic staff costs are grouped under 'flexible costs', they are not actually flexible: 
        the institution is obligated to keep the total number of hours contracted broadly consistent between years, 
        where possible; they are therefore more accurately described as *variable* costs.

        The word 'fraction' is a reference to when the institution provided Further Education: at this time, a 
        contract's 'fraction' 
        was the proportion of the total FE term time spent teaching. It is therefore analogous to 
        a 'Full-Time-\ **Term-Time**\ -Equivalent, which would be a larger number than the 
        commonly-used :term:`Full-Time-Equivalent`.  

        Teaching contracts therefore had both an FTE *and* a Fraction. The 'fraction' figure disappeared from the teaching contracts in 2017. 
        Historically, the 'fraction' concept has also been used with term-time pastoral posts, but is no longer in common use.  

        Fractional Academic salaries are calculated differently to most: see the following section ofr more details. 

    Fractional Academic Salary

        Due to a rounding error in the historic calculation of a :term:`Fractional Academic`'s FTE, fractional salaries are very slightly higher than 
        a non-fractional salary at the same point in the pay framework. 

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

            \text{Salary} &= \frac{\frac{100\beta}{\gamma} + \delta}{100} \times d \times \frac{\gamma}{b + c} \\
            &= \frac{(\frac{100(1+\frac{c}{b})a}{\gamma} + \delta)d\gamma}{100(b+c)}  \\
            &= \left(\frac{a(b+c)}{b(b+c)}+\frac{\delta \gamma}{100(b+c)}\right) d \\
            &= \left(\frac{a(b+c)}{b(b+c)}+\frac{1110\delta(1+\frac{c}{b})}{193140}\right) d

        We can then define the fixed part of the error term explicitly to give a simpler representation of the salary calculation, and calculate the actual 
        terms for each type of contract:

        .. math::

            \epsilon &= \frac{1110\delta}{193140} \\
                     &= 0.002873557  \\
            \\
            \text{Salary} &= \left(\frac{a}{b} + \left(1+\frac{c}{b}\right)\epsilon\right)\delta \\
            &= \frac{a+(b+c)\epsilon}{b}d
            &= \begin{cases}
            (\frac{a}{b}+0.0035)d,  &  \text{Old contract} \\
            (\frac{a}{b}+0.0034)d,  &  \text{New contract} 
            \end{cases}
            
        This shows that a fractional FTE is the number of hours worked as a proportion of the maximum number of hours workable (the :math:`\frac{a}{b}` term), 
        plus a small extra from the error term, which is equivalent to about :math:`5\frac{1}{2}` hours additional work. In financial terms, this translates to 
        an absolute increase in salary of between £100 and £200 per member of fractional staff. 
        
        
         

