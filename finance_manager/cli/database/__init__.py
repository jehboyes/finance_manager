import click

from .oncost import oncost


@click.group()
@click.pass_obj
def database(config):
    """
    Edit data in the main database. 
    """
    pass


database.add_command(oncost)


# commands = [payclaim, curriculum, csv]
# for command in commands:
#     load.add_command(command)
