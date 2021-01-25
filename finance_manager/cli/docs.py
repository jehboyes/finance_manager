# pylint: disable=no-member
import click
import win32com.client
from finance_manager.database.spec import directorate
from finance_manager.database import DB


@click.command()
@click.argument("template", type=click.Path(exists=True))
@click.argument("folder", type=click.Path(exists=True))
@click.pass_obj
def docs(config, template, folder):
    """
    Generate documentation for each directorate.

    Currently relies on the template having a sheet called 'data_Params', with the columns laid out
    as configured in this source code. Only works on Windows. 
    """
    with DB(config=config) as db:
        session = db.session()
        directorates = session.query(directorate).filter(
            directorate.director_name.isnot(None)).all()

        # Create an excel app
        xlapp = win32com.client.DispatchEx("Excel.Application")
        xlapp.DisplayAlerts = False
        # Open the workbook in said instance of Excel
        wb = xlapp.workbooks.open(template)
        ws = wb.Worksheets("data_Params")
        with click.progressbar(directorates) as bar:
            for d in bar:
                ws.Range("A2").Value = d.directorate_id
                ws.Range("D2").Value = d.description
                ws.Range("E2").Value = d.director_name
                filename = folder + '\\' + d.description + '.xlsm'
                macro_name = "'" + wb.name + "'!Automation.UpdateRefreshConnections"
                xlapp.Run(macro_name)
                wb.SaveAs(filename)
        xlapp.quit
