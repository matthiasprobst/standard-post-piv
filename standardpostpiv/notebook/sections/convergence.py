from .cells import code_cells, markdown_cells
from .core import NotebookSection


class ConvergenceSection(NotebookSection):

    def get_cells(self):
        if self.notebook.report.is_snapshot():
            return []

        cells = [markdown_cells(["### PIV Convergence",
                                 "",
                                 "To judge the PIV convergence it is helpful to plot the `running mean`, the `running",
                                 "standard deviation` and the `running relative standard deviation` at various discrete",
                                 "points."]), ]

        if self.notebook.report.is_plane():
            cells.append(code_cells(["_shape = report.velocity.inplane_velocity.shape",
                                     "iy, ix = _shape[0] // 2, _shape[1] // 2",
                                     "",
                                     "fig, axs = plt.subplots(1, 2, figsize=(10, 4))",
                                     "report.velocity.inplane_velocity[:, iy, ix].ssp.running_mean().plot(ax=axs[0])",
                                     "report.velocity.inplane_velocity[:, iy, ix].ssp.running_std().plot(ax=axs[0])",
                                     "report.velocity.inplane_velocity[:, iy, ix].ssp.running_relative_standard_deviation().plot(ax=axs[1])",
                                     "plt.tight_layout()"]))

        return cells
