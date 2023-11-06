from .cells import markdown_cells, code_cells, NotebookCells
from .toc import USECHAPTER


class Section:
    """A section of a notebook"""

    def __init__(self, title, label, level=None, report=None):
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
