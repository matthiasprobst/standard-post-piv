from standardpostpiv.notebook_utils.cells import markdown_cells, code_cells

from standardpostpiv.notebook_utils.section import Section

__cells = [markdown_cells("""Analysis of the velocity fields"""),
           code_cells("""from standardpostpiv.utils import compute_magnitude
import xarray as xr"""), markdown_cells("""Velocity magnitude for each time step:"""),
           code_cells("""displacement_magnitude = xr.concat(
    [compute_magnitude(dx[i,...], dy[i,...]) for i in range(dx.coords['reltime'].size)], 'reltime'
)
displacement_magnitude.attrs['standard_name'] = 'magnitude_of_displacement'"""),
           markdown_cells(
               """Ensemble mean of velocity magnitude (compute the mean for each time step an then compute mean)""")]

main_section = Section('Displacement fields', label='displacement_fields')

for cell in __cells:
    main_section.add_cell(cell)

section_instantaneous_velocity = Section('Displacement fields at specific time stamps', label='inst_vel')

__cells = [code_cells("""it = 2

fig, axes = stdplt.subplots(1, 3, figsize=(12, 3), tight_layout=True)
displacement_magnitude.isel(reltime=it).plot(ax=axes[0])
# axes.pivstreamplot(dx.mean('reltime')[:,:], dy.mean('reltime')[:,:], color='k')
axes[0].pivquiver(dx.isel(reltime=it)[:,:], dy.isel(reltime=it)[:,:], color='k', every=8)

dx.isel(reltime=it).plot(ax=axes[1])
dy.isel(reltime=it).plot(ax=axes[2])
for ax in axes:
    ax.set_aspect('equal')""")]

for cell in __cells:
    section_instantaneous_velocity.add_cell(cell)

section_mean_displacement = Section('Mean displacement fields', label='mean_velocity')

__cells = [code_cells("""fig, axes = stdplt.subplots(1, 3, figsize=(12, 3), tight_layout=True)
displacement_magnitude.stdpiv.mean('reltime').plot(ax=axes[0])
# axes.pivstreamplot(dx.mean('reltime')[:,:], dy.mean('reltime')[:,:], color='k')
axes[0].pivquiver(dx.mean('reltime')[:,:], dy.mean('reltime')[:,:], color='k', every=8)

dx.stdpiv.mean('reltime').plot(ax=axes[1])
dy.stdpiv.mean('reltime').plot(ax=axes[2])
for ax in axes:
    ax.set_aspect('equal')""")]

for cell in __cells:
    section_mean_displacement.add_cell(cell)
