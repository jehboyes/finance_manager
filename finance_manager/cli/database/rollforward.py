# pylint: disable=no-member
import click
from sqlalchemy import and_
from sqlalchemy.orm import aliased
from finance_manager.database import DB
from finance_manager.database.spec import Base, f_set


@click.command()
@click.argument("tosetcat")
@click.argument("toacadyear", type=int)
@click.argument("fromsetcat")
@click.argument("fromacadyear", type=int)
@click.option("--omit", "-o", multiple=True, help="A table to omit (can be used multiple times).")
@click.pass_obj
def rollforward(config, tosetcat, toacadyear, fromsetcat, fromacadyear, omit):
    """
    Copy forward input table contents to those with TOSETCAT in TOACADYEAR from FROMSETCAT FROMACADYEAR.

    \b
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
    tables = []
    # Define list of tables to be copied forward
    for model in Base._decl_class_registry.values():
        if hasattr(model, '__tablename__'):
            # Automatically add any tables that begin with 'input' as per naming convention
            if model.__tablename__[:5] == 'input' \
                    and model.__tablename__[-4:] != 'type' \
                    and not (model.__tablename__ in omit):
                tables.append(model)

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
        with click.progressbar(tables, label="Iterating through tables...") as bar:
            for table in bar:
                try:
                    records = []
                    table_query = s.query(table).join(f_set).filter(and_(f_set.acad_year == fromacadyear,
                                                                         f_set.set_cat_id == fromsetcat))
                    if len(table_query.all()) > 0:  # if anything to rollforward
                        # Get primary keys, as these will need to be removed
                        pk = []
                        for col in table.__table__.columns:
                            if col.primary_key and col.key != 'set_id' and col.key != 'period':
                                pk.append(col.key)
                        # For each row old id, change id and add to bulk insert
                        for row in table_query.all():
                            record = row.__dict__
                            for col in pk:
                                record.pop(col)
                            record["set_id"] = set_map[row.set_id]
                            records.append(record)
                        s.bulk_insert_mappings(table, records)
                except:
                    raise RuntimeError(f"Failed on {table.__tablename__}")
        if click.confirm("Confirm rollforward?"):
            s.commit()
            click.echo("Complete!")
