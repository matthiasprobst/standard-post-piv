from .cells import markdown_cells, code_cells
from .core import NotebookSection


class TitleSection(NotebookSection):
    """Title section of the report"""

    def get_cells(self):
        """write the cells"""
        return [markdown_cells(['# PIV Report',
                                'Automatically created with '
                                '[`standard-post-piv`](https://github.com/matthiasprobst/standard-post-piv):',
                                f'  * date: {self.notebook.creation_datetime.strftime("%d/%m/%Y %H:%M:%S")}',
                                f'  * contact: <a href={self.notebook.report.contact}>{self.notebook.report.contact}'
                                f'</a>', ]),
                code_cells(["import standardpostpiv as spp",
                            "import matplotlib.pyplot as plt",
                            "import warnings",
                            "warnings.filterwarnings('ignore')"]),
                code_cells([f'piv_filename = r"{self.notebook.report.filename.absolute()}"',
                            '',
                            'report = spp.Report(piv_filename)', ]),
                markdown_cells(['## General information',]),
                code_cells([f'info = report.info()',
                            'for k, v in info.items():',
                            '    print(f"{k:<20}: {v}")'])
                ]
