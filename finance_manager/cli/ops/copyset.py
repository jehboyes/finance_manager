# pylint: disable=no-member
import click
from sqlalchemy import and_
from sqlalchemy.orm import aliased
from finance_manager.database import DB
from finance_manager.database.spec import Base, f_set
from finance_manager.cli.ops.newset import newset


@click.command()
@click.argument("tosetcat")
@click.argument("toacadyear", type=int)
@click.argument("fromsetcat")
@click.argument("fromacadyear", type=int)
@click.option("--create", type=int, help="Create the sets as well, with given curriculum ID. Shortcut for simple use of ``newset`` command.")
@click.option("--omit", "-o", multiple=True, help="A table to omit (can be used multiple times).")
@click.option("--close", "-c", is_flag=True, help="Close the sets being copied from.")
@click.option("--gen", is_flag=True, help="Copy forward the generic tables only (the ones that are shared by all sets).")
@click.pass_obj
def copyset(config, tosetcat, toacadyear, fromsetcat, fromacadyear, omit, close, gen, create):
    """
    Copy forward input table contents. Moves from ``FROMSETCAT`` in ``FROMACADYEAR`` to ``TOSETCAT`` in ``TOACADYEAR``.

    \f
    Parameters
    ----------
    config : Config
        Custom config object.
    tosetcat : str
        Target's 3 character set category code.
    toacadyear : int
        Academic year of target.
    fromsetcat : str
        Source's 3 character set category code.
    fromacadyear : int
        Source's academic year.

    """
    # if, create option specified, create new sets
    if create is not None:
        newset(config, toacadyear, tosetcat, create, create, 1)
    tables = []  # Tables to be rolled forward for each set
    set_tables = []  # Tables to be rolled forward for the entire category
    year_tables = []  # Tables to be rolled forward for the entire year
    # Define list of tables to be copied forward
    for model in Base._decl_class_registry.values():
        if hasattr(model, '__tablename__'):
            # Automatically add any tables that begin with 'input' or 'staff' as per naming convention
            if model.__tablename__[:5] in ['input', 'staff', 'conf_'] \
                    and not (model.__tablename__ in omit):
                # determine which ones have a set_id or set_cat_id or acad year(some don't)
                set_id_col = sum(
                    [1 for col in model.__table__.columns if col.key == 'set_id'])
                set_cat_id_col = sum(
                    [1 for col in model.__table__.columns if col.key == 'set_cat_id'])
                acad_year_col = sum(
                    [1 for col in model.__table__.columns if col.key == 'acad_year'])
                # using set, set cat, year hierarchy, add to copy forward lit
                if set_id_col == 1:
                    tables.append(model)
                elif set_cat_id_col == 1:
                    set_tables.append(model)
                elif acad_year_col == 1:
                    year_tables.append(model)
    with DB(config=config) as db:
        s = db.session()
        # Get set_id mapping, define a version of f_set as alias to enable self join
        new_set = aliased(f_set)
        set_map_query = s.query(f_set.set_id, new_set.set_id).join(new_set, new_set.costc == f_set.costc). \
            filter(and_(new_set.acad_year == toacadyear,
                        new_set.set_cat_id == tosetcat,
                        f_set.set_cat_id == fromsetcat,
                        f_set.acad_year == fromacadyear))
        set_map = {}
        for old, new in set_map_query.all():
            set_map[old] = new
        # For each input table, reinsert from old_id with new set_id
        if not gen:
            with click.progressbar(tables, label="Iterating through input tables...") as bar:
                for table in bar:
                    try:
                        records = []
                        table_query = s.query(table).join(f_set).filter(and_(f_set.acad_year == fromacadyear,
                                                                             f_set.set_cat_id == fromsetcat))
                        destination_query = s.query(table).join(f_set).filter(and_(f_set.acad_year == toacadyear,
                                                                                   f_set.set_cat_id == tosetcat))
                        # if anything to rollforward and destination empty
                        if len(table_query.all()) > 0 and len(destination_query.all()) == 0:
                            # Get primary keys, as these will need to be removed
                            pk = []
                            for col in table.__table__.columns:
                                if col.primary_key and col.key != 'set_id' and col.key != 'period':
                                    pk.append(col.key)
                            # For each row old id, change set id and add to bulk insert
                            for row in table_query.all():
                                record = row.__dict__
                                for col in pk:
                                    record.pop(col)
                                record["set_id"] = set_map[row.set_id]
                                records.append(record)
                            s.bulk_insert_mappings(table, records)
                    except:
                        raise RuntimeError(f"Failed on {table.__tablename__}")
        with click.progressbar(set_tables, label="Iterating through category tables...") as bar:
            for table in bar:
                records = []
                table_query = s.query(table).filter(and_(table.acad_year == fromacadyear,
                                                         table.set_cat_id == fromsetcat))
                destination_query = s.query(table).filter(and_(table.acad_year == toacadyear,
                                                               table.set_cat_id == tosetcat))
                if len(table_query.all()) > 0 and len(destination_query.all()) == 0:
                    for row in table_query.all():
                        record = row.__dict__
                        record['set_cat_id'] = tosetcat
                        record['acad_year'] = toacadyear
                        records.append(record)
                    s.bulk_insert_mappings(table, records)
        with click.progressbar(year_tables, label="Iterating through annual tables...") as bar:
            for table in bar:
                records = []
                table_query = s.query(table).filter(
                    table.acad_year == fromacadyear)
                destination_query = s.query(table).filter(
                    table.acad_year == toacadyear)
                if len(table_query.all()) > 0 and len(destination_query.all()) == 0:
                    for row in table_query.all():
                        record = row.__dict__
                        record['acad_year'] = toacadyear
                        records.append(record)
                    s.bulk_insert_mappings(table, records)
        if close:
            old_sets = s.query(f_set).filter(and_(f_set.acad_year == fromacadyear,
                                                  f_set.set_cat_id == fromsetcat)).all()
            for _set in old_sets:
                _set.closed = 1
        if click.confirm("Confirm rollforward?"):
            s.commit()
            click.echo("Complete!")