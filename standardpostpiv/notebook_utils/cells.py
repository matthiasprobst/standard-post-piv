from enum import Enum

from nbformat.v4 import new_markdown_cell, new_code_cell


class CellType(Enum):
    MARKDOWN = 1
    CODE = 2


def make_markdown_cell(sources):
    if not isinstance(sources, list):
        sources = [sources]
    _sources = []
    for i, source in enumerate(sources):
        if source:
            if source[0] != '#':
                sources[i] = f'{source}<br>'

    cell_text = '\n'.join(sources)
    return new_markdown_cell(source=cell_text)


def make_code_cells(sources):
    if not isinstance(sources, list):
        sources = [sources]
    cell_text = '\n'.join(sources)
    return new_code_cell(source=cell_text)


class NotebookCells:
    """A collection of cells

    Parameters
    ----------
    ctype: CellType
        type of cells in this section

    """

    def __init__(self, ctype: CellType):
        self.lines = []
        self.ctype = ctype

    def __call__(self, lines):
        cells = NotebookCells(self.ctype)
        cells.lines = lines
        return cells

    def is_markdown(self):
        return self.ctype == CellType.MARKDOWN

    def is_code(self):
        return self.ctype == CellType.CODE

    def make(self):
        """return a valid notebook cell"""
        if self.ctype == CellType.MARKDOWN:
            return make_markdown_cell(sources=self.lines)
        elif self.ctype == CellType.CODE:
            return make_code_cells(sources=self.lines)


markdown_cells = NotebookCells(CellType.MARKDOWN)
code_cells = NotebookCells(CellType.CODE)
