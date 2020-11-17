import click
from .save import save
from .export import export

@click.group()
@click.pass_obj
def finance(config):
    """
    **Group** of finance-related commands.
    """
    pass


commands = [save, export]
for command in commands:
    finance.add_command(command)
