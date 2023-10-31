import abc

from .cells import markdown_cells


class NotebookSection:
    """Multiple cells as a logical section in a notebook"""

    def __init__(self, notebook, title, level=1, label=None):
        self.notebook = notebook
        self.title = title
        self.level = level
        self.label = label

    def build_title(self):
        level_str = '#' * self.level
        return markdown_cells(f'{level_str} {self.title} <a id="{self.label}"></a>')

    def __get_cells__(self):
        return [self.build_title(), *self.get_cells()]

    @abc.abstractmethod
    def get_cells(self):
        """return list of cells"""
