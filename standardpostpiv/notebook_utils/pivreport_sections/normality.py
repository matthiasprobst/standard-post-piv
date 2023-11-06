from standardpostpiv.notebook_utils.cells import code_cells, markdown_cells

from standardpostpiv.notebook_utils.section import Section

__cells = [code_cells("""from standardpostpiv.statistics import is_gaussian"""),
           code_cells("""j, i = 10, 40

displ_mag_monitor_sample = displacement_magnitude[:, j, i]

fig, axes =stdplt.subplots(1,3, tight_layout=True, sharey=True)

dx[:, j, i].plot.hist(binwidth=1/2, ax=axes[0], density=True)
axes[0].plot_normal_distribution(dx[:, j, i], n=100)
axes[0].set_title('dx')

dy[:, j, i].plot.hist(binwidth=1/2, ax=axes[1], density=True)
axes[1].plot_normal_distribution(dy[:, j, i], n=100)
axes[1].set_title('dy')

# speeds:
displ_mag_monitor_sample.plot.hist(binwidth=1/2, ax=axes[2], density=True)
axes[2].plot_normal_distribution(displ_mag_monitor_sample, n=100)
is_gaussian(displ_mag_monitor_sample, axis=0, method='shapiro', alpha=0.05).values
axes[2].set_title('mag')
axes[0].set_ylabel('number of phases')
stdplt.show()"""),
           code_cells("""norm_res = is_gaussian(displacement_magnitude[:, :, :], axis=0, method='shapiro', alpha=0.05)
norm_res = norm_res.where(~res.piv_flags[0,...] & 2)
norm_res.plot(vmax=1, cmap=stdplt.get_discrete_cmap(['red', 'green']), levels=[0, 0.5, 1.0000000001])"""),

           ]

section_normality_check = Section('Normality check', label='normality_check')
for cell in __cells:
    section_normality_check.add_cell(cell)

section_monitor_point_convergence = Section('Convergence', label='convergence')

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
    section_monitor_point_convergence.add_cell(cell)
