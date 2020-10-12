"""
Classes for specifying tables.

If altering a table, use `alembic` to migrate to DB.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, CHAR, VARCHAR, BINARY, DECIMAL, DATE, INTEGER, create_engine, ForeignKey

# Standard financial decimal
FDec = DECIMAL(precision=18, scale=2)

# Define the database base class, to hold the database info
Base = declarative_base()

# Dummy in memory database for testing
engine = create_engine("sqlite:///:memory:", echo=True)
session = sessionmaker(bind=engine)


class directorate(Base):
    __tablename__ = "directorate"

    directorate_id = Column(CHAR(1), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    director = Column(VARCHAR(50))

    cost_centres = relationship("Cost_Centre", back_populates="directorate")


class cost_centre(Base):
    __tablename__ = "cost_centre"

    costc = Column(CHAR(6), primary_key=True)
    description = Column(VARCHAR(50), nullable=False)
    directorate_id = Column(CHAR(1), ForeignKey(
        "directorate.directorate_id", ondelete="CASCADE"), nullable=False)
    owner = Column(VARCHAR(50), nullable=False)
    supercede_by = Column(CHAR(6), nullable=True)
    password = Column(VARCHAR(50), nullable=True)

    directorate = relationship("Directorate", back_populates="cost_centres")


class set_cat(Base):
    __tablename__ = "set_cat"

    set_cat_id = Column(CHAR(3), primary_key=True)
    description = Column(VARCHAR(50))


class f_set(Base):
    __tablename__ = "f_set"

    set_id = Column(Integer, primary_key=True)
    acad_year = Column(Integer, nullable=False)
    costc = Column(String(4), ForeignKey(
        "cost_centre.costc", ondelete="CASCADE"), nullable=False)
    set_cat_id = Column(String(3), ForeignKey(
        "set_cat.set_cat_id", ondelete="CASCADE"), nullable=False)


class input_inc_courses(Base):
    __tablename__ = 'input_inc_courses'
    courses_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                        nullable=False, mssql_identity_start=1000, mssql_identity_increment=1)
    course_name = Column(VARCHAR(length=50, collation='Latin1_General_CI_AS')
                         autoincrement=False, nullable=True)
    students = Column(INTEGER(), autoincrement=False, nullable=True)
    fee = Column(DECIMAL(precision=10, scale=5)
                 autoincrement=False, nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id") autoincrement=False, nullable=False)


class input_inc_courses_p(Base):
    __tablename__ = "input_inc_courses_p"
    courses_id = Column(INTEGER(), ForeignKey(
        "Input_inc_courses.courses_id"), primary_key=True, nullable=False)
    period = Column(INTEGER(), primary_key=True, nullable=False)
    amount = Column(FDec, nullable=True)


class input_inc_other(Base):
    __tablename__ = 'input_inc_other'
    inc_id = Column(INTEGER(), primary_key=True, autoincrement=True,
                    nullable=False, mssql_identity_start=1000, mssql_identity_increment=1)
    account = Column(CHAR(4), nullable=True)
    description = Column(VARCHAR(250), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id") autoincrement=False, nullable=False)


class input_inc_other_p(Base):
    __tablename__ = "input_inc_courses_p"
    inc_id = Column(INTEGER(), ForeignKey(
        "Input_inc_courses.courses_id"), primary_key=True, nullable=False)
    period = Column(INTEGER(), primary_key=True)
    amount = Column(FDec, nullable=True)


class input_pay_staff(Base):
    __tablename__ = "input_pay_staff"
    post_status_id = Column(CHAR(4), nullable=True)
    post_type_id = Column(CHAR(5), nullable=True)
    title = Column(VARCHAR(50), nullable=True),
    name = Column(VARCHAR(50), nullable=True),
    staff_id = Column(VARCHAR(8), nullable=True)
    post_id = Column(VARCHAR(50), nullable=True)
    start_date = Column(DATE(), nullable=True)
    end_date = Column(DATE(), nullable=True)
    grade = Column(INTEGER(), nullable=True)
    current_spine = Column(INTEGER(), nullable=True)
    indicative_fte = Column(DECIMAL(precision=10, scale=5), nullable=True)
    allowances = Column(FDec,  nullable=True)
    con_type_id = Column(INTEGER(), nullable=True)
    pension_id = Column(VARCHAR(3), nullable=True)
    travel_scheme = Column(FDec, nullable=True)
    teaching_hours = Column(DECIMAL(precision=10, scale=5), nullable=True)
    set_id = Column(INTEGER(), ForeignKey("f_set.set_id") autoincrement=False, nullable=False)


class input_inc_bursary(Base):
    __tablename__ = 'input_inc_bursary'

    set_id = Column(INTEGER(), ForeignKey("f_set.set_id") autoincrement=False, nullable=False)
    description = Column(VARCHAR(250), nullable=True)
    amount = Column(FDec, nullable=True)
    number = Column(INTEGER(), nullable=True)
    status = Column(CHAR(1), nullable=True)


class input_pay_fracclaim(Base):
    __tablename__ = 'input_pay_fracclaim',
    period = Column(INTEGER(), nullable=True)
    hours = Column(DECIMAL(precision=18, scale=5), nullable=True)

    Column('period', INTEGER(), autoincrement=False, nullable=True),
    Column('hours', DECIMAL(precision=18, scale=0),
           autoincrement=False, nullable=True),
    Column('set_id', INTEGER(), autoincrement=False, nullable=True),
    ForeignKeyConstraint(['set_id'], ['f_set.set_id'],
                         name='FK_input_pay_fracclaim_set')
    )
        op.create_index('IX_fin_pay_fracclaim', 'input_pay_fracclaim', [
            'period', 'set_id'], unique = False)
        op.create_table('staff_post_type',
    Column('post_type_id', CHAR(length=5, collation='Latin1_General_CI_AS'),
           autoincrement=False, nullable=False),
    Column('description', VARCHAR(length=50, collation='Latin1_General_CI_AS'),
           autoincrement=False, nullable=False)
    )
        op.create_table('set_cat',
    Column('set_cat_id', CHAR(length=3, collation='Latin1_General_CI_AS'),
           autoincrement=False, nullable=False),
    Column('description', VARCHAR(length=50, collation='Latin1_General_CI_AS'),
           autoincrement=False, nullable=False),
    PrimaryKeyConstraint('set_cat_id', name='PK_set_code')
    )
        op.create_table('input_inc_other',
    Column('account', CHAR(length=4, collation='Latin1_General_CI_AS'),
           autoincrement=False, nullable=False),
    Column('description', VARCHAR(length=100, collation='Latin1_General_CI_AS'),
           autoincrement=False, nullable=True),
    Column('inc_id', INTEGER(), autoincrement=True, nullable=False,
           mssql_identity_start=1, mssql_identity_increment=1),
    Column('set_id', INTEGER(), autoincrement=False, nullable=True),
    ForeignKeyConstraint(['set_id'], ['f_set.set_id'],
                         name='FK_input_inc_other_set'),
    PrimaryKeyConstraint('inc_id', name='PK_fin_inc_other')
    )
        op.create_table('input_inc_feeloss',
    Column('set_id', INTEGER(), autoincrement=False, nullable=False),
    Column('status', CHAR(length=1, collation='Latin1_General_CI_AS'),
           autoincrement=False, nullable=False),
    Column('rate', DECIMAL(precision=10, scale=5),
           autoincrement=False, nullable=False),
    ForeignKeyConstraint(['set_id'], ['f_set.set_id'],
                         name='FK_input_inc_feeloss_set')


Base.metadata.create_all(engine)
