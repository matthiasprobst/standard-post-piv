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
            cells.append(
                code_cells(["report.velocity.inplane_vector.ssp.interactive_contourf_and_quiver(every=(2, 2))"]))
            cells.append(code_cells("report.velocity.inplane_velocity.ssp.stats()"))
        else:
            cells.append(markdown_cells('### Mean in-plane velocity'))
            cells.append(
                code_cells(["report.velocity.inplane_vector.sel(time=0).ssp.interactive_contourf_and_quiver(every=(2, 2))", ]))
            cells.append(code_cells("report.velocity.inplane_velocity.ssp.stats()"))

        # --- monitor/line plots ---

        # --- piv scatter ---
        cells.append(markdown_cells('### PIV scatter plot'))
        cells.append(code_cells(["scatter_ax = report.displacement.inplane_vector[['u', 'v']].sel("
                                 "time=0).piv.scatter(fiwsize=report.fiwsize)"]))
        # cells.append(code_cells(["from standardpostpiv import standardplots",
        #                          "ax = standardplots.piv_scatter(u=report.displacement.inplane_vector.u,",
        #                          "                               v=report.displacement.inplane_vector.v,",
        #                          "                               fiwsize=report.fiwsize,",
        #                          "                               indicate_means=True)",
        #                          ]))

        cells.append(markdown_cells('### PIV histogram plot'))
        cells.append(code_cells(["from standardpostpiv import standardplots",
                                 "ax = standardplots.piv_hist(u=report.displacement.inplane_vector.u,",
                                 "                            v=report.displacement.inplane_vector.v,",
                                 "                            color='k', bins=40, density=True)",
                                 ]))

        return cells
