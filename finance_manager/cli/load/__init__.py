import click
from .payclaim import payclaim
from .curriculum import curriculum
from .csv import csv
from .actuals import actuals


@click.group()
@click.pass_obj
def load(config):
    """
    **Group** of commands for importing data from other sources. 
    """
    pass


commands = [payclaim, curriculum, actuals, csv]
for command in commands:
    load.add_command(command)
