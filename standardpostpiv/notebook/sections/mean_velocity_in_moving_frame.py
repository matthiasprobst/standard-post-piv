codecell_compute_and_plot = """import xarray as xr
urel = report.velocity.x[()].piv.in_moving_frame()
vrel = report.velocity.y[()].piv.in_moving_frame()
rel_vec = xr.Dataset(dict(urel=urel,vrel=vrel))
magrel = rel_vec.magnitude.compute_from('urel', 'vrel', name='magrel', inplace=False)

magrel.mean('time').plot()
rel_vec.isel(y=slice(None, None, yevery), x=slice(None, None, xevery)).mean('time').plot.quiver('x', 'y', 'urel', 'vrel')"""


def add_section(parent_section):
    section = parent_section.add_section('In moving frame of reference', 'velocity_in_moving_frame')
    section.add_cell(codecell_compute_and_plot, 'code')
    return section
