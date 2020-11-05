import click

from .oncost import oncost
from .preview import preview
from .newset import newset
from .rollforward import rollforward
from .syncviews import syncviews


@click.group()
@click.pass_obj
def database(config):
    """
    Edit data in the main database. 
    """
    pass


commands = [oncost, preview, newset, syncviews, rollforward]
for command in commands:
    database.add_command(command)
