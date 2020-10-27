import click


@click.group()
@click.pass_obj
def permissions():
    """
    Manage access to cost centres in the UI.
    """
    pass
