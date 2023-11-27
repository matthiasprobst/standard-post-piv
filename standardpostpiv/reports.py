import pathlib
from typing import Union

from .notebook import PIVReportNotebook
from .notebook_utils.pivreport_sections import imports, statistics, pdfs, \
    displacement, monitor


def get_basic_2D2C_report(hdf_filename: Union[str, pathlib.Path]):
    """

    Parameters
    ----------
    hdf_filename: Union[str, pathlib.Path]
        HDF5 file containing the PIV data with standard names.

    Returns
    -------
    report: PIVReportNotebook
        The basic report with basic evaluation sections. Call `.create()` to build
        the corresponding notebook.

    Examples
    --------
    report = standardpostpiv.get_basic_2D2C_report()
    ntb = report.create(execute_notebook=True,
                        overwrite=False,
                        notebook_filename='my_piv_eval.ipynb',
                        inplace=True)
    """

    report = PIVReportNotebook(hdf_filename)

    # report.add_section(imports.section, level=2)
    report.add_section(statistics.section_with_badge, level=2)
    report.add_section(pdfs.section, level=2)
    report.add_section(displacement.main_section, level=2)
    report.add_section(displacement.section_mean_displacement, level=3)
    report.add_section(displacement.section_instantaneous_velocity, level=3)
    report.add_section(monitor.points(), level=2)
    report.add_section(monitor.convergence(), level=3)
    report.add_section(monitor.line(None), level=3)
    return report
