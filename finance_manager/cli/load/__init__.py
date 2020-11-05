import click
from .payclaim import payclaim
from .curriculum import curriculum
from .csv import csv
from .actuals import actuals


@click.group()
@click.pass_obj
def load(config):
    """
    Import data from other systems and sources
    """
    pass


commands = [payclaim, curriculum, actuals, csv]
for command in commands:
    load.add_command(command)
