codecells_info = """import h5rdmtoolbox as h5tbx
import pathlib
import numpy as np

import standardpostpiv.plotting as stdplt

_ = h5tbx.set_config(add_provenance=False)"""
from standardpostpiv.notebook_utils.section import Section

section = Section('Imports', label='imports')
section.add_cell(codecells_info, 'code')

# def add_section(parent_section):
#     section = parent_section.add_section('Imports', label='imports')
#     section.add_cell(codecells_info, 'code')
#     return section
