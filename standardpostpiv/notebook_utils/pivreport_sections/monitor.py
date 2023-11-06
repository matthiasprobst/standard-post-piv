from standardpostpiv.notebook_utils.cells import code_cells
from standardpostpiv.notebook_utils.cells import markdown_cells
from standardpostpiv.notebook_utils.section import Section


def points():
    __cells = [code_cells("""n_pts = 4
np.random.seed(10)
mp_x = np.random.uniform(low=res.x_coordinate[0], high=res.x_coordinate[-1], size=4)
mp_y = np.random.uniform(low=res.y_coordinate[0], high=res.y_coordinate[-1], size=4)"""),
               code_cells("""from standardpostpiv.utils import MaskSeeder"""),
               code_cells("""# random seed:
monitor_points = MaskSeeder(res.get_mask()[0,:,:],
                            res.x_coordinate,
                            res.y_coordinate,
                            n=4, min_dist=20).generate(ret_indices=False)
# manually:
# monitor_points = [(130, 100, 20, 50), (25, 30.5, 100, 200)]"""),
               code_cells("""fig, axes = stdplt.subplots(1, 2, figsize=(10, 3), tight_layout=True)
displacement_magnitude.stdpiv.mean('reltime').plot(ax=axes[0])
axes[0].set_aspect(1)

for x, y in monitor_points:
    m, c = next(stdplt.markers), next(stdplt.gray_colors)
    monitor_pt = displacement_magnitude.sel(x=x, y=y)
    line = monitor_pt.plot(ax=axes[1], marker='', color=c)
    # mark first and last point:
    axes[1].scatter(monitor_pt.reltime[0], monitor_pt[0], marker=m, color=line[0].get_color())
    axes[1].scatter(monitor_pt.reltime[-1], monitor_pt[-1], marker=m, color=line[0].get_color())
    axes[0].scatter(monitor_pt.x, monitor_pt.y, marker=m, color=line[0].get_color())"""),
               ]

    section_monitor_points = Section('Monitor points', label='monitor_points')
    for cell in __cells:
        section_monitor_points.add_cell(cell)
    return section_monitor_points


def convergence():
    """Build convergence section."""
    section_convergence = Section('Convergence', label='convergence')

    __cells = [markdown_cells(r"""Convergence or "significance" is judged by analyzing the evolution the running standard deviation $\sigma_r$ in relation to the running mean $\mu_r$:
\begin{equation}
    s = \frac{\sigma_r}{\mu_r}
\end{equation}"""),
               code_cells("""displacement_magnitude.standard_name"""),
               code_cells("""displacement_magnitude.stdpiv.mean('reltime').standard_name"""),
               code_cells("""fig, axes = stdplt.subplots(1, 3, figsize=(10, 3), tight_layout=True)

displacement_magnitude.stdpiv.mean('reltime').plot(ax=axes[0])
axes[0].set_aspect(1)

ddof = 2

rrsd = displacement_magnitude.stdpiv.compute_developing_relative_standard_deviation(dim='reltime', ddof=ddof)
mag_develop_mean = displacement_magnitude.stdpiv.compute_developing_mean(dim='reltime')

_norm_displ_mag = displacement_magnitude / displacement_magnitude.mean()
_norm_displ_mag.attrs['standard_name'] = 'normalized_magnitude'
norm_mag_develop_std = _norm_displ_mag.stdpiv.compute_developing_std(dim='reltime', ddof=ddof)

# ax2 = axes[1].twinx()
for x, y in monitor_points:
    m, c = next(stdplt.markers), next(stdplt.gray_colors)

    # get data at monitor locations:
    # monitor_rrsd = rrsd.sel(x=x, y=y, method='nearest')

    # plot developing properties:
    data = mag_develop_mean.sel(x=x, y=y, method='nearest')
    normalize_data = data/data[-1]  # normalize with mean, which is the last
    line = normalize_data[1:].plot(color=c, ax=axes[1])
    # line = monitor_rrsd.plot(color=c)
    
    # axes[1].scatter(monitor_rrsd.reltime[ddof+1], monitor_rrsd[ddof+1], marker=m, color=line[0].get_color())
    # axes[1].scatter(monitor_rrsd.reltime[-1], monitor_rrsd[-1], marker=m, color=line[0].get_color())
    axes[0].scatter(x, y, marker=m, color=line[0].get_color())
    
    # data = mag_develop_std.sel(x=x, y=y, method='nearest')
    # data = data/data[-1]
    # line = data[1:].plot(color=line[0].get_color(), ax=axes[2], linestyle='--')

    line = norm_mag_develop_std.sel(x=x, y=y, method='nearest').plot(color=line[0].get_color(), ax=axes[2], linestyle='--')

axes[1].set_ylabel('dev mean')
axes[2].set_ylabel('dev std')"""),
               ]

    for cell in __cells:
        section_convergence.add_cell(cell)

    return section_convergence


def line(linedata):
    section_monitor_line = Section('Monitor line', label='monitor_line')
    __cells = [code_cells("""fig, axes = stdplt.subplots(1, 1)

mean_abs_displacement = displacement_magnitude.sel(y=80, method='nearest').mean('reltime')
max_abs_displacement = displacement_magnitude.sel(y=80, method='nearest').max('reltime')
min_abs_displacement = displacement_magnitude.sel(y=80, method='nearest').min('reltime')
std_abs_displacement = displacement_magnitude.sel(y=80, method='nearest').std('reltime')

max_abs_displacement.plot(ax=axes, linestyle='--', label='min/max', color='lightgray')
min_abs_displacement.plot(ax=axes, linestyle='--', color='lightgray')
mean_abs_displacement.plot(ax=axes, label='mean', color='k')

axes.fill_between(mean_abs_displacement.x,
                  (mean_abs_displacement-std_abs_displacement), (mean_abs_displacement+std_abs_displacement),
                 color='lightgray', label='$\sigma$')

axes.set_ylabel('magnitude of displacement / pixel')
stdplt.legend()""")]
    for cell in __cells:
        section_monitor_line.add_cell(cell)
    return section_monitor_line
