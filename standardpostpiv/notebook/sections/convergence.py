markdown_title = """To judge the PIV convergence it is helpful to plot the `running mean`, the `running standard deviation` and the 
`running relative standard deviation` at various discrete points."""

code_define_monitors = """report.monitor_points.set([(40.3, 130.),
                           (80.0, 70.5),
                           (130, 90)])
# report.monitor_points.generate(report.mask.isel(time=0), 3, 3, ref=True)"""

code_plot_single_plane = """fig, axs = plt.subplots(1, 2, figsize=(14, 4))

report.monitor_points.plot(report.mask.isel(time=0), s=100, ax=axs[0])

for i, (ix, iy) in enumerate(report.monitor_points.indices):
    # report.velocity.x[:, iy, ix].piv.running_mean().plot(label=f'{i+1}', ax=axs[1])
    report.velocity.mag.isel(y=iy, x=ix).piv.running_mean().plot(label=f'{i+1}', ax=axs[1])

_ = axs[0].set_title('Monitor point definition')
_ = axs[1].set_title('Running mean of monitor points')
plt.legend()

plt.show()"""

code_plot_multi_plane = """for iz in range(report.z[()].size):
    fig, axs = plt.subplots(1, 2, figsize=(14, 4))

    report.mask.plot(cmap='binary', ax=axs[0])
    for i, pt in enumerate(report.seeding_points):
        axs[0].scatter(report.x[pt[1]], report.y[pt[0]], color='red', marker='+')

    for i, pt in enumerate(report.seeding_points):
        report.velocity.inplane_velocity[iz, :, pt[0], pt[1]].piv.running_mean().plot(label=f'{i+1}', ax=axs[1])

    _ = axs[0].set_title('Monitor point definition')
    _ = axs[1].set_title('Running mean of monitor points')
    plt.legend()

    plt.show()"""


def add_section(parent_section):
    section = parent_section.add_section('Convergence', 'convergence')
    section.add_cell(markdown_title, 'markdown')
    section.add_cell(code_define_monitors, 'code')
    if section.report.is_plane():
        section.add_cell(code_plot_single_plane, 'code')
    else:
        section.add_cell(code_plot_multi_plane, 'code')
    return section
