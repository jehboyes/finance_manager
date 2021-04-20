# pylint: disable=no-member
from finance_manager.database.spec import table_map
import click


@click.command()
@click.pass_obj
@click.option("--filter", "-f", type=str, help="Must contain given characters (can be used multiple times).", multiple=True)
def schema(config, filter):
    """
    List the schema objects. 

    Use the ``crud`` command to interact with individual objects.

    TODO Include object types other than tables. 
    """
    names = [k for k in table_map.keys()]
    for f in filter:
        names = [n for n in names if f in n]
    names.sort()
    print("\n".join(names))
