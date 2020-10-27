"""
Classes for specifying tables.

If altering a table, use `alembic` to migrate to DB.

Standard table prefixes are used on the database tables for easier navigation/organisation.
Note however that these are **not** used in the class names, for brevity. They are:
-  **fs_** for tables that are part of the financial structure
-  **f_** for tables that hold and structure actual finance data
-  **input_** for tables that are used directly by the interface
-  **staff_** for the various lookups used exclusively by the pay_staff table

"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, CHAR, VARCHAR, DECIMAL, DATE, INTEGER, create_engine, ForeignKey
from sqlalchemy.dialects.mssql import BIT, DATETIME
from finance_manager.functions import periods

# Standard financial decimal
_FDec = DECIMAL(precision=18, scale=2)

# Define the database base class, to hold the database info
Base = declarative_base()

# Dummy in memory database for testing
engine = create_engine("sqlite:///:memory:", echo=False)
Session = sessionmaker(bind=engine)
session = Session()


def generate_period_cols(type_string="_FDec"):
    """
    Generate columns for all twelve periods

    Bad practice to use exec to achieve this; will try and find a better way 
    of achieving the same result when possible.
    """
    for n in periods():
        exec(f"p{n} = Column(type_string, server_default='0')")


class directorate(Base):
    """
    A one to one mapping with SLT

    ...
    """
    __tablename__ = "fs_directorate"

    directorate_id = Column(CHAR(1), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    director = Column(VARCHAR(50))

    cost_centres = relationship("cost_centre", back_populates="directorate")


class cost_centre(Base):
    """
    Standard 6-character cost centres

    ...
    """
    __tablename__ = "fs_cost_centre"

    costc = Column(CHAR(6), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    directorate_id = Column(CHAR(1), ForeignKey(
        "fs_directorate.directorate_id", ondelete="CASCADE"), nullable=False)
    owner = Column(VARCHAR(50), nullable=False)
    supercede_by = Column(CHAR(6), nullable=True, comment="Use to indicate where a cost centre subsumes this one going forward")
    password = Column(VARCHAR(50), nullable=True, comment="Legacy vegan password from excel era")

    directorate = relationship("directorate", back_populates="cost_centres")


class f_set_cat(Base):
    """
    Set categories

    BP1, forecast P3 etc
    """
    __tablename__ = "f_set_cat"
    set_cat_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))

    f_sets = relationship("f_set", back_populates="category")


class f_set(Base):
    """
    Finance sets

    Integral part of data structure. Unique by acad_year, costc, category. For example,
    there can only be 1 2020 BP3 MA1600. 
    """
    __tablename__ = "f_set"
    set_id = Column(INTEGER(), primary_key=True)
    acad_year = Column(INTEGER(), nullable=False)
    costc = Column(CHAR(6), ForeignKey(
        "fs_cost_centre.costc", ondelete="CASCADE"), nullable=False)
    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id", ondelete="CASCADE"), nullable=False)
    curriculum_id = Column(INTEGER(), comment = "Foreign key to CM Database")
    curriculum_hours = Column(DECIMAL(20, 5), comment="From CM; updated manually to reflect Luminate ownership philosophy.")
    student_number_usage_id = Column(VARCHAR(100), comment="Foreign key for CM Database") 
    allow_student_number_change = Column(BIT(), server_default="0", comment="Allow users to input different student numbers") 

    category = relationship("f_set_cat", back_populates="f_sets") 

class finance_instance(Base):
    """
    An instance of finance records for a set

    Allows for viewing the finace history of a set. 
    """

    __tablename__ = "f_finance_instance"

    instance_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                         mssql_identity_start=1000, mssql_identity_increment=1)
    created_by = Column(VARCHAR(50), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    datestamp = Column(DATETIME())
    notes = Column(VARCHAR(500), nullable=True)


class account(Base):
    __tablename__ = "fs_account"

    account = Column(CHAR(4), primary_key=True)
    description = Column(VARCHAR(50))
    summary_code = Column(CHAR(3), ForeignKey(
        "fs_summary_code.summary_code"), nullable=False)
    hide_from_users = Column(BIT(), server_default='0', comment="Control ability to use in the app's 'Other' screens")
    default_balance = Column(CHAR(2), ForeignKey(
        "fs_entry_type.balance_type"), nullable=False)


class entry_type(Base):
    __tablename__ = "fs_entry_type"
    balance_type = Column(CHAR(2), primary_key=True)
    coefficient = Column(INTEGER(), nullable=False)
    description = Column(VARCHAR(6))


class summary_code(Base):
    __tablename__ = "fs_summary_code"

    summary_code = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    section_id = Column(CHAR(3), ForeignKey("fs_section.section_id"))
    position = Column(INTEGER())


class finance_section(Base):
    __tablename__ = "fs_section"

    section_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))
    show_in_ui = Column(BIT())
    position = Column(INTEGER())


class finance(Base):
    __tablename__ = "f_finance"

    instance_id = Column(INTEGER(), ForeignKey(
        "f_finance_instance.instance_id"), primary_key=True)
    account = Column(CHAR(4), ForeignKey(
        "fs_account.account"), primary_key=True)
    period = Column(INTEGER(), primary_key=True)
    amount = Column(_FDec)


class inc_courses(Base):
    __tablename__ = 'input_inc_courses'
    courses_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                        mssql_identity_start=1000, mssql_identity_increment=1)
    course_name = Column(VARCHAR(50), nullable=True)
    students = Column(INTEGER(), autoincrement=False, nullable=True)
    fee = Column(_FDec, nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    for n in periods():
        exec(f"p{n} = Column(_FDec, server_default='0')")


class inc_other(Base):
    __tablename__ = 'input_inc_other'
    inc_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                    mssql_identity_start=1000, mssql_identity_increment=1)
    account = Column(CHAR(4), nullable=True)
    description = Column(VARCHAR(1000), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    for n in periods():
        exec(f"p{n} = Column(_FDec, server_default='0')")


class inc_bursary(Base):
    __tablename__ = 'input_inc_bursary'

    bursary_id = Column(INTEGER(),autoincrement=True,
                    mssql_identity_start=1000, mssql_identity_increment=1)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"))
    description = Column(VARCHAR(250), primary_key=True, nullable=True)
    amount = Column(_FDec, nullable=True)
    number = Column(INTEGER(), nullable=True)
    status = Column(CHAR(1), nullable=True)


class inc_feeloss(Base):
    __tablename__ = 'input_inc_feeloss'

    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), primary_key=True)
    status = Column(CHAR(1), primary_key=True)
    rate = Column(DECIMAL(precision=10, scale=5), nullable=True)


class pay_fracclaim(Base):
    __tablename__ = 'input_pay_fracclaim'

    period = Column(INTEGER(), nullable=True, primary_key=True)
    hours = Column(DECIMAL(precision=18, scale=5), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"),
                    primary_key=True,  nullable=False)


class claim_type(Base):
    """
    Table for claim types
    """
    __tablename__ = "input_pay_claim_type"

    claim_type_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))
    variable_rate = Column(BIT())
    base_multiplier = Column(DECIMAL(10, 5))
    holiday_multiplier = Column(DECIMAL(10, 5))
    rate_uplift = Column(_FDec)


class pay_claim(Base):
    """
    Claim lines
    """
    __tablename__ = "input_pay_claim"

    claim_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                      mssql_identity_start=1000, mssql_identity_increment=1)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"))
    account = Column(CHAR(4), ForeignKey("fs_account.account"))
    description = Column(VARCHAR(1000))
    rate = Column(_FDec)
    claim_type_id = Column(CHAR(3), ForeignKey(
        "input_pay_claim_type.claim_type_id"))
    # Bad practice to use exec, but assigning to a dict wouldn't work
    for n in periods():
        exec(f"p{n} = Column(DECIMAL(10,5), server_default='0')")


class pay_staff(Base):
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
        "staff_con_type.con_type_id"), nullable=True)
    pension_id = Column(VARCHAR(3), ForeignKey(
        "staff_pension.pension_id"), nullable=True)
    travel_scheme = Column(_FDec, nullable=True)
    teaching_hours = Column(DECIMAL(precision=10, scale=5),
                            nullable=True, server_default='0')
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    staff_line_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                           mssql_identity_start=1000, mssql_identity_increment=1)


class post_type(Base):
    __tablename__ = 'staff_post_type'

    post_type_id = Column(CHAR(5), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    lcc_description = Column(VARCHAR(50), nullable=False)


class post_status(Base):
    __tablename__ = 'staff_post_status'

    post_status_id = Column(CHAR(4), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    exclude_from_finance = Column(BIT(), server_default='0')


class spine(Base):
    __tablename__ = "staff_spine"

    spine = Column(INTEGER(), primary_key=True)
    value = Column(_FDec)


class con_type(Base):
    __tablename__ = "staff_con_type"

    con_type_id = Column(INTEGER(), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    work_hours = Column(DECIMAL(10, 5), nullable=False)
    hol_hours = Column(DECIMAL(10, 5), nullable=False)


class pension(Base):
    __tablename__ = "staff_pension"

    pension_id = Column(VARCHAR(3), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)


class pension_emp_cont(Base):
    """
    Employers pension contributions for each month, by year
    """
    __tablename__ = "staff_pension_contrib"

    pension_id = Column(VARCHAR(3), ForeignKey(
        "staff_pension.pension_id"), primary_key=True)
    acad_year = Column(INTEGER(), primary_key=True)
    for n in periods():
        exec(f"p{n} = Column(DECIMAL(6,5), server_default='0')")


class ni(Base):
    """
    National insurance secondary threshold 

    Has one rate for year, and threshold by month
    """
    __tablename__ = 'staff_ni'

    acad_year = Column(INTEGER(), primary_key=True)
    rate = Column(DECIMAL(9, 8))
    for n in periods():
        exec(f"p{n} = Column(_FDec, server_default='0')")


class nonp_other(Base):
    __tablename__ = 'input_nonp_other'
    nonp_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                     mssql_identity_start=1000, mssql_identity_increment=1)
    account = Column(CHAR(4), ForeignKey("fs_account.account"), nullable=True)
    description = Column(VARCHAR(1000), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    for n in periods():
        exec(f"p{n} = Column(_FDec, server_default='0')")


class nonp_internal(Base):
    __tablename__ = "input_nonp_internal"

    internal_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                         mssql_identity_start=1000, mssql_identity_increment=1)
    description = Column(VARCHAR(50), nullable=True)
    costc = Column(CHAR(6), ForeignKey("fs_cost_centre.costc"), nullable=True)
    amount = Column(_FDec, nullable=True)


class permission(Base):
    """
    Permissions for access to cost centres via the UI
    """
    __tablename__ = "a_permission"

    costc = Column(CHAR(6), ForeignKey(
        "fs_cost_centre.costc"), primary_key=True)
    login_365 = Column(VARCHAR(50), primary_key=True)


# Map taking string names to table objects
table_map = {}
for model in Base._decl_class_registry.values():
    if hasattr(model, '__tablename__'):
        table_map[model.__tablename__] = model
