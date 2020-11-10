import click
from .save import save


@click.group()
@click.pass_obj
def finance(config):
    """
    **Group** of finance-related commands.
    """
    pass


commands = [save]
for command in commands:
    finance.add_command(command)
