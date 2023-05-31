import h5rdmtoolbox as h5tbx
from .cells import markdown_cells, code_cells
from .core import NotebookSection


class MiscSection(NotebookSection):
    """Title section of the report"""

    def get_cells(self):
        """write the cells"""
        return [markdown_cells(['## Misc', ]),
                code_cells(["import h5rdmtoolbox as h5tbx",
                            "h5tbx.dump(piv_filename)"]), ]
