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



# import xarray as xr
# urel = report.velocity.x[()].piv.in_moving_frame(subtract=True)
# vrel = report.velocity.y[()].piv.in_moving_frame(subtract=True)
#
# rel_vec = xr.Dataset(dict(urel=urel, vrel=vrel))
# magrel = rel_vec.magnitude.compute_from('urel', 'vrel', name='magrel', inplace=False)
#
# magrel.mean('time').plot()
# rel_vec.isel(y=slice(None, None, yevery), x=slice(None, None, xevery)).mean('time').plot.quiver('x', 'y', 'urel', 'vrel', scale=200)
# report.velocity['x','y'][:, ::xevery, ::yevery].mean('time').plot.quiver('x', 'y', 'u', 'v', color='r', scale=200)
#
# mv_vec = xr.Dataset(dict(umv= report.velocity.x[()].u_rot, vmv= report.velocity.y[()].v_rot))
# # mv_vec.isel(y=slice(None, None, 12), x=slice(None, None, 12)).mean('time').plot.quiver('x', 'y', 'umv', 'vmv', color='g', scale=200)