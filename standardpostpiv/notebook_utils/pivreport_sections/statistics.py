mk1 = """Find out what the PIV method is, the final window size, etc.:"""

cell1 = """from standardpostpiv import badge, StandardPIVResult
from standardpostpiv.flags import eval_flags"""

mk2 = """Initialize a helper class around the PIV result HDF5 file:"""

cell2 = """res = StandardPIVResult(hdf_filename)"""

mk3 = """Compute the valid detection probability (VDP):"""

cell3 = """import numpy as np
flag_series = eval_flags(res.piv_flags[()])
edited_vectors = np.sum([flag_series[f] for f in ('NORESULT', 'FILTERED', 'INTERPOLATED', 'REPLACED', 'MANUALEDIT')], axis=0)
vdp = (flag_series['ACTIVE']-edited_vectors)/flag_series['ACTIVE']
vdp.attrs['standard_name'] = 'valid_detection_probability'
vdp.name = 'vdp'
vdp.attrs['units'] = ''"""

mk4 = """Get a broad overview of the file:"""

cell4_badge = """badge.display(method=res.eval_method,
              final_ws=res.final_iw_size,
              piv_dim=res.piv_dim,
              piv_type=res.piv_type,
              magnification=str(float(res.piv_scaling_factor[()].data)) + res.piv_scaling_factor.attrs['units'],
              vdp=f'{np.mean(vdp):.2f}',
              color=['green', 'blue', 'yellow', None, 'orange'], inline=True)"""

cell4_dict = """stats = {'PIV Eval method': res.eval_method,
         'PIV final window size': res.final_iw_size,
         'PIV Dimension': res.piv_dim,
         'PIV Type': res.piv_type,
         'PIV magnification': str(float(res.piv_scaling_factor[()].data)) + res.piv_scaling_factor.attrs['units'],
         'Valid detection probability': round(float(np.mean(vdp)), 2)}

from pprint import pprint
pprint(stats)"""

cell5 = """import standardpostpiv.plotting as stdplt 
fig, axes = stdplt.subplots(1, 1, tight_layout=True)
vdp.plot(ax=axes)"""

from standardpostpiv.notebook_utils.section import Section


def _build_section(shield_badge=True):
    _section = Section('Stats', label='stats')
    _section.add_cell(mk1, 'markdown')
    _section.add_cell(cell1, 'code')
    _section.add_cell(mk2, 'markdown')
    _section.add_cell(cell2, 'code')
    _section.add_cell(mk3, 'markdown')
    _section.add_cell(cell3, 'code')
    _section.add_cell(mk4, 'markdown')
    if shield_badge:
        _section.add_cell(cell4_badge, 'code')
    else:
        _section.add_cell(cell4_dict, 'code')

    _section.add_cell(cell5, 'code')
    return _section


# def extract_imports(section):
#     code_cells = [c for c in section.cells if c.is_code()]
#     import_lines = []
#     new_cell_lines = []
#     for cell in code_cells:
#         lines = cell.lines.split('\n')
#         import_free_lines = []
#         for line in lines:
#             if 'import' in line:
#                 import_lines.append(line)
#             else:
#                 import_free_lines.append(line)
#
#         if len(import_free_lines) > 0:
#             new_cell_lines.append('\n'.join(import_free_lines))
#
#     print(set(import_lines))
#     return new_cell_lines


section_with_badge = _build_section(True)
# new_cells = extract_imports(section_with_badge)
section_without_badge = _build_section(False)
