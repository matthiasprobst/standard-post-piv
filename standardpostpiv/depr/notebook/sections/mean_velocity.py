codecell_compute_mean_vel = """cmean = report.velocity.mag[()].mean('time')
umean = report.velocity.x[()].mean('time')
vmean = report.velocity.y[()].mean('time')"""

codecell_plot_mean_vel = """xevery, yevery = 4, 4
cmean.plot()
report.velocity['x','y'][0, ::xevery, ::yevery].plot.quiver('x', 'y', 'u', 'v')"""


def add_section(parent_section):
    section = parent_section.add_section('Velocity', 'velocity')
    section.add_cell(codecell_compute_mean_vel, 'code')
    section.add_cell(codecell_plot_mean_vel, 'code')
    return section
