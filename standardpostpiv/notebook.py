"""Main module for creating a PIV report notebook"""
import pathlib

import nbformat as nbf
import numpy as np

from .notebook_utils import pivreport_sections
from .notebook_utils.cells import markdown_cells
from .notebook_utils.section import Section
from .notebook_utils.toc import generate_toc_html


class PIVReportNotebook:
    __slots__ = ('hdf_filename', 'sections', 'notebook_filename')

    def __init__(self, hdf_filename):
        self.sections = []
        self.hdf_filename = pathlib.Path(hdf_filename)
        self.notebook_filename = None

        # create Title cell
        title_section = Section(f'PIV Report for "{self.hdf_filename.stem}"', 'piv-report')
        title_section.add_cell(markdown_cells('Automatically generated report.'))
        title_section.add_cell(f'hdf_filename = r"{self.hdf_filename.absolute()}"', 'code')
        self.add_section(title_section, level=1)
        # title_section = self.add_section(f'PIV Report for "{self.hdf_filename.stem}"', 'piv-report')

        # title_section.add_cell(code_cells(['import standardpostpiv as spp',
        #                                    'import matplotlib.pyplot as plt',
        #                                    'import warnings',
        #                                    "warnings.filterwarnings('ignore')"]))
        # title_section.add_cell(code_cells([f'piv_filename = r"{self.hdf_filename.absolute()}"',
        #                                    'report = spp.PIVReport(piv_filename)']))

    def add_section(self, section: Section, level: int):
        if not isinstance(section, Section):
            raise TypeError(f'section must be of type Section but got "{type(section)}"')
        section.level = level
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
            target_folder = self.hdf_filename.parent
        else:
            target_folder = pathlib.Path(target_folder)

        target_folder.mkdir(parents=True, exist_ok=True)

        if notebook_filename is None:
            notebook_filename = target_folder / f'{self.hdf_filename.stem}_standardpostpiv_standard_report.ipynb'

        if notebook_filename.exists() and not overwrite:
            raise FileExistsError(f'Notebook file {notebook_filename} already exists')

        self.notebook_filename = notebook_filename

        root_section = self.sections[0]

        if False:
            # add sections:
            if sections['overview']:
                new_section = pivreport_sections.overview.add_section(root_section)
            if sections['statistics']:
                new_section = pivreport_sections.statistics.add_section(root_section)
            if sections['convergence']:
                if sections['statistics']:
                    new_section = pivreport_sections.convergence.add_section(new_section)
                else:
                    new_section = pivreport_sections.convergence.add_section(root_section)
            if sections['mean_velocity']:
                new_section = pivreport_sections.mean_velocity.add_section(root_section)
            if sections['mean_velocity_in_moving_frame']:
                if sections['mean_velocity']:
                    new_section = pivreport_sections.mean_velocity_in_moving_frame.add_section(new_section)
                else:
                    new_section = pivreport_sections.mean_velocity_in_moving_frame.add_section(root_section)
            if sections['misc']:
                new_section = pivreport_sections.misc.add_section(root_section)

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
