mk1 = """Find out what the PIV method is, the final window size, etc.:"""

cell1 = """from standardpostpiv import badge, StandardPIVResult
from standardpostpiv.flags import eval_flags"""

mk2 = """Initialize a helper class around the PIV result HDF5 file:"""

cell2 = """res = StandardPIVResult(hdf_filename)"""

mk3 = """Compute the valid detection probability (VDP):"""

cell3 = """flag_series = eval_flags(res.piv_flags[()])
edited_vectors = np.sum([flag_series[f] for f in ('NORESULT', 'FILTERED', 'INTERPOLATED', 'REPLACED', 'MANUALEDIT')], axis=0)
vdp = (flag_series['ACTIVE']-edited_vectors)/flag_series['ACTIVE']
vdp.attrs['standard_name'] = 'valid_detection_probability'
vdp.name = 'vdp'
vdp.attrs['units'] = ''"""

mk4 = """Get a broad overview of the file:"""

cell4 = """def to_quantity(da):
    if da.ndim == 0:
        return h5tbx.get_ureg().Quantity(da.data, units=da.units)
        
badge.display(method=res.eval_method,
              final_ws=res.final_iw_size,
              piv_dim=res.piv_dim,
              piv_type=res.piv_type,
              magnification=str(to_quantity(res.piv_scaling_factor[()])),
              vdp=f'{np.mean(vdp):.2f}',
              color=['green', 'blue', 'yellow', None, 'orange'], inline=True)"""

cell5 = """fig, axes = stdplt.subplots(1, 1, tight_layout=True)
vdp.plot(ax=axes)"""

from standardpostpiv.notebook_utils.section import Section

section = Section('Stats', label='stats')
section.add_cell(mk1, 'markdown')
section.add_cell(cell1, 'code')
section.add_cell(mk2, 'markdown')
section.add_cell(cell2, 'code')
section.add_cell(mk3, 'markdown')
section.add_cell(cell3, 'code')
section.add_cell(mk4, 'markdown')
section.add_cell(cell4, 'code')
section.add_cell(cell5, 'code')
