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
from sqlalchemy import Column, CHAR, VARCHAR, BOOLEAN, DECIMAL, DATE, INTEGER, create_engine, ForeignKey
from finance_manager.functions import periods

# Standard financial decimal
FDec = DECIMAL(precision=18, scale=2)

# Define the database base class, to hold the database info
Base = declarative_base()

# Dummy in memory database for testing
if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()


class directorate(Base):
    __tablename__ = "fs_directorate"

    directorate_id = Column(CHAR(1), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    director = Column(VARCHAR(50))

    cost_centres = relationship("fs_cost_centre", back_populates="directorate")


class cost_centre(Base):
    __tablename__ = "fs_cost_centre"

    costc = Column(CHAR(6), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    directorate_id = Column(CHAR(1), ForeignKey(
        "fs_directorate.directorate_id", ondelete="CASCADE"), nullable=False)
    owner = Column(VARCHAR(50), nullable=False)
    supercede_by = Column(CHAR(6), nullable=True)
    password = Column(VARCHAR(50), nullable=True)

    directorate = relationship("fs_directorate", back_populates="cost_centres")


class f_set_cat(Base):
    __tablename__ = "f_set_cat"
    set_cat_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))

    f_sets = relationship("f_set", back_populates="category")


class f_set(Base):
    __tablename__ = "f_set"

    set_id = Column(INTEGER(), primary_key=True)
    acad_year = Column(INTEGER(), nullable=False)
    costc = Column(CHAR(4), ForeignKey(
        "fs_cost_centre.costc", ondelete="CASCADE"), nullable=False)
    set_cat_id = Column(CHAR(3), ForeignKey(
        "f_set_cat.set_cat_id", ondelete="CASCADE"), nullable=False)

    category = relationship("f_set_cat", back_populates="f_sets")
    finances = relationship("f_finance", back_populates="f_set")


class account(Base):
    __tablename__ = "fs_account"

    account = Column(CHAR(4), primary_key=True)
    description = Column(VARCHAR(50))
    summary_code = Column(CHAR(3), ForeignKey(
        "fs_summary_code.summary_code"), nullable=False)
    hide_from_users = Column(BOOLEAN(), server_default='0')

    summary_code = relationship("fs_summary_code", back_populates="accounts")


class summary_code(Base):
    __tablename__ = "fs_summary_code"

    summary_code = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)

    accounts = relationship("fs_account", back_populates="summary_code")


class finance(Base):
    __tablename__ = "f_finance"

    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"),
                    primary_key=True, nullable=False)
    account = Column(CHAR(4), ForeignKey(
        "fs_account.account"), primary_key=True)
    costc = Column(CHAR(6), ForeignKey(
        "fs_cost_centre.costc"), primary_key=True)
    period = Column(INTEGER(), primary_key=True)
    amount = Column(FDec)

    f_set = relationship("f_set", back_populates="finances")


class inc_courses(Base):
    __tablename__ = 'input_inc_courses'
    courses_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                        mssql_identity_start=1000, mssql_identity_increment=1)
    course_name = Column(VARCHAR(50), nullable=True)
    students = Column(INTEGER(), autoincrement=False, nullable=True)
    fee = Column(DECIMAL(precision=10, scale=5), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    # Bad practice to use exec, but assigning to a dict wouldn't work
    for n in periods():
        exec(f"p{n} = Column(FDec)")


class inc_other(Base):
    __tablename__ = 'input_inc_other'
    inc_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                    mssql_identity_start=1000, mssql_identity_increment=1)
    account = Column(CHAR(4), nullable=True)
    description = Column(VARCHAR(250), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)


class inc_other_p(Base):
    __tablename__ = "input_inc_other_p"
    inc_id = Column(INTEGER(), ForeignKey(
        "input_inc_other.inc_id"), primary_key=True, nullable=False)
    period = Column(INTEGER(), primary_key=True)
    amount = Column(FDec, nullable=True)


class inc_bursary(Base):
    __tablename__ = 'input_inc_bursary'

    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"),
                    primary_key=True, autoincrement=False, nullable=False)
    description = Column(VARCHAR(250), primary_key=True, nullable=True)
    amount = Column(FDec, nullable=True)
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
    __tablename__ = "input_pay_claim_type"

    claim_type_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))


