from .cells import markdown_cells, code_cells
from .core import NotebookSection


class StatisticsSection(NotebookSection):
    """Title section of the report"""

    def get_cells(self):
        """write the cells"""
        return [markdown_cells(['## Statistics', ]),
                code_cells(["inplane_vector_stats = report.velocity.inplane_vector.ssp.stats()",
                            "print('Statistics of inplane velocity vector:')",
                            "inplane_vector_stats"]), ]
