def make_title(report):
    report.add_markdown_cell("### Along line")


def plot_along_lines(report,
                     x: str,
                     y: str):
    """make a single plot along a line. x and y must be explicit lists of values or string of a numpy
    object, e.g. 'np.linspace(0, 10, 11)'"""
    report.add_code_cell(f"""import xarray as xr
import numpy as np

# physical coordinates:
ip_coords = [{{'x': xr.DataArray({x}, dims='line'),
              'y': xr.DataArray({y}, dims='line'),
              'kwargs': {{'color': 'gray', 'marker': 'o'}}}},
              ]

# select variable:
data = report.velocity.inplane_velocity

fig, axs = plt.subplots(1, 2, figsize=(10, 4))
data.plot.contourf(ax=axs[0], levels=21, cmap='jet')

line_data = []
for coord in ip_coords:
    xinterp = coord['x']
    yinterp = coord['y']

axs[0].plot(xinterp, yinterp, **coord['kwargs'])

dx=xinterp-xinterp[0]
dy=yinterp-yinterp[0]

s = xr.DataArray(data=np.sqrt(dx**2+dy**2), dims=('line',), attrs={{'units': data.attrs['units']}})

line_data.append(data.interp(x=xinterp, y=yinterp))
line_data[-1] = line_data[-1].assign_coords(line=s)
line_data[-1].plot(ax=axs[1])
# line_data[-1].assign_coords(line=np.sqrt(xinterp.diff('line')**2+yinterp.diff('line')**2))
plt.tight_layout()""")
