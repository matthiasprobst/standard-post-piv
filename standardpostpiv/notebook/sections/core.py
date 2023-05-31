import abc


class NotebookSection:
    """Multiple cells as a logical section in a notebook"""

    def __init__(self, notebook):
        self.notebook = notebook

    @abc.abstractmethod
    def get_cells(self):
        """return list of cells"""