class pay_claim(Base):
    __tablename__ = "input_pay_claim"

    claim_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                      mssql_identity_start=1000, mssql_identity_increment=1)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"))
    account = Column(CHAR(4), ForeignKey("fs_account.account"))
    description = Column(VARCHAR(50))
    rate = Column(FDec)
    claim_type_id = Column(CHAR(3), ForeignKey(
        "input_pay_claim_type.claim_type_id"))

    hours = relationship("input_pay_claim_p", back_populates="claim")


class pay_claim_p(Base):
    __tablename__ = "input_pay_claim_p"

    claim_id = Column(INTEGER(), ForeignKey(
        "input_pay_claim.claim_id"), primary_key=True)
    period = Column(INTEGER(), primary_key=True)
    hours = Column(DECIMAL(10, 5))

    claim = relationship("input_pay_claim", back_populates="hours")


class pay_staff(Base):
    __tablename__ = "input_pay_staff"

    post_status_id = Column(CHAR(4), ForeignKey(
        "staff_post_status.post_status_id"), nullable=True)
    post_type_id = Column(CHAR(5), ForeignKey(
        "staff_post_type.post_type_id"), nullable=True)
    title = Column(VARCHAR(50), nullable=True),
    name = Column(VARCHAR(50), nullable=True),
    staff_id = Column(VARCHAR(8), nullable=True)
    post_id = Column(VARCHAR(50), nullable=True)
    start_date = Column(DATE(), nullable=True)
    end_date = Column(DATE(), nullable=True)
    grade = Column(INTEGER(), nullable=True)
    current_spine = Column(INTEGER(), ForeignKey(
        "staff_spine.spine"), nullable=True)
    indicative_fte = Column(DECIMAL(precision=10, scale=5), nullable=True)
    allowances = Column(FDec,  nullable=True)
    con_type_id = Column(INTEGER(), ForeignKey(
        "staff_con_type.con_type_id"), nullable=True)
    pension_id = Column(VARCHAR(3), ForeignKey(
        "staff_pension.pension_id"), nullable=True)
    travel_scheme = Column(FDec, nullable=True)
    teaching_hours = Column(DECIMAL(precision=10, scale=5), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)
    staff_line_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                           mssql_identity_start=1000, mssql_identity_increment=1)


class post_type(Base):
    __tablename__ = 'staff_post_type'

    post_type_id = Column(CHAR(5), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)


class post_status(Base):
    __tablename__ = 'staff_post_status'

    post_status_id = Column(CHAR(4), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    exclude_from_finance = Column(BOOLEAN(), server_default='0')


class spine(Base):
    __tablename__ = "staff_spine"

    spine = Column(INTEGER(), primary_key=True)
    value = Column(FDec)


class on_type(Base):
    __tablename__ = "staff_con_type"

    con_type_id = Column(INTEGER(), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    work_hours = Column(DECIMAL(10, 5), nullable=False)
    hol_hours = Column(DECIMAL(10, 5), nullable=False)


class pension(Base):
    __tablename__ = "staff_pension"

    pension_id = Column(VARCHAR(3), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    emp_cont_rate = Column(DECIMAL(10, 8), nullable=False)


class nonp_other(Base):
    __tablename__ = 'input_nonp_other'
    nonp_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                     mssql_identity_start=1000, mssql_identity_increment=1)
    account = Column(CHAR(4), ForeignKey("fs_account.account"), nullable=True)
    description = Column(VARCHAR(250), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id"), nullable=False)


class nonp_other_p(Base):
    __tablename__ = "input_nonp_other_p"
    nonp_id = Column(INTEGER(), ForeignKey(
        "input_nonp_other.nonp_id"), primary_key=True, nullable=False)
    period = Column(INTEGER(), primary_key=True)
    amount = Column(FDec, nullable=True)


class nonp_internal(Base):
    __tablename__ = "input_nonp_internal"

    internal_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                         mssql_identity_start=1000, mssql_identity_increment=1)
    description = Column(VARCHAR(50), nullable=True)
    costc = Column(CHAR(6), ForeignKey("fs_cost_centre.costc"), nullable=True)
    amount = Column(FDec, nullable=True)


Base.metadata.create_all(engine)
