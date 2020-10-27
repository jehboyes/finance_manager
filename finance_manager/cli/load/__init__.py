import click
from .payclaim import payclaim
from .curriculum import curriculum
from .csv import csv


@click.group()
@click.pass_obj
def load(config):
    """
    Import data from other systems and sources
    """
    pass


commands = [payclaim, curriculum, csv]
for command in commands:
    load.add_command(command)
