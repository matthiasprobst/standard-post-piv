import nbformat as nbf
import numpy as np
import pathlib

from . import sections as ntb_sections
from .sections.cells import markdown_cells, code_cells, NotebookCells
from .toc import generate_toc_html, USECHAPTER
from .. import core_logger


class Section:

    def __init__(self, title, label, level, report):
        self.title = title
        self.label = label
        self.level = level
        self.report = report
        self.sections = []
        self.cells = []

    def __repr__(self):
        return f'<Section title="{self.title}", n_sections={len(self.sections)}, n_cells={len(self.cells)}>'

    def _make_title(self, level_numbers):
        use_level = self.level - USECHAPTER
        if use_level > 0:
            level_numbers[use_level - 1] += 1
            level_numbers[use_level:] = 0
            section_num_str = '.'.join([str(_level) for _level in level_numbers[:use_level]])
            self.title = f'{section_num_str} {self.title}'
        return '#' * self.level + f' {self.title}', level_numbers

    def add_section(self, title, label=None, level=None):
        if level is None:
            level = self.level + 1
        section = Section(title, label, level, self.report)
        self.sections.append(section)
        return section

    def add_cell(self, cell, cell_type: str = None):
        if cell_type is None and isinstance(cell, NotebookCells):
            self.cells.append(cell)
        elif cell_type == 'markdown':
            self.cells.append(markdown_cells(cell))
        elif cell_type == 'code':
            self.cells.append(code_cells(cell))
        else:
            raise TypeError(f'Unknown cell type: {cell_type}')

    def __getitem__(self, item):
        return self.sections[item]

    def get_cells(self, cells, level_numbers):

        if not self.cells:
            return []

        _title, level_numbers = self._make_title(level_numbers)
        if self.label is None:
            title_cell = markdown_cells(f'{_title}')
        else:
            title_cell = markdown_cells(f'{_title} <a id="piv-{self.label}"></a>')

        if self.cells[0].is_markdown():
            # combine the title and the first markdown cell
            self.cells[0].lines = title_cell.lines + '\n' + self.cells[0].lines
        else:
            # add title in front of cells
            self.cells.insert(0, title_cell)

        for cell in self.cells:
            cells.append(cell.make())

        for section in self.sections:
            cells, level_numbers = section.get_cells(cells, level_numbers)

        return cells, level_numbers

    def get_toc(self, toc=None):
        if toc is None:
            toc = []
        if self.level > 0:
            toc.append((self.level, self.title, self.label))
        else:
            toc = []
        for section in self.sections:
            toc = section.get_toc(toc)
        return toc


class PIVReportNotebook:
    __slots__ = ('report', 'sections', 'notebook_filename')

    def __init__(self, report):
        self.sections = []
        self.report = report
        self.notebook_filename = None

        # create Title cell
        title_section = self.add_section('PIV Report', 'piv-report')
        title_section.add_cell(markdown_cells('Automatically generated report.'))
        title_section.add_cell(code_cells(['import standardpostpiv as spp',
                                           'import matplotlib.pyplot as plt',
                                           'import warnings',
                                           "warnings.filterwarnings('ignore')"]))
        title_section.add_cell(code_cells([f'piv_filename = r"{self.report.filename.absolute()}"',
                                           'report = spp.PIVReport(piv_filename)']))

    def add_section(self, title, label=None):
        section = Section(title, label, level=1, report=self.report)
        self.sections.append(section)
        return section

    def create(self,
               target_folder: pathlib.Path = None,
               execute_notebook: bool = False,
               notebook_filename: pathlib.Path = None,
               overwrite: bool = False,
               inplace: bool = False,
               to_html: bool = False,
               to_pdf: bool = False,
               # available pre-defined sections:
               sections={'overview': True,
                         'statistics': True,
                         'convergence': True,
                         'mean_velocity': True,
                         'mean_velocity_in_moving_frame': True,
                         'misc': True}):

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

        root_section = self.sections[0]

        # add sections:
        if sections['overview']:
            new_section = ntb_sections.overview.add_section(root_section)
        if sections['statistics']:
            new_section = ntb_sections.statistics.add_section(root_section)
        if sections['convergence']:
            if sections['statistics']:
                new_section = ntb_sections.convergence.add_section(new_section)
            else:
                new_section = ntb_sections.convergence.add_section(root_section)
        if sections['mean_velocity']:
            new_section = ntb_sections.mean_velocity.add_section(root_section)
        if sections['mean_velocity_in_moving_frame']:
            if sections['mean_velocity']:
                new_section = ntb_sections.mean_velocity_in_moving_frame.add_section(new_section)
            else:
                new_section = ntb_sections.mean_velocity_in_moving_frame.add_section(root_section)
        if sections['misc']:
            new_section = ntb_sections.misc.add_section(root_section)

        assert len(root_section.cells) > 0
        # add table of contents in second cell:
        _ = root_section.cells.insert(1, self._generate_toc_cell())

        cells = []
        level_numbers = np.zeros(10, dtype=int)
        for section in self.sections:
            cells, _ = section.get_cells(cells, level_numbers)

        notebook = nbf.v4.new_notebook()

        notebook['cells'] = cells

        nbf.write(notebook, str('test.ipynb'))

        if execute_notebook:
            core_logger.debug(f'Executing the notebook: {notebook_filename}')
            self.execute(inplace=inplace,
                         to_html=to_html,
                         to_pdf=to_pdf)

    def _get_table_of_content_info(self):
        _toc_data = []
        for section in self.sections:
            _toc_data = section.get_toc(_toc_data)
        return _toc_data

    def _generate_toc_cell(self):
        html_string = generate_toc_html(self._get_table_of_content_info())
        return markdown_cells(html_string)
