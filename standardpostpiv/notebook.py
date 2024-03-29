"""Main module for creating a PIV report notebook"""
import pathlib
from typing import Union, Dict

import nbformat
import numpy as np
from nbconvert import PDFExporter, HTMLExporter
from nbconvert.exporters import export, pdf
from nbconvert.preprocessors import ExecutePreprocessor

from .logger import logger
from .notebook_utils.cells import markdown_cells
from .notebook_utils.section import Section
from .notebook_utils.toc import generate_toc_html


class PIVReportNotebook:
    __slots__ = ('hdf_filename', 'notebook', 'sections', 'notebook_filename')

    def __init__(self, hdf_filename):
        self.sections = []
        self.notebook = None
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

    def execute(self, inplace=True, to_html=False, to_pdf=False) -> Dict:
        """Execute the notebook and optionally save it as html or pdf

        Parameters
        ----------
        inplace: bool
            If True, the notebook is executed in place. Otherwise, a new notebook is created.
        to_html: bool
            If True, the notebook is converted to html.
        to_pdf: bool
            If True, the notebook is converted to pdf. Note that ioshield badges cannot be displayed in pdf.
            An error will be raised!

        Returns
        -------
        filenames: Dict
            Dictionary containing the filenames of the executed notebook and the html/pdf file.
        """
        assert self.notebook_filename.exists()
        if inplace:
            cmd = f'jupyter nbconvert --execute "{self.notebook_filename}" --inplace'
        else:
            cmd = f'jupyter nbconvert --execute --to notebook "{self.notebook_filename}"'
        if to_html:
            cmd += ' --to html'
        elif to_pdf:
            cmd += ' --to pdf'

        logger.debug(f'jupyter nbconvert command: {cmd}')

        # import nbformat
        # with open(self.notebook_filename) as f:
        #     nb = nbformat.read(f, as_version=4)

        ep = ExecutePreprocessor(timeout=600, kernel='python3')
        ep.allow_errors = True
        ep.store_widget_state = False
        ep.preprocess(self.notebook)

        if inplace:
            # execute the notebook
            with open(self.notebook_filename, 'w', encoding='utf-8') as f:
                nbformat.write(self.notebook, f)

        if to_pdf:
            pdf_filename = self.notebook_filename.parent / f'{self.notebook_filename.stem}.pdf'
            try:
                r, _ = export(PDFExporter, self.notebook)
            except pdf.LatexFailed as e:
                logger.error('Latex failed. Please check the log file for more information. Original error message: '
                             '{}'.format(e))
                pdf_filename = None
            else:
                with open(pdf_filename, 'w') as f:
                    f.write(r)
        else:
            pdf_filename = None

        if to_html:
            html_filename = self.notebook_filename.parent / f'{self.notebook_filename.stem}.html'
            html_data, _ = export(HTMLExporter, self.notebook)
            with open(html_filename, "w") as f:
                f.write(html_data)
        else:
            html_filename = None

        return {'ipynb': self.notebook_filename, 'html': html_filename, 'pdf': pdf_filename}

        # NotebookExporter().from_notebook_node(self.notebook)
        #
        # if 'win' in platform.system().lower():
        #     warnings.warn('There are some problems on windows system, that are not sorted out. The bash '
        #                   'script may fail. Reason for this most likely are the filenames')
        #     cmd = cmd.replace('\\', '/')
        # print(cmd)
        # success = subprocess.run(cmd, shell=True, capture_output=True)
        # if success.returncode != 0:
        #     warnings.warn(f'Notebook execution failed: {success.stderr.decode()}', UserWarning)
        # else:
        #     print(f'Notebook executed successfully')
        # return success

    def create(self,
               notebook_filename: Union[str, pathlib.Path] = None,
               execute_notebook: bool = False,
               overwrite: bool = False,
               inplace: bool = False,
               to_html: bool = False,
               to_pdf: bool = False) -> Dict:
        """Create the notebook and optionally execute it and save it as html or pdf

        Parameters
        ----------
        notebook_filename : str or pathlib.Path, optional
            Filename of the notebook. If None, the filename will be the same as the hdf_filename with the
            suffix `_StdPIVReport.ipynb` instead of `.hdf`
        execute_notebook : bool, optional
            If True, the notebook will be executed after creation
        overwrite : bool, optional
            If True, an existing notebook file will be overwritten
        inplace : bool, optional
            If True, the notebook will be executed in place. Otherwise, a new notebook will be created
        to_html : bool, optional
            If True, the notebook will be converted to html after execution
        to_pdf : bool, optional
            If True, the notebook will be converted to pdf after execution

        Returns
        -------
        filenames: Dict
            Dictionary containing the filenames of the executed notebook and the html/pdf file.

        """
        target_folder = self.hdf_filename.parent

        if notebook_filename is None:
            notebook_filename = target_folder / f'{self.hdf_filename.stem}_StdPIVReport.ipynb'
        else:
            notebook_filename = pathlib.Path(notebook_filename)

        if notebook_filename.exists() and not overwrite:
            raise FileExistsError(f'Notebook file {notebook_filename} already exists')

        print(f'Creating notebook: {notebook_filename.absolute()}')

        self.notebook_filename = notebook_filename

        root_section = self.sections[0]

        assert len(root_section.cells) > 0
        # add table of contents in second cell:
        _ = root_section.cells.insert(1, self._generate_toc_cell())

        cells = []
        level_numbers = np.zeros(10, dtype=int)

        # extract all imports and insert them in a separate section at the beginning
        import_lines = []
        for section in self.sections:
            iremove_cell = []
            for icell, cell in enumerate(section.cells):
                if cell.is_code():
                    import_free_lines = []
                    lines = cell.lines.split('\n')
                    for line in lines:
                        if 'import' in line:
                            import_lines.append(line)
                        else:
                            import_free_lines.append(line)
                    if len(import_free_lines) == 0:
                        iremove_cell.append(icell)
                    else:
                        cell.lines = '\n'.join(import_free_lines)
            for icell in iremove_cell[::-1]:
                logger.debug(f'Removing cell {icell} because it is empty.')
                section.cells.pop(icell)

        import_section = Section('Imports', label='imports')
        import_section.level = 2
        import_section.add_cell('\n'.join(import_lines), 'code')

        self.sections.insert(1, import_section)
        # for section in self.sections[2:]:
        #     section.level += 1

        for section in self.sections:
            cells, _ = section.get_cells(cells, level_numbers)

        notebook = nbformat.v4.new_notebook()

        notebook['cells'] = cells

        nbformat.write(notebook, str(notebook_filename))

        logger.info(f'Standard evaluation notebook will be written to: {notebook_filename.absolute()}')
        self.notebook = notebook

        if execute_notebook:
            logger.info(f'Executing the notebook: {notebook_filename}')
            return self.execute(inplace=inplace,
                                to_html=to_html,
                                to_pdf=to_pdf)
        return {'ipynb': notebook_filename, 'html': None, 'pdf': None}

    def _get_table_of_content_info(self):
        _toc_data = []
        for section in self.sections:
            _toc_data = section.get_toc(_toc_data)
        return _toc_data

    def _generate_toc_cell(self):
        html_string = generate_toc_html(self._get_table_of_content_info())
        return markdown_cells(html_string)
