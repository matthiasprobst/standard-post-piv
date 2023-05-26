import nbformat as nbf
import pathlib
import subprocess
# get current datetime:
from datetime import datetime
from nbformat.v4 import new_code_cell, new_markdown_cell

from h5postpiv.report import Report

now = datetime.now()


class PIVReportNotebook:
    """Create a Jupyter Notebook for a PIV report"""

    def __init__(self, filename, datetime=None):
        self.filename = pathlib.Path(filename)
        self.notebook_filename = None
        self._datetime = datetime
        self._cells = []

    @property
    def datetime(self):
        if self._datetime is None:
            self._datetime = datetime.now()
        return self._datetime

    def create(self,
               target_folder: pathlib.Path = None,
               execute_notebook=False,
               notebook_filename: pathlib.Path = None,
               overwrite: bool = False):

        if target_folder is None:
            target_folder = self.filename.parent
        else:
            target_folder = pathlib.Path(target_folder)

        target_folder.mkdir(parents=True, exist_ok=True)

        if notebook_filename is None:
            notebook_filename = target_folder / f'{self.filename.stem}_h5post_standard_report.ipynb'

        if notebook_filename.exists() and not overwrite:
            raise FileExistsError(f'Notebook file {notebook_filename} already exists')

        self.notebook_filename = notebook_filename

        notebook = self._make_cells()
        # Save the notebook to a file

        nbf.write(notebook, str(notebook_filename))

        print(f'Notebook created: {notebook_filename}')
        if execute_notebook:
            self.execute(overwrite_notebook=True)

        return notebook_filename

    def add_markdown_cell(self, sources):
        if not isinstance(sources, list):
            sources = [sources]
        _sources = []
        for i, source in enumerate(sources):
            if source:
                if source[0] != '#':
                    sources[i] = f'{source}<br>'

        cell_text = '\n'.join(sources)
        self._cells.append(new_markdown_cell(source=cell_text))

    def add_code_cell(self, sources):
        if not isinstance(sources, list):
            sources = [sources]
        cell_text = '\n'.join(sources)
        self._cells.append(new_code_cell(source=cell_text))

    def _make_cells(self):
        report = Report(self.filename)

        # Create a new notebook object
        notebook = nbf.v4.new_notebook()

        # Create a code cell

        self.add_markdown_cell(['# PIV Report',
                                f'contact: <a href={report.contact}>{report.contact}</a>',
                                f'date: {self.datetime.strftime("%d/%m/%Y %H:%M:%S")}'])

        self.add_code_cell(['import h5postpiv as pp',
                            'import matplotlib.pyplot as plt',
                            'import warnings',
                            'warnings.filterwarnings("ignore")'])

        self.add_code_cell(f'piv_filename = r"{self.filename.absolute()}"')

        self.add_code_cell('report = pp.Report(piv_filename)')

        self.add_code_cell(['info = report.info()',
                            'for k, v in info.items():',
                            '    print(f"{k:<20}: {v}")'])

        self.add_markdown_cell('## Statistics')

        self.add_code_cell(["inplane_vector_stats = report.velocity.inplane_vector.stats()",
                            "print('Statistics of inplane velocity vector:')",
                            "inplane_vector_stats"])

        self.add_markdown_cell('## Plots')
        self.add_markdown_cell('### Mean in-plane velocity')

        self.add_code_cell([
            "report.velocity.mean_inplane_velocity.plot.contourf_and_quiver(every=[4, 8], quiver_kwargs={'scale': 200})",
            "report.velocity.mean_inplane_velocity.stats()"])

        self.add_markdown_cell(["### PIV Convergence",
                                "",
                                "To judge the PIV convergence it is helpful to plot the `running mean`, the `runing "
                                "standard deviation` and the `runing relative standard deviation` at various discrete points"])
        self.add_code_cell(["_shape = report.velocity.inplane_velocity.shape",
                            "iy, ix = _shape[0] // 2, _shape[1] // 2",
                            "",
                            "fig, axs = plt.subplots(1, 2, figsize=(10, 4))",
                            "report.velocity.inplane_velocity[:, iy, ix].running_mean().plot(ax=axs[0])",
                            "report.velocity.inplane_velocity[:, iy, ix].running_std().plot(ax=axs[0])",
                            "report.velocity.inplane_velocity[:, iy, ix].running_relative_standard_deviation().plot(ax=axs[1])",
                            "axs[0].set_title(f'running variables\\nx : {report.x[ix]:f} {report.x.attrs[\"units\"]}, y : {report.y[iy]:f} {report.y.attrs[\"units\"]}')",
                            "axs[1].set_title(f'relative running standard deviation (significance)\\nx : {report.x[ix]:f} {report.x.attrs[\"units\"]}, y : {report.y[iy]:f} {report.y.attrs[\"units\"]}')",
                            "plt.tight_layout()"])

        self.add_markdown_cell(["### Along line"])

        """import xarray as xr
import numpy as np
nline = 31
time = 'mean'  # or physical time

# physical coordinates:
ip_coords = [{'x': xr.DataArray(np.linspace(600, 600, nline), dims='line'),
              'y': xr.DataArray(np.linspace(300, 900, nline), dims='line'),
              'kwargs': {'color': 'gray', 'marker': 'o'}},
             {'x': xr.DataArray(np.linspace(20, 900, nline), dims='line'),
              'y': xr.DataArray(np.linspace(600, 600, nline), dims='line'),
              'kwargs': {'color': 'gray', 'marker': '^'}}]

# select variable:
if time == 'mean':
    data = report.velocity.x[:].mean('time')
    data = report.velocity.mean_inplane_velocity.mag
else:
    # data = report.velocity.x[:].sel(time=time)
    data = report.velocity.inplane_velocity.mag.sel(time=time)

fig, axs = plt.subplots(1, 2, figsize=(10, 4))
data.plot.contourf(ax=axs[0], levels=21, cmap='jet')

line_data = []
for coord in ip_coords:
    xinterp = coord['x']
    yinterp = coord['y']
    
    axs[0].plot(xinterp, yinterp, **coord['kwargs'])

    dx=xinterp-xinterp[0]
    dy=yinterp-yinterp[0]
    
    s = xr.DataArray(data=np.sqrt(dx**2+dy**2), dims=('line',), attrs={'units': data.attrs['units']})
    
    line_data.append(data.interp(x=xinterp, y=yinterp))
    line_data[-1] = line_data[-1].assign_coords(line=s)
    line_data[-1].plot(ax=axs[1])
    # line_data[-1].assign_coords(line=np.sqrt(xinterp.diff('line')**2+yinterp.diff('line')**2))
    plt.tight_layout()"""
        self.add_code_cell(["import xarray as xr",
                            "import numpy as np",
                            "nline = 31",
                            "time = 'mean'  # or physical time",
                            "",
                            "# physical coordinates:",
                            "ip_coords = [{'x': xr.DataArray(np.linspace(600, 600, nline), dims='line'),",
                            "              'y': xr.DataArray(np.linspace(300, 900, nline), dims='line'),",
                            "              'kwargs': {'color': 'gray', 'marker': 'o'}},",
                            "             {'x': xr.DataArray(np.linspace(20, 900, nline), dims='line'),",
                            "              'y': xr.DataArray(np.linspace(600, 600, nline), dims='line'),",
                            "              'kwargs': {'color': 'gray', 'marker': '^'}}]",
                            "",
                            "# select variable:",
                            "if time == 'mean':",
                            "    data = report.velocity.x[:].mean('time')",
                            "    data = report.velocity.mean_inplane_velocity.mag",
                            "else:",
                            "    # data = report.velocity.x[:].sel(time=time)",
                            "    data = report.velocity.inplane_velocity.mag.sel(time=time)",
                            "",
                            "fig, axs = plt.subplots(1, 2, figsize=(10, 4))",
                            "data.plot.contourf(ax=axs[0], levels=21, cmap='jet')",
                            "",
                            "line_data = []",
                            "for coord in ip_coords:",
                            "    xinterp = coord['x']",
                            "    yinterp = coord['y']",
                            "    ",
                            "    axs[0].plot(xinterp, yinterp, **coord['kwargs'])",
                            "",
                            "    dx=xinterp-xinterp[0]",
                            "    dy=yinterp-yinterp[0]",
                            "    ",
                            "    s = xr.DataArray(data=np.sqrt(dx**2+dy**2), dims=('line',), attrs={'units': data.attrs['units']})",
                            "    ",
                            "    line_data.append(data.interp(x=xinterp, y=yinterp))",
                            "    line_data[-1] = line_data[-1].assign_coords(line=s)",
                            "    line_data[-1].plot(ax=axs[1])",
                            "    plt.tight_layout()"])

        # Add the code cell to the notebook
        notebook['cells'] = self._cells
        return notebook

    def execute(self, notebook_filename=None, inplace=False, html: bool = True, pdf: bool = True):
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

        exec_str_notebook = 'jupyter nbconvert --ExecutePreprocessor.store_widget_state=False --to notebook ' \
                            f'--execute {notebook_filename}'
        if html:
            exec_str_html = 'jupyter nbconvert --ExecutePreprocessor.store_widget_state=False --to html ' \
                            f'--execute {notebook_filename}'
        if pdf:
            exec_str_pdf = 'jupyter nbconvert --ExecutePreprocessor.store_widget_state=False --to pdf ' \
                           f'--execute {notebook_filename}'

        if inplace:
            exec_str_notebook += f' --output {notebook_filename}'
            exec_str_html += f' --output {notebook_filename.parent / notebook_filename.stem}.html'
            exec_str_pdf += f' --output {notebook_filename.parent / notebook_filename.stem}.pdf'

        else:
            exec_notebook_filename = notebook_filename.parent / f'{notebook_filename.stem}_executed.ipynb'
            exec_str_notebook += f' --output {exec_notebook_filename}'
            exec_notebook_filename_html = notebook_filename.parent / f'{notebook_filename.stem}_executed.html'
            exec_notebook_filename_pdf = notebook_filename.parent / f'{notebook_filename.stem}_executed.pdf'
            exec_str_html += f' --output {exec_notebook_filename_html}'
            exec_str_pdf += f' --output {exec_notebook_filename_pdf}'
        subprocess.run(exec_str_notebook.split(' '))
        if html:
            subprocess.run(exec_str_html.split(' '))
        if pdf:
            subprocess.run(exec_str_pdf.split(' '))
