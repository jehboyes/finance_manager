import click

from .oncost import oncost
from .preview import preview


@click.group()
@click.pass_obj
def database(config):
    """
    Edit data in the main database. 
    """
    pass


database.add_command(oncost)
database.add_command(preview)

# commands = [payclaim, curriculum, csv]
# for command in commands:
#     load.add_command(command)
