import click

from .oncost import oncost


@click.group()
@click.pass_obj
def edit(config):
    """
    Edit data in the main database. 
    """
    pass


edit.add_command(oncost)


# commands = [payclaim, curriculum, csv]
# for command in commands:
#     load.add_command(command)
