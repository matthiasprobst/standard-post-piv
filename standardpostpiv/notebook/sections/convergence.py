from .cells import code_cells, markdown_cells
from .core import NotebookSection


class ConvergenceSection(NotebookSection):

    def get_cells(self):
        cells = [markdown_cells(["### PIV Convergence",
                                 "",
                                 "To judge the PIV convergence it is helpful to plot the `running mean`, the `running",
                                 "standard deviation` and the `running relative standard deviation` at various discrete",
                                 "points."]), ]

        if self.notebook.report.is_snapshot():
            cells.append(markdown_cells('No convergence for snapshot data'))
        elif self.notebook.report.is_snapshot():
            cells.append(code_cells(["_shape = report.velocity.inplane_velocity.shape",
                                     "iy, ix = _shape[0] // 2, _shape[1] // 2",
                                     "",
                                     "fig, axs = plt.subplots(1, 2, figsize=(10, 4))",
                                     "report.velocity.inplane_velocity[:, iy, ix].running_mean().plot(ax=axs[0])",
                                     "report.velocity.inplane_velocity[:, iy, ix].running_std().plot(ax=axs[0])",
                                     "report.velocity.inplane_velocity[:, iy, ix].running_relative_standard_deviation().plot(ax=axs[1])",
                                     "plt.tight_layout()"]))
        else:
            cells.append(markdown_cells('No convergence implemented yet (!) for mplane data'))

        return cells


__title__ = """### PIV Convergence

To judge the PIV convergence it is helpful to plot the `running mean`, the `running
standard deviation` and the `running relative standard deviation` at various discrete points"""


def plot_plane_velocity(report):
    report.add_code_cell(["_shape = report.velocity.inplane_velocity.shape",
                          "iy, ix = _shape[0] // 2, _shape[1] // 2",
                          "",
                          "fig, axs = plt.subplots(1, 2, figsize=(10, 4))",
                          "report.velocity.inplane_velocity[:, iy, ix].running_mean().plot(ax=axs[0])",
                          "report.velocity.inplane_velocity[:, iy, ix].running_std().plot(ax=axs[0])",
                          "report.velocity.inplane_velocity[:, iy, ix].running_relative_standard_deviation().plot(ax=axs[1])",
                          "axs[0].set_title(f'running variables\\nx : {report.x[ix]:f} {report.x.attrs[\"units\"]}, y : {report.y[iy]:f} {report.y.attrs[\"units\"]}')",
                          "axs[1].set_title(f'relative running standard deviation (significance)\\nx : {report.x[ix]:f} {report.x.attrs[\"units\"]}, y : {report.y[iy]:f} {report.y.attrs[\"units\"]}')",
                          "plt.tight_layout()"])
