import nbformat as nbf
import pathlib

from .sections.cells import markdown_cells, code_cells, NotebookCells
from .toc import generate_toc_html
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

    def _make_title(self):
        return '#' * self.level + f' {self.title}'

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

    def get_cells(self, cells):
        if not self.cells:
            return []
        if self.label is None:
            title_cell = markdown_cells(f'{self._make_title()}')
        else:
            title_cell = markdown_cells(f'{self._make_title()} <a id="piv-{self.label}"></a>')

        if self.cells[0].is_markdown():
            # combine the title and the first markdown cell
            self.cells[0].lines = title_cell.lines + '\n' + self.cells[0].lines
        else:
            # add title in front of cells
            self.cells.insert(0, title_cell)

        for cell in self.cells:
            cells.append(cell.make())

        for section in self.sections:
            cells = section.get_cells(cells)

        return cells

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
               overview: bool = True,
               statistics: bool = True,
               convergence: bool = True, ):

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
        if overview:
            from .sections.overview import add_section
            new_section = add_section(root_section)
        if statistics:
            from .sections.statistics import add_section
            new_section = add_section(root_section)
        if convergence:
            from .sections.convergence import add_section
            if statistics:
                new_section = add_section(new_section)
            else:
                new_section = add_section(root_section)

        assert len(root_section.cells) > 0
        # add table of contents in second cell:
        root_section.cells.insert(1, self._generate_toc_cell())

        cells = []
        for section in self.sections:
            cells = section.get_cells(cells)

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
