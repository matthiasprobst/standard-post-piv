from .cells import markdown_cells, code_cells
from .core import NotebookSection


class VelocityPlots(NotebookSection):
    """Title section of the report"""

    def get_cells(self):
        """write the cells"""
        # --- mean velocities ----
        cells = [markdown_cells(['## Velocity Plots', ])]

        if self.notebook.report.velocity.is_snapshot():
            cells.append(markdown_cells('### In-plane velocity'))
            cells.append(code_cells(["report.velocity.inplane_vector.ssp.contourf_and_quiver(every=(2, 2))"]))
            cells.append(code_cells("report.velocity.inplane_velocity.ssp.stats()"))
        else:
            cells.append(markdown_cells('### Mean in-plane velocity'))
            cells.append(code_cells(["report.velocity.inplane_vector.ssp.contourf_and_quiver(every=(2, 2))", ]))
            cells.append(code_cells("report.velocity.inplane_velocity.ssp.stats()"))

        # --- monitor/line plots ---

        # --- piv scatter ---
        cells.append(markdown_cells('### PIV scatter plot'))
        cells.append(code_cells(["from standardpostpiv import standardplots",
                                 "ax = standardplots.piv_scatter(u=report.displacement.inplane_vector.u,",
                                 "                               v=report.displacement.inplane_vector.v,",
                                 "                               fiwsize=report.fiwsize,",
                                 "                               indicate_means=True)",
                                 ]))

        cells.append(markdown_cells('### PIV histogram plot'))
        cells.append(code_cells(["from standardpostpiv import standardplots",
                                 "ax = standardplots.piv_hist(u=report.displacement.inplane_vector.u,",
                                 "                            v=report.displacement.inplane_vector.v,",
                                 "                            color='k', bins=40, density=True)",
                                 ]))

        return cells
# self.add_code_cell([
#     "report.velocity.mean_inplane_velocity.plot.contourf_and_quiver(every=[4, 8], quiver_kwargs={'scale': 200})",
#     "report.velocity.mean_inplane_velocity.stats()"])"""]))
#
#         # --- monitor/line plots ---
#         cells.append(code_cells(["""if report.velocity.is_snapshot():
#     from .sections import monitor
#     monitor.snapshot.plot_along_lines(self,
#                                       x="np.linspace(600, 600, 31)",
#                                       y="np.linspace(300, 900, 31)")
# else:
#     from .sections import monitor
#     monitor.plane.plot_along_lines(self,
#                                    x="np.linspace(600, 600, 31)",
#                                    y="np.linspace(300, 900, 31)")"""]))
#         return cells
