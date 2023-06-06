from .cells import markdown_cells, code_cells
from .core import NotebookSection
from ... import __version__


def make_badge(s1: str, s2: str, color: str):
    """make a badge"""
    return f'![nbviewer](https://img.shields.io/badge/{str(s1).replace(" ", "_")}-{str(s2).replace(" ", "_")}-{color}.svg)'


# ![nbviewer](https://img.shields.io/badge/piv_type-2D2C-orange.svg)
# ![nbviewer](https://img.shields.io/badge/software-PIVview_3.x.x-green.svg)


class TitleSection(NotebookSection):
    """Title section of the report"""

    def get_cells(self):
        """write the cells"""
        return [markdown_cells(['# PIV Report',
                                # 'Automatically created with<br>'
                                f'{make_badge("type", self.notebook.report.info()["pivtype"], "green")} '
                                f'{make_badge("method", self.notebook.report.info()["pivmethod"], "blue")} '
                                f'{make_badge("winsize", self.notebook.report.info()["final_iw_size"], "organe")}',
                                f'[{make_badge("contact", self.notebook.report.contact.replace("-", "--"), "red")}]({self.notebook.report.contact}) '
                                f'{make_badge("date", self.notebook.creation_datetime.strftime("%d/%m/%Y %H:%M:%S"), "lightgray")}',
                                f'{make_badge("standard_post_piv", __version__, "lightgray")}',
                                ]),
                code_cells(["import standardpostpiv as spp",
                            "import matplotlib.pyplot as plt",
                            "import warnings",
                            "warnings.filterwarnings('ignore')"]),
                code_cells([f'piv_filename = r"{self.notebook.report.filename.absolute()}"',
                            '',
                            'report = spp.Report(piv_filename)', ]),]
                # markdown_cells(['## General information', ]),
                # code_cells([f'info = report.info()',
                #             'for k, v in info.items():',
                #             '    print(f"{k:<20}: {v}")'])
                # ]
