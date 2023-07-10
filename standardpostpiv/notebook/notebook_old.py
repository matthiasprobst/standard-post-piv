import nbformat as nbf
import pathlib
import tqdm
from datetime import datetime
from nbclient import NotebookClient
from nbconvert.preprocessors import ExecutePreprocessor

from .sections import TitleSection, ConvergenceSection, StatisticsSection, VelocityPlots, MiscSection
from .. import core_logger

now = datetime.now()


class ProgressExecutePreprocessorWithProgressbar(ExecutePreprocessor):
    """adding tqdm progress bar to indicate how many cells are executed"""

    def preprocess(self, nb, resources=None, km=None):
        """overwrite original method to add tqdm.tqdm.
        Taken from https://github.com/jupyter/nbconvert/blob/main/nbconvert/preprocessors/execute.py
        """
        NotebookClient.__init__(self, nb, km)
        self.reset_execution_trackers()
        self._check_assign_resources(resources)

        total_cells = sum(1 for cell in nb.cells)  # if cell.cell_type == 'code')

        with self.setup_kernel():
            assert self.kc  # noqa
            info_msg = self.wait_for_reply(self.kc.kernel_info())
            assert info_msg  # noqa
            self.nb.metadata["language_info"] = info_msg["content"]["language_info"]
            for index, cell in tqdm.tqdm(enumerate(self.nb.cells),
                                         total=total_cells, desc="Executing", unit="cell(s)"):
                self.preprocess_cell(cell, resources, index)
        self.set_widgets_metadata()

        return self.nb, self.resources


class MonitorManager:

    def __init__(self, report):
        self.report = report
        self._data = []

    def add_line_plot(self, x: str, y: str):
        """add a line plot to the report"""
        self.report._data.append((x, y))


class PIVReportNotebook:
    """Create a Jupyter Notebook for a PIV report"""

    def __init__(self, report, dtime=None):
        self.report = report
        self.hdf_filename = pathlib.Path(report.filename)
        self.notebook_filename = None
        self._datetime = dtime
        self.sections = {'title': TitleSection(self, 'PIV Report', level=1),
                         'statistics': StatisticsSection(self, 'PIV Statistics', level=2, label='statistics'),
                         'convergence': ConvergenceSection(self, 'PIV Convergence', level=3, label='convergence'),
                         'velocity_plots': VelocityPlots(self, 'PIV Velocity', level=2, label='velocity_plots'),
                         'misc': MiscSection(self, 'Misc', level=2), }
        self._monitor = MonitorManager(self)

    @property
    def creation_datetime(self):
        if self._datetime is None:
            self._datetime = datetime.now()
        return self._datetime

    @property
    def monitor(self):
        return self._monitor

    def create(self,
               target_folder: pathlib.Path = None,
               execute_notebook=False,
               notebook_filename: pathlib.Path = None,
               overwrite: bool = False,
               inplace: bool = False,
               to_html: bool = False,
               to_pdf: bool = False):

        if target_folder is None:
            target_folder = self.report.filename.parent
        else:
            target_folder = pathlib.Path(target_folder)

        target_folder.mkdir(parents=True, exist_ok=True)

        if notebook_filename is None:
            notebook_filename = target_folder / f'{self.report.filename.stem}_standardpostpiv_standard_report.ipynb'

        if notebook_filename.exists() and not overwrite:
            raise FileExistsError(f'Notebook file {notebook_filename} already exists')

        self.notebook_filename = notebook_filename

        core_logger.debug(f'Notebook filename: {notebook_filename}')

        # Create a new notebook object
        notebook = nbf.v4.new_notebook()

        core_logger.debug(f'Section names: {list(self.sections.keys())}')

        # Add the code cell to the notebook
        _cells = [section.__get_cells__() for section in self.sections.values()]
        # flatten the list:
        notebook['cells'] = [item.make() for sublist in _cells for item in sublist]

        # Save the notebook to a file
        core_logger.debug(f'Writing notebook to {notebook_filename}')
        nbf.write(notebook, str(notebook_filename))

        if execute_notebook:
            core_logger.debug(f'Executing the notebook: {notebook_filename}')
            self.execute(inplace=inplace,
                         to_html=to_html,
                         to_pdf=to_pdf)

        return notebook_filename

    def execute(self, notebook_filename=None,
                inplace=False,
                to_html: bool = False,
                to_pdf: bool = False):
        """Execute the notebook and save the output. If `inplace` is True,
        the notebook is executed. If False a new notebook is created with the
        suffix `_executed` appended to the filename. The original notebook is
        not modified."""
        if notebook_filename is None:
            if self.notebook_filename is None:
                raise ValueError('Notebook filename not set.')
            notebook_filename = pathlib.Path(self.notebook_filename)
        else:
            notebook_filename = pathlib.Path(notebook_filename)

        with open(notebook_filename) as f:
            nb = nbf.read(f, as_version=4)
        ep = ProgressExecutePreprocessorWithProgressbar(timeout=600, kernel_name='python3')

        out = ep.preprocess(nb, {'metadata': {'path': ''}})

        if inplace:
            output_notebook_filename = notebook_filename
        else:
            output_notebook_filename = notebook_filename.parent / f'{notebook_filename.stem}_executed.ipynb'

        with open(output_notebook_filename, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)

        if to_html:
            import subprocess
            core_logger.debug(f'jupyter nbconvert --to html {output_notebook_filename}')
            subprocess.run(f'jupyter nbconvert --to html {output_notebook_filename}'.split(' '))

        if to_pdf:
            import subprocess
            core_logger.debug(f'jupyter nbconvert --to pdf {output_notebook_filename}')
            subprocess.run(f'jupyter nbconvert --to pdf {output_notebook_filename}'.split(' '))
