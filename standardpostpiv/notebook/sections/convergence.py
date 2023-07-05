from .cells import code_cells, markdown_cells
from .core import NotebookSection

markdown_title = """### PIV Convergence

To judge the PIV convergence it is helpful to plot the `running mean`, the `running standard deviation` and the 
`running relative standard deviation` at various discrete<br>
points.<br>"""

code_define_monitors = """# uncomment the following to define the monitor points yourself:
# user_defined_monitor_points = [(y, x) for x, y in zip(spp.utils.find_nearest_indices(report.x[()], (40.3, 140)),
#                                                       spp.utils.find_nearest_indices(report.y[()], (80.0, 60.5)))]
# report.seeding_points = user_defined_monitor_points"""

code_plot_single_plane = """fig, axs = plt.subplots(1, 2, figsize=(14, 4))

report.mask.plot(cmap='binary', ax=axs[0])
for i, pt in enumerate(report.seeding_points):
    axs[0].scatter(report.x[pt[1]], report.y[pt[0]], color='red', marker='+')

for i, pt in enumerate(report.seeding_points):
    report.velocity.inplane_velocity[:, pt[0], pt[1]].piv.running_mean().plot(label=f'{i+1}', ax=axs[1])
    
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


class ConvergenceSection(NotebookSection):

    def get_cells(self):
        if self.notebook.report.is_snapshot():
            return []

        cells = [markdown_cells(markdown_title),
                 code_cells(code_define_monitors),]

        if self.notebook.report.is_plane():
            cells.append(code_cells(code_plot_single_plane))

        else:
            cells.append(code_cells(code_plot_multi_plane))

        # cells.append(code_cells(["plt.imshow(report.mask, cmap='binary')",
        #                          "for i, pt in enumerate(report.seeding_points):",
        #                          "    plt.scatter(pt[1], pt[0], color='red', marker='o')",
        #                          "    plt.text(pt[1]+1, pt[0]+1, f'{i+1}', color='r')",
        #                          "plt.show()"]))
        #
        # if self.notebook.report.is_plane():
        #     cells.append(code_cells(["for i, pt in enumerate(report.seeding_points):",
        #                              "    report.velocity.inplane_velocity[:, pt[0],"
        #                              " pt[1]].piv.running_mean().plot(label=f'{i+1}')",
        #                              "_ = plt.gca().set_title('Running mean of monitor points')",
        #                              "plt.legend()"]))
        # elif self.notebook.report.is_mplane():
        #     for iz in range(self.notebook.report.nz):
        #         cells.append(code_cells(["for i, pt in enumerate(report.seeding_points):",
        #                                  f"    report.velocity.inplane_velocity[{iz}, :, pt[0],"
        #                                  f" pt[1]].piv.running_mean().plot(label=f'{i + 1}')",
        #                                  f"_ = plt.gca().set_title('Running mean of monitor points for\nplane {iz + 1}')",
        #                                  "plt.legend()"]))

        return cells
