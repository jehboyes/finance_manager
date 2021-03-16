"""

Standard table prefixes are used on the database tables for easier navigation/organisation.
Note however that these are **not** used in the class names, for brevity. 


*  **fs_** for tables that are part of the financial structure
*  **f_** for tables that hold and structure actual finance data
*  **input_** for tables that are used directly by the interface
*  **staff_** for the various lookups used exclusively by the pay_staff table
*  **conf_** for confguration values, intended to be static

.. note::

    If altering a table, use the `alembic <https://alembic.sqlalchemy.org/en/latest/>`_ module to migrate to the database.


.. contents:: Contents
    :local:
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, CHAR, BOOLEAN, VARCHAR, DECIMAL, DATE, INTEGER, create_engine, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.mssql import DATETIME
from finance_manager.functions import periods

# Standard financial decimal
_FDec = DECIMAL(precision=18, scale=2)

# Define the database base class, to hold the database info
Base = declarative_base()


def _period_cols(datatype):
    """Returns a list of period columns, 

    This exists to save writing out 12 columns in the several tables that need a column for each period, 
    which is both time and error-saving. Resultant columns are named p1, ..., p12, and have the provided datatype. 

    Attributes
    ----------
    datatype : datatype
        An SQLAlchemy datatype.  

    Returns
    -------
    sqlalchemy.Column
        12 SQLAlchemy Column objects, each named for a period.  
    """
    return [Column(f'p{n}', datatype, server_default='0')
            for n in periods()]


class directorate(Base):
    """
    A directorate.  

    Each is a set of departments, overseen by one director. 

    Attributes
    ----------
    directorate_id : str
        A one-letter ID for the directorate. 
    description : str
        The name of the department. 
    director : str
        The **login name** for the Director. 
    director_name : str
        The name to appear on documentation. 
    """
    __tablename__ = "fs_directorate"

    directorate_id = Column(CHAR(1), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    director = Column(VARCHAR(50))
    director_name = Column(VARCHAR(100))

    cost_centres = relationship("cost_centre", back_populates="directorate")


class cost_centre(Base):
    """
    Standard 6-character cost centres. 

    Generally corresponds to a department. Each cost centre is part of a directorate. 

    Attributes
    ----------
    costc : str
        Six character cost centre code. Consistent with central finance system. 
    description : str
        The name of the cost centre. Does not have to be consistent with Finance system.
    directorate_id : str
        The 1 character identifier of the directorate to which this cost centre belongs. 
    owner : str
        Login name of the cost centre owner. 
    supercede_by : str
        If this cost centre is no longer in use, it must be superceded by an un-superceded 
        cost centre.  
    password : str
        The password of the 20/21 BP3 workbooks. Reference only. 
    """
    __tablename__ = "fs_cost_centre"

    costc = Column(CHAR(6), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    directorate_id = Column(CHAR(1), ForeignKey(
        "fs_directorate.directorate_id", ondelete="CASCADE"), nullable=False)
    owner = Column(VARCHAR(50), nullable=False)
    supercede_by = Column(CHAR(
        6), nullable=True, comment="Use to indicate where a cost centre subsumes this one going forward")
    password = Column(VARCHAR(50), nullable=True,
                      comment="Legacy vegan password from excel era")

    directorate = relationship("directorate", back_populates="cost_centres")


class report_cat_a(Base):
    """
    A reporting category.  

    Student-friendly categories. Lower level than cat b. 

    Attributes
    ----------
    rep_cat_a_id : str
        3 character ID for the category.
    rep_cat_b_id : str
        2 character ID for the category. 
    description : str
        The name of the category. 
    """
    __tablename__ = "fs_reporting_cat_a"

    rep_cat_a_id = Column(CHAR(3), primary_key=True)
    rep_cat_b_id = Column(CHAR(2), ForeignKey(
        "fs_reporting_cat_b.rep_cat_b_id"))
    description = Column(VARCHAR(50), nullable=False)


class report_cat_b(Base):
    """
    A reporting category.  

    Student-friendly categories. Parent to rep_cat_a. 

    Attributes
    ----------
    rep_cat_b_id : str
        Three character ID for the category. 
    description : str
        The name of the category. 
    """
    __tablename__ = "fs_reporting_cat_b"

    rep_cat_b_id = Column(CHAR(2), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)


class f_set_cat(Base):
    """
    Set categories. 

    BP1, forecast P3 etc. 

    Attributes
    ----------
    set_cat_id : str
        3 character ID for the set category. 
    description : str
        Name of the set category. 
    is_forecast : BOOLEAN
        Boolean to indicate if the set is being constructed in detail, or using the top-level forecasting mechanism.  
    """
    __tablename__ = "f_set_cat"
    set_cat_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))
    is_forecast = Column(BOOLEAN())

    f_sets = relationship("f_set", back_populates="category")


class forecast_config(Base):
    """
    Configures displaying forecast sets. 

    Defines which set_cat and year should appear alongside the given set_cat and acad_year 
    combination. Several of these fields may seem trivial, such as having a year and 
    previous year, but may allow for more complex scenarios in future. 

    Attributes
    ----------
    set_cat_id : str
        3 Character ID of the set being configured. 
    acad_year_main : int
        Year being configured. 
    split_at_period : int
        The period before figures are being entered for. For example, 6 would indicate P1:6|P7:12. 
    comp_set_cat_a : str 
        The set category to be used for the first comparator (probably actuals). 
    comp_acad_year_a : int
        The academic year of cat a. 
    comp_set_cat_b : str 
        The set category to be used for the second comparator: could be a budget, or a forecast. Uses acad_year_main.  
    comp_set_cat_main : str 
        The set category to be used for the actuals being constructed against. 
    """
    __tablename__ = "conf_forecast"

    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id"), primary_key=True)
    acad_year = Column(INTEGER(), primary_key=True)
    split_at_period = Column(INTEGER())
    comp_set_cat_a = Column(CHAR(3), ForeignKey("f_set_cat.set_cat_id"))
    comp_acad_year_a = Column(INTEGER())
    comp_set_cat_b = Column(CHAR(3), ForeignKey("f_set_cat.set_cat_id"))
    comp_set_cat_main = Column(CHAR(3), ForeignKey("f_set_cat.set_cat_id"))


class f_set(Base):
    """
    :: _set:
    Finance sets

    Integral part of data structure. Unique by acad_year, costc, category. For example,
    there can only be 1 2020 BP3 MA1600.

    Attributes
    ----------
    set_id : int
        ID for a set (autogenerated).
    acad_year : int
        See :term:`Academic Year`.
    costc : str
        The cost centre ID. 
    set_cat_id : str
        Set category ID. 
    curriculum_id : int
        ID of the curriculum used within the Curriculum Model. 
    curriculum_hours : decimal
        From CM; updated manually to reflect Luminate ownership philosophy. 
    student_number_usage_id : str
        ID for the student number usage. See the ``student_number_usage`` table of the 
        curriculum model database.  
    allow_student_number_change : BOOLEAN
        Boolean that designates whether or not users can alter changes within the Powerapp. 
        Typically, this will be '0' for actuals, and '1' for Business Planning. 
    closed : BOOLEAN
        Boolean that indicates whether or not this set is closed for further edits. CHanges can be made, but 
        they will not be reflected in the finances.   
    """
    __tablename__ = "f_set"
    set_id = Column(INTEGER(), primary_key=True)
    acad_year = Column(INTEGER(), nullable=False)
    costc = Column(CHAR(6), ForeignKey(
        "fs_cost_centre.costc", ondelete="CASCADE"), nullable=False)
    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id", ondelete="CASCADE"), nullable=False)
    curriculum_id = Column(
        INTEGER())
    curriculum_hours = Column(DECIMAL(20, 5))
    student_number_usage_id = Column(VARCHAR(100))
    allow_student_number_change = Column(BOOLEAN(), server_default="0")
    closed = Column(BOOLEAN(), server_default="0")
    surpress = Column(BOOLEAN(), server_default="0")
    # Add unique constraint on year, cost centre and set code
    __table_args__ = (Index('IX_f_set',
                            'costc', 'acad_year', 'set_cat_id', unique=True),)
    category = relationship("f_set_cat", back_populates="f_sets")


class conf_set_hide(Base):
    """Configures visibility of set in UI. 

    Combinations of set_cat_id and acad_year in this table 
    will be removed from the UI permissions views (and therefore
    are not selectable).  

    Attributes
    ----------
    acad_year : int
        See :term:`Academic Year`.
    set_cat_id : str
        Set category ID. 
    """
    __tablename__ = "conf_set_hide"

    acad_year = Column(INTEGER(), nullable=False, primary_key=True)
    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id", ondelete="CASCADE"), primary_key=True)


class conf_shared_service(Base):
    """Configures shared service rows. 

    Row for each shared service that may be used. 

    Attributes
    ----------
    costc : str
        Cost centre of the service. Note that this should not appear in ``fs_cost_centre``.
    description : str
        Description of this external cost centre. 
    """
    __tablename__ = "conf_shared_service"

    costc = Column(CHAR(6), primary_key=True)
    description = Column(VARCHAR(50))


class transaction_type(Base):
    """Type of the transaction. 

    Indicates the type of document the transaction relates to. 

    Attributes
    ----------
    status_id : str
        1 character ID for the status. 
    description : str
        Description of the status.
    """
    __tablename__ = "f_transaction_type"
    type_id = Column(CHAR(2), primary_key=True)
    description = Column(VARCHAR(50))


class transaction_status(Base):
    """Approval status of the transaction. 

    Transactions go through different stages of approval, denoted by this table. 

    Attributes
    ----------
    status_id : str
        1 character ID for the status. 
    description : str
        Description of the status.
    """
    __tablename__ = "f_transaction_status"
    status_id = Column(CHAR(1), primary_key=True)
    description = Column(VARCHAR(255))


class transaction(Base):
    """Actual financial transactions. 

    Underpins an eaiser way of viewing transactions from the finance system. 
    Though transactions are obviously 'actuals', they should only relate to forecast 
    sets, because forecast sets are informed by actual transactions. 

    Attributes
    ----------
    f_t_id : int
        ArBOOLEANrary primary key (exists for SQL Alchemy's sake).
    set_id : int
        ID of the set to which this transaction belongs. 
    transaction_id : str
        8 character numeric string for transaction ID from finance system. 
    account : str
        4 character account ID. 
    period : int
        Financial period (in year). 
    status_id : str
        Approval status of transaction.
    type_id : str
        Type of transaction.
    dt : datetime
        Date of transaction
    supplier_name : str
        Name of the supplier - can be None. 
    description : str
        Description of the transaction. 
    amount : float
        Value of transaction.
    """
    __tablename__ = "f_transaction"
    f_t_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                    mssql_identity_start=1000, mssql_identity_increment=1)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    transaction_id = Column(CHAR(8), nullable=False)
    account = Column(CHAR(4), ForeignKey("fs_account.account"), nullable=False)
    period = Column(INTEGER(), nullable=False)
    status_id = Column(CHAR(1), ForeignKey(
        "f_transaction_status.status_id"), nullable=False)
    type_id = Column(CHAR(2), ForeignKey(
        "f_transaction_type.type_id"), nullable=False)
    dt = Column(DATETIME(), nullable=False)
    supplier_name = Column(VARCHAR(100), nullable=True)
    description = Column(VARCHAR(255), nullable=False)
    amount = Column(_FDec)


class hfi_bursary(Base):
    """
    Higher Fee Bursary

    Sets the proportion of HE fees that are paid *back out* as bursaries.

    Attributes
    ----------
    acad_year : int
        See :term:`Academic Year`.
    set_cat_id : str
        Set category ID to apply the proportions to. 
    hfi_prop : float
        Proportion of the gross HE student fee that is designated 'higher' fee income.
    bursary_prop : float
        Proportion of the HFI income paid out as bursaries. 
    """
    __tablename__ = "conf_hfi_bursary"
    acad_year = Column(INTEGER(), primary_key=True)
    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id"), primary_key=True)
    hfi_prop = Column(
        DECIMAL(9, 8), comment="Higher Fee Proportion, for calculating bursary")
    bursary_prop = Column(
        DECIMAL(9, 8), comment="Proportion of HFI paid as bursaries")


class fee_loss(Base):
    """
    Default fee loss.

    Sets the proportion of HE fees that will be lost to withdrawal and suspension.

    Attributes
    ----------
    acad_year : int
        See :term:`Academic Year`.
    set_cat_id : str
        Set category ID to apply the proportions to. 
    status : str {H,O}
        Fee status. 
    rate : float
        Proportion of gross fee income that will be lost. 
    """
    __tablename__ = "conf_fee_loss"
    acad_year = Column(INTEGER(), primary_key=True)
    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id"), primary_key=True)
    status = Column(CHAR(1), primary_key=True)
    rate = Column(DECIMAL(9, 8))


class finance_instance(Base):
    """
    An instance of finance records for a set. 

    Allows for viewing the finance history of a set.

    Attributes
    ----------
    instance_id : int
        Database-generated ID of the finance instance. 
    created_by : str
        Username that saved the instance. 
    set_id : int
        The set to which this instance belongs. 
    datestamp : datetime
        When this instance was created. 
    notes : str
        Any explanatory notes on the instance. 
    """

    __tablename__ = "f_finance_instance"

    instance_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                         mssql_identity_start=1000, mssql_identity_increment=1)
    created_by = Column(VARCHAR(50), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    datestamp = Column(DATETIME())
    notes = Column(VARCHAR(500), nullable=True)


class entry_type(Base):
    """
    Debit or Credit entry.

    Details how to adjust amount depending on whether they are a debit or credit. 

    Attributes
    ----------
    balance_type : str {DR, CR}
        Debit (DR) or Credit (CR). 
    coefficient : int
        Integer to convert amount to finance system 
        credit (negative) or debit (positive). 
    description : str {Credit, Debit}
        Debit or Credit. 
    """
    __tablename__ = "fs_entry_type"
    balance_type = Column(CHAR(2), primary_key=True)
    coefficient = Column(INTEGER(), nullable=False)
    description = Column(VARCHAR(6))
    accounts = relationship("account", back_populates='balance')


class account(Base):
    """
    A nominal (or general ledger) account.  

    Consistent with the finance system's accounts.  

    Attributes
    ----------
    account : str
        4 digit nominal account code. Must be consistent 
        with the central finance system. 
    description : str
        Name of the account.
    summary_code : int
        3 digit summary code ID to which this belongs.
    hide_from_users : BOOLEAN
        Whether or not the account is available for selection in the PowerApp. 
    default_balance : str {DR, CR}
        Denoting whether the account *should* have a Debit or Credit balance. 
    """
    __tablename__ = "fs_account"

    account = Column(CHAR(4), primary_key=True)
    description = Column(VARCHAR(50))
    summary_code = Column(CHAR(3), ForeignKey(
        "fs_summary_code.summary_code"), nullable=False)
    hide_from_users = Column(BOOLEAN(), server_default='0',
                             comment="Control ability to use in the app's 'Other' screens")
    default_balance = Column(CHAR(2), ForeignKey(
        "fs_entry_type.balance_type"), nullable=False)
    balance = relationship("entry_type", back_populates='accounts')


class report_cat_config(Base):
    """
    Configures the reporting category. 

    Attributes
    ----------
    costc : str
        6 Character cost centre code. 
    account : str
        4 Character account code. 
    rep_cat_a_id : str
        3 character ID of the reporting category A. 
    """
    __tablename__ = "fs_reporting_cat_config"
    costc = Column(CHAR(6), ForeignKey(
        "fs_cost_centre.costc"), primary_key=True)
    account = Column(CHAR(4), ForeignKey(
        "fs_account.account"), primary_key=True)
    rep_cat_a_id = Column(CHAR(3), ForeignKey(
        "fs_reporting_cat_a.rep_cat_a_id"))


class summary_code(Base):
    """
    Summary Code 

    A higher level of account, aggregates several accounts to the level prescribed
    by Luminate. 

    Attributes
    ----------
    summary_code : int 
        3 digit ID for the summary. 1XX is income, 2XX pay, 3XX nonpay, 
        4XX capex, 5XX internal
    description : str
        Describe the summary code, as per Luminate category. 
    section_id : str
        Section ID of where this summary appears in a SOCI.
    position : int
        Determines the order in which these categories are displayed. 
        """
    __tablename__ = "fs_summary_code"
    summary_code = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    sub_section_id = Column(CHAR(5), ForeignKey(
        "fs_sub_section.sub_section_id"))
    position = Column(INTEGER())
    default_account = Column(CHAR(4), nullable=True)
    explanation = Column(VARCHAR(255))


class finance_sub_section(Base):
    """
    Sub-section in a SOCI. 

    A subtotal-ed sub-section in a statement of consolidated income. 

    Attributes
    ----------
    sub_section_id : str
        Five character ID for the sub-section. 
    description : str
        Name for the sub-section. 
    show_in_ui : BOOLEAN
        Whether or not to display this section in the PowerApp. 
    position : int
        How to order the sections when displaying. 
    """
    __tablename__ = "fs_sub_section"

    sub_section_id = Column(CHAR(5), primary_key=True)
    description = Column(VARCHAR(50))
    section_id = Column(CHAR(3), ForeignKey("fs_section.section_id"))
    line_order = Column(INTEGER())
    explanation = Column(VARCHAR(255))


class finance_section(Base):
    """
    Section in a SOCI. 

    A subtotal-ed section in a statement of consolidated income. 

    Attributes
    ----------
    section_id : str
        Three character ID for the section. 
    description : str
        Name for the section. 
    show_in_ui : BOOLEAN
        Whether or not to display this section in the PowerApp. 
    position : int
        How to order the sections when displaying. 
    """
    __tablename__ = "fs_section"

    section_id = Column(CHAR(3), primary_key=True)
    super_section_id = Column(CHAR(1), ForeignKey(
        "fs_super_section.super_section_id"))
    description = Column(VARCHAR(50))
    show_in_ui = Column(BOOLEAN())
    position = Column(INTEGER())
    explanation = Column(VARCHAR(255))


class finance_super_section(Base):
    """
    Super section in a SOCI. 

    A total section in a statement of consolidated income. 

    Attributes
    ----------
    section_id : str
        1 character ID for the section. 
    description : str
        Name for the section. 
    show_in_ui : BOOLEAN
        Whether or not to display this section in the PowerApp. 
    position : int
        How to order the sections when displaying. 
    """
    __tablename__ = "fs_super_section"

    super_section_id = Column(CHAR(1), primary_key=True)
    description = Column(VARCHAR(50))
    show_in_ui = Column(BOOLEAN())
    position = Column(INTEGER())
    explanation = Column(VARCHAR(255))


class finance(Base):
    """
    A finance record. 

    Unique by finance instance, account and period. 

    Attributes
    ----------
    instance_id : int
        Database-generated identifier for the finance row. 
    account : char
        4 digit account, see account. 
    period : int
        Accounting period. 
    amount : float 
        Amount on given account in given period. 
    """
    __tablename__ = "f_finance"

    instance_id = Column(INTEGER(), ForeignKey(
        "f_finance_instance.instance_id", ondelete="CASCADE"), primary_key=True)
    account = Column(CHAR(4), ForeignKey(
        "fs_account.account"), primary_key=True)
    period = Column(INTEGER(), primary_key=True)
    amount = Column(_FDec)


class forecast(Base):
    """Forecast values. 

    Attributes
    ----------
    forecast_id : int
        Unique ID for the foecast line. 
    set_id : int
        Set to which this forecast line belongs (unique with summary code).
    summary_code : int
        Summary code the record relates to (unique with set ID). 
    amount : float
        Financial amount. 
    """
    __tablename__ = "input_forecast"

    forecast_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                         mssql_identity_start=1000, mssql_identity_increment=1)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"))
    summary_code = Column(CHAR(3), ForeignKey(
        "fs_summary_code.summary_code"))
    amount = Column(_FDec)
    notes = Column(VARCHAR(255))
    # Add unique constraint on set and summary
    __table_args__ = (Index('IX_input_forecast',
                            'set_id', 'summary_code', unique=True),)


class inc_courses(Base):
    """
    Input table for non-HE courses. 

    Used by Junior LC and Short Courses. 

    Attributes
    ----------
    courses_id : int 
        Database-generated ID for the course income line. 
    course_name : str
        Description of the course. 
    students : int
        Number of students to enrol in the year. 
    fee : float
        Individual fee. 
    set_id : int
        ID of the set to which this row belongs. 
    P1_to_P12 : float
        Field for each of the twelve periods. 
    """
    __tablename__ = 'input_inc_courses'
    courses_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                        mssql_identity_start=1000, mssql_identity_increment=1)
    course_name = Column(VARCHAR(50), nullable=True)
    students = Column(INTEGER(), autoincrement=False, nullable=True)
    fee = Column(_FDec, nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    # Add period cols
    __table_args__ = (*_period_cols(_FDec),)


class inc_other(Base):
    """
    Other income lines. 

    Any income not from student fees. 

    Attributes
    ----------
    inc_id : int 
        Database generated ID for the income line. 
    account : str
        Nominal account. 
    description : str
        Description of the income line. 
    project_id : int
        Optional project identifier, to link with related income & expenditure.     
    set_id : int
        ID of the set. 
    """
    __tablename__ = 'input_inc_other'
    inc_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                    mssql_identity_start=1000, mssql_identity_increment=1)
    account = Column(CHAR(4), nullable=True)
    description = Column(VARCHAR(1000), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    project_id = Column(INTEGER(), ForeignKey(
        "input_project.project_id"), nullable=True)

    # Add period cols
    __table_args__ = (*_period_cols(_FDec),)


class inc_bursary(Base):
    """
    Non-standard bursaries. 

    Bursaries other than the standard conservatoire bursary. 

    Attributes
    ----------
    bursary_id : int
        Database-generated ID for the bursary line. 
    set_id : int
        ID of the set to which the bursary line belongs. 
    description : str
        Description of the bursary. 
    amount : float
        Value of the bursary. 
    number : int
        Number of bursaries to award. 
    status : int
        Fee stats of the students eligible for the bursary. Dictates which income 
        line the bursary will reduce.  
    """
    __tablename__ = 'input_inc_bursary'

    bursary_id = Column(INTEGER(), autoincrement=True,
                        mssql_identity_start=1000, mssql_identity_increment=1, primary_key=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"))
    description = Column(VARCHAR(250), nullable=True)
    amount = Column(_FDec, nullable=True)
    number = Column(INTEGER(), nullable=True)
    status = Column(CHAR(1), nullable=True)


class inc_grant(Base):
    """
    Grant income. 

    Not linked to a set, instead an academic year and set category. 

    Attributes
    ----------
    acad_year : int
        See :term:`Academic Year`.
    set_cat_id : str
        ID of the set category to which this grant belongs.  
    high_cost_funding : float
        Amount of OfS Bursary recieved as high cost course funding. 
    access_funding : float
        Amount of Access and Participation grant recieved. 
    capital_grant : float 
        Amount of capital grant to be paid in year. 

    """
    __tablename__ = 'input_inc_grant'

    acad_year = Column(INTEGER(), primary_key=True)
    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id"), primary_key=True)
    high_cost_funding = Column(
        _FDec, comment="Funding for high-cost courses.", server_default='0')
    access_funding = Column(
        _FDec, comment="Funding for student access and success.", server_default='0')
    capital_grant = Column(
        _FDec, comment="Total amount of OfS Grant to be recieved.", server_default='0')


class inc_feeloss(Base):
    """
    Fee loss rate. 

    Proportion of fee that will be lost to student withdrawal or 
    suspension in year. 

    Attributes
    ---------- 
    set_id : int
        ID of the set t which this fee loss belongs. 
    status : str {H, O}
        Student fee status that the rate applies to.
    rate : float 
        The fee loss rate to apply. 
    """
    __tablename__ = 'input_inc_feeloss'

    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), primary_key=True)
    status = Column(CHAR(1), primary_key=True)
    rate = Column(DECIMAL(precision=10, scale=5), nullable=True)


class pay_fracclaim(Base):
    """
    Fractional Claim Amount. 

    Number of hours, by period, to move from fractional costs and into claim costs. 

    Attributes
    ----------
    period : int
        Number of the period in which the fractional claims would be moved to. 
    hours : float 
        Number of hours to move to claims. 
    set_id : int
        ID of the set to which the fractional claim line belongs. 
    """
    __tablename__ = 'input_pay_fracclaim'

    period = Column(INTEGER(), nullable=True, primary_key=True)
    hours = Column(DECIMAL(precision=18, scale=5), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"),
                    primary_key=True,  nullable=False)


class claim_type(Base):
    """
    Type of claim.

    Determines how to adjust the input rate of pay. 

    Attributes
    ----------
    claim_type_id : str
        3 character ID for the claim type. 
    description : str
        Description of the claim type. 
    variable_rate : BOOLEAN
        Whether or not the rate for this claim type is variable (i.e. can be 
        entered by the end user). 
    base_multiplier : float
        Proportion by which to change the base entered rate, e.g. 1.3412 for teaching.
    holiday_multiplier : float 
        Proportional amount of holiday pay to apply.
    rate_uplift : float
        amount ot add to the rate. Useful in conjunction with the ``variable_rate``.
    apply_ni : BOOLEAN
        Whether or not to add national insurance to the claim costs.
    apply_pension : BOOLEAN
        Whether or not to add pension costs to the claim line.  
    """
    __tablename__ = "input_pay_claim_type"

    claim_type_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))
    variable_rate = Column(BOOLEAN())
    base_multiplier = Column(DECIMAL(10, 5))
    holiday_multiplier = Column(DECIMAL(10, 5))
    rate_uplift = Column(_FDec)
    apply_ni = Column(BOOLEAN())
    apply_pension = Column(BOOLEAN())


class pay_claim(Base):
    """
    Pay Claim line. 

    A claim line. 

    Attributes
    ----------
    claim_id : int
        Database-generated ID for the pay claim line. 
    set_id : int
        ID of the set to which the claim belongs. 
    account : str
        Account number. 
    description : str
        Description or rationale for the claim amount.
    rate : float 
        Base hourly rate for the claim. 
    claim_type_id : str
        ID for the claim type. Will affect the rate. 
    P1_to_P12 : float
        Field for each of the twelve periods. 
    project_id : int
        Optional project identifier, to link with related income & expenditure.     
    """
    __tablename__ = "input_pay_claim"

    claim_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                      mssql_identity_start=1000, mssql_identity_increment=1)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"))
    account = Column(CHAR(4), ForeignKey("fs_account.account"))
    description = Column(VARCHAR(1000))
    rate = Column(_FDec)
    project_id = Column(INTEGER(), ForeignKey(
        "input_project.project_id"), nullable=True)
    claim_type_id = Column(CHAR(3), ForeignKey(
        "input_pay_claim_type.claim_type_id"))
    # Add period cols
    __table_args__ = (*_period_cols(DECIMAL(10, 5)),)


class pay_staff(Base):
    """
    Details staffing. 

    Staffing in a given set. 

    Attributes
    ----------
    post_status_id : str
        ID of the post. 
    post_type-id : str 
        ID of the post's type. 
    title  : str
        Title of the post. 
    name : str
        Name of the postholder. 
    staff_id : str 
        Institutional ID of the postholder. Used for cross referencing between departments, 
        which allows more accurate calculation of National Insurance.  
    post_id : str
        Institutional ID of the post. Does not need to be unique by post. 
    start_date : date
        When the post was occupied. 
    end_date : date
        When the post was/will be vacated. 
    grade : int
        Pay framework Grade number.
    current_spine : int
        Pay framework spine point. 
    indicative_fte : float
        Full Time Equivalent of the post, where full time is 1.0 for 37 hours a week 
        (with holiday). 
    allowances : float
        An absolute amount to add to he salary. 
    con_type_id : int
        ID of the contract the postholder is on. 
    pension_id : str
        ID of the pension scheme in which the post is enrolled.
    travel_scheme : float
        Amount of academic travel scheme to be paid to the postholder over the year.
    teaching_hours : float 
        Number of 'fractional' hours taught by non-fractional academics. 
    assessing_hours : float 
        Number of 'fractional' hours assessed by non-fractional academics. 
    coordination_hours : float 
        Number of 'fractional' hours coordinated by non-fractional academics. 
    set_id : int
        ID of the set to which the post belongs. 
    staff_line_id : int
        ID for the staff line. 
    notes : str
        Open text notes for the post. 
    """
    __tablename__ = "input_pay_staff"

    post_status_id = Column(CHAR(4), ForeignKey(
        "staff_post_status.post_status_id"), nullable=True)
    post_type_id = Column(CHAR(5), ForeignKey(
        "staff_post_type.post_type_id"), nullable=True)
    title = Column(VARCHAR(200), nullable=True)
    name = Column(VARCHAR(200), nullable=True)
    staff_id = Column(VARCHAR(8), nullable=True)
    post_id = Column(VARCHAR(50), nullable=True)
    start_date = Column(DATE(), nullable=True)
    end_date = Column(DATE(), nullable=True)
    grade = Column(INTEGER(), nullable=True)
    current_spine = Column(INTEGER(), ForeignKey(
        "staff_spine.spine"), nullable=True)
    indicative_fte = Column(DECIMAL(precision=10, scale=5), nullable=True)
    allowances = Column(_FDec,  nullable=True)
    con_type_id = Column(INTEGER(), ForeignKey(
        "staff_con_type.con_type_id"), nullable=True, server_default="2")
    pension_id = Column(VARCHAR(3), ForeignKey(
        "staff_pension.pension_id"), nullable=True)
    travel_scheme = Column(_FDec, nullable=True)
    teaching_hours = Column(DECIMAL(precision=10, scale=5),
                            nullable=True, server_default='0')
    assessing_hours = Column(DECIMAL(precision=10, scale=5),
                             nullable=True, server_default='0')
    coordination_hours = Column(DECIMAL(precision=10, scale=5),
                                nullable=True, server_default='0')
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    staff_line_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                           mssql_identity_start=1000, mssql_identity_increment=1)
    notes = Column(VARCHAR(255))


class post_type(Base):
    """
    Types of post. 

    This determines which accounts a post is costed to.  

    Attributes
    ----------
    post_type_id : str
        5 character ID for the post type. 
    description : str
        Description of the post type. 
    lcc_description : str
        Description of the post type used by Luminate. 
    salary_account : str
        Account the salary is recorded against. 
    ni_account : str
        Account the National Insurance is recorded against. 
    pension_account : str
        Account the Pension costs are recorded against.  
    """
    __tablename__ = 'staff_post_type'

    post_type_id = Column(CHAR(5), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    lcc_description = Column(VARCHAR(50), nullable=False)
    salary_account = Column(CHAR(4), ForeignKey("fs_account.account"))
    ni_account = Column(CHAR(4), ForeignKey("fs_account.account"))
    pension_account = Column(CHAR(4), ForeignKey("fs_account.account"))


class post_status(Base):
    """
    Status of the post. 

    Determines how the post is presented in the PowerApp. 

    Attributes
    ----------
    post_status_id : str
        4 character ID for the status. 
    description : str
        Description of the status. 
    exclude_from_finance : BOOLEAN
        Whether or not the costs of the post are included in the finances.
    colour_hex : str
        Colour hex string, in the format ``#rrggbbaa``, where ``aa`` is the alpha component. 
    """
    __tablename__ = 'staff_post_status'

    post_status_id = Column(CHAR(4), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    exclude_from_finance = Column(BOOLEAN(), server_default='0')
    colour_hex = Column(CHAR(9), server_default='#')
    luminate_description = Column(VARCHAR(50), nullable=True)


class spine(Base):
    """
    Spine Points. 

    Pay framework spine point values. Only stores the most recent version, as 
    the actual financial impact was recorded in 

    Attributes
    ----------
    acad_year : int
        See :term:`Academic Year`.
    set_cat_id : str
        3 character ID for the set category. 
    spine : int
        Spine point number. 
    value : float
        Annual salary of the spine point. 
    """
    __tablename__ = "staff_spine"
    acad_year = Column(INTEGER(),  primary_key=True)
    set_cat_id = Column(CHAR(3),  primary_key=True)
    spine = Column(INTEGER(), ForeignKey(
        "staff_spine_grade.spine"), primary_key=True)
    value = Column(_FDec)


class grade(Base):
    """
    Spine point grades

    Attributes
    ----------
    spine : int
        Spine point number
    grade : int 
        Grade number
    """
    __tablename__ = "staff_spine_grade"
    spine = Column(INTEGER(), primary_key=True)
    grade = Column(INTEGER())


class con_type(Base):
    """
    Type of contract. 

    This table allows for different types of contract to be used. 

    Parameters
    ----------
    con_type_id : int
        ID for the contract type. 
    set_cat_id : str
        3 character ID for the set category. 
    acad_year : int 
        See :term:`Academic Year`
    description : str
        Description of the contract. 
    work_hours : float 
        Number of hours of work. 
    hol_hours : float
        Number of hours of holiday.  
    """
    __tablename__ = "staff_con_type"

    con_type_id = Column(INTEGER(), primary_key=True)
    acad_year = Column(INTEGER(),  primary_key=True)
    set_cat_id = Column(CHAR(3),  primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    work_hours = Column(DECIMAL(10, 5), nullable=False)
    hol_hours = Column(DECIMAL(10, 5), nullable=False)


class pension(Base):
    """
    Pension schemes. 

    A pension scheme, relevant because of employer's contributions. See :term:`On-costs` for more detail. 

    Attributes
    ----------
    pension_id : str
        ID of the pension scheme. 
    description : str
        Diplay name of the pension scheme."""
    __tablename__ = "staff_pension"

    pension_id = Column(VARCHAR(3), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)


class pension_emp_cont(Base):
    """
    Employers pension contributions. 

    Exists for each month, for each pension scheme, for each year. 

    Attributes
    ----------
    pension_id : str
        ID of the pension scheme.
    acad_year : int
        See :term:`Academic Year`.
    P1_to_P12 : float
        Field for each of the twelve periods. 
    """
    __tablename__ = "staff_pension_contrib"

    pension_id = Column(VARCHAR(3), ForeignKey(
        "staff_pension.pension_id"), primary_key=True)
    acad_year = Column(INTEGER(), primary_key=True)
    # Add period cols
    __table_args__ = (*_period_cols(DECIMAL(6, 5)),)


class ni(Base):
    """
    National Insurance secondary threshold and rate. 

    Has one rate for year, and threshold by month.

    .. note::
        The rate also includes the apprenticeship levy. 

    Attributes
    ----------
    acad_year : int
        See :term:`Academic Year`. 
    rate : float
        Proportion of salary (above the threshold) to be paid as employer's contributions. 
    P1_to_P12 : float
        Threshold for each of the twelve periods. 

    """
    __tablename__ = 'staff_ni'

    acad_year = Column(INTEGER(), primary_key=True)
    rate = Column(DECIMAL(9, 8))
    # Add period cols
    __table_args__ = (*_period_cols(_FDec),)


class nonp_other(Base):
    """
    Non-pay expenditure. 

    This is any expenditure that is not employment. More detail (i.e. more lines and better descriptions) is encouraged where possible, for 
    transparency.  

    Attributes
    ----------
    nonp_id : int
        Database generated ID for the line. 
    account : str 
        Nominal account.
    description : str 
        Description of the expenditure. 
    P1_to_P12 : float
        Field for each of the twelve periods. 
    project_id : int
        Optional project identifier, to link with related income & expenditure.     
    """
    __tablename__ = 'input_nonp_other'
    nonp_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                     mssql_identity_start=1000, mssql_identity_increment=1)
    account = Column(CHAR(4), ForeignKey("fs_account.account"), nullable=True)
    description = Column(VARCHAR(1000), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    project_id = Column(INTEGER(), ForeignKey(
        "input_project.project_id"), nullable=True)

    # Add period cols
    __table_args__ = (*_period_cols(_FDec),)


class nonp_internal(Base):
    """
    Internal non-pay expenditue. 

    Records money moving within the institution, or within the group. 
    Each instance should be balanced by another instance in the contra cost centre.  

    Attributes
    ----------
    internal_id : int
        Database-generated ID for the internal income row. 
    description : str
        Description of the transaction. 
    costc : str, optional
        Cost centre of corresponding department. No foreign key as could be an external cost centre. 
    account : str
        Determines type of transaction. On the interface, this is restricted to the four combinations of I & E and Group & Internal. 
    amount : float
        Value of the transaction. 
    set_id : int
        ID of the set to which this line belongs. 
    """
    __tablename__ = "input_nonp_internal"

    internal_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                         mssql_identity_start=1000, mssql_identity_increment=1)
    description = Column(VARCHAR(50), nullable=True)
    costc = Column(CHAR(6),  nullable=True)
    account = Column(CHAR(4), ForeignKey("fs_account.account"), nullable=True)
    amount = Column(_FDec, nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)


class project(Base):
    """
    Project identifiers. 

    Means of linking co-dependant income & expenditure (including capital expenditure), 
    in order to easily view the net impact of a project.  

    Attributes
    ----------
    project_id : str
        An integer ID for the project. 
    title : str
        Short title of the project. 
    description : str
        Verbose description of the project.  
    """
    __tablename__ = "input_project"

    project_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                        mssql_identity_start=1000, mssql_identity_increment=1)
    title = Column(VARCHAR(50), nullable=False)
    description = Column(VARCHAR(255), nullable=True)


class capex_priority(Base):
    """
    Capital Expenditure Priority. 

    Simple lookup for prioritising capital expenditure projects. 

    Attributes
    ----------
    priority_id : str
        Description of the priority level. 
    ordering : int
        Integer by which to order priority. 
    """
    __tablename__ = "input_capex_priority"

    priority_id = Column(VARCHAR(50), primary_key=True)
    ordering = Column(INTEGER(), nullable=False)


class capex_reason(Base):
    """
    Capital Request Reasons. 

    Category of capital expenditure requirement.  

    Attributes
    ----------
    reason_id : str
        Unique title of the reason for expenditure.  
    """
    __tablename__ = "input_capex_reason"

    reason_id = Column(VARCHAR(50), primary_key=True)


class capex(Base):
    """
    Capital Expenditure.

    Detail of capital expenditure project. 

    Attributes
    ----------
    capex_id : int
        Database-generated ID for the capex row. 
    title : str
        Summary description of the proposal. 
    source : str
        Description of the source of the cost. 
    priority : str
        Priority level.
    reason : str
        Reason for request. 
    description : str
        Full descripton of the proposal. 
    amount_furniture : float
        Amount to be spent on furniture.
    amount_equipment : float
        Amount to be spent on equipment.
    amount_it : float
        Amount to be spent on IT.
    amount_building : float
        Amount to be spent on the bulding. 
    purchase_date : datetime
        Approximate prospective purchase date. 
    project_id : int
        Optional project identifier, to link with related income & expenditure. 
    set_id : int
        ID of the set to which this line belongs. 
    """
    __tablename__ = "input_capex"

    capex_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                      mssql_identity_start=1000, mssql_identity_increment=1)
    title = Column(VARCHAR(50), nullable=True)
    source = Column(VARCHAR(50), nullable=True)
    priority_id = Column(VARCHAR(50), ForeignKey(
        "input_capex_priority.priority_id"), nullable=True)
    reason_id = Column(VARCHAR(50), ForeignKey(
        "input_capex_reason.reason_id"), nullable=True)
    description = Column(VARCHAR(8000), nullable=True)
    amount_furniture = Column(_FDec, nullable=True, server_default="0")
    amount_equipment = Column(_FDec, nullable=True, server_default="0")
    amount_it = Column(_FDec, nullable=True, server_default="0")
    amount_building = Column(_FDec, nullable=True, server_default="0")
    purchase_date = Column(DATETIME(), nullable=True)
    project_id = Column(INTEGER(), ForeignKey(
        "input_project.project_id"), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)


class permission(Base):
    """
    Custom access permissions. 

    Entry on this table gives access to a cost centres via the UI. 

    .. note::

        Budget Holders and Directors are given access by virtue of their ownership statuses, and so do not need to be added to this list. 

    Attributes
    ----------
    costc : str
        Cost centre to be given access to. 
    login_365 : str
        Login name of the user to be given access. 
    """
    __tablename__ = "a_permission"

    costc = Column(CHAR(6), ForeignKey(
        "fs_cost_centre.costc"), primary_key=True)
    login_365 = Column(VARCHAR(50), primary_key=True)


class dt_cat(Base):
    """
    Categories of key dates. 

    Parameters
    ----------
    dt_cat_id : str
        4 character ID for the date category.
    description : str
        Description of the category.
    important : BOOLEAN
        Flag as important. 
    """
    __tablename__ = "a_dt_cat"

    dt_cat_id = Column(CHAR(4), primary_key=True)
    description = Column(VARCHAR(50))
    important = Column(BOOLEAN(), server_default="0")


class dt(Base):
    """
    Key dates to display in the app. 

    Just intended as a reference, and not mandatory. 

    Parameters
    ----------
    set_cat_id : str
        Set category ID. 
    acad_year : int
        See :term:`Academic Year`.
    dt : datetime
        Actual date and time of the key date. 
    description : str
        Description of what's happening on this date. 
    dt_cat_id : str
        Category of the date. 
    """
    __tablename__ = "a_dt"

    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id"), primary_key=True)
    acad_year = Column(INTEGER(), primary_key=True)
    dt = Column(DATETIME(), primary_key=True)
    description = Column(VARCHAR(50))
    dt_cat_id = Column(CHAR(4), ForeignKey("a_dt_cat.dt_cat_id"))


class f_set_costing(Base):
    """
    Defines how loss-making areas are costed. 

    Referenced by views to provide a manual override for 
    default costings. Each set which makes a loss can appear in
    this table to specify to which other cost centre that loss 
    should be attributed. See the relevant view for more detail 
    on the mechanics.  

    Attributes
    ----------
    set_id : int
        ID of the set being costed. 
    costc : str
        Cost centre be costed to. 
    base_proportion : float
        Proportion to cost to the given costc. Needn't sum to 100%. 
    """
    __tablename__ = "f_set_costing"

    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"),
                    primary_key=True)
    costc = Column(CHAR(6), ForeignKey("fs_cost_centre.costc"),
                   primary_key=True)
    base_proportion = Column(DECIMAL(10, 5), nullable=False)


# Map taking string names to table objects
table_map = {}
for model in Base._decl_class_registry.values():
    if hasattr(model, '__tablename__'):
        table_map[model.__tablename__] = model
        # Add the table name to the docstring
        additional_str = f"Actual table name: ``{model.__tablename__}``\r \r"
        model.__doc__ = additional_str + model.__doc__
        # Mark Primary key columns in the docstring
        for col in model.__table__.columns:
            if col.primary_key:
                attributepos = model.__doc__.find(
                    col.key, model.__doc__.find("Attribute"))
                splitpoint = model.__doc__.find(
                    '\n', attributepos)
                pre, post = model.__doc__[:splitpoint], \
                    model.__doc__[splitpoint:]
                model.__doc__ = pre + ' [**PK**]' + post
