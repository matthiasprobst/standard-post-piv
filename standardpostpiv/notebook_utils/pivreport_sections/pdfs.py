from ..cells import markdown_cells, code_cells

cells = []
cells.append(markdown_cells("""Find out what the PIV method is, the final window size, etc.:"""))
cells.append(code_cells("""from standardpostpiv.utils import apply_mask"""))

cells.append(code_cells("""dx = apply_mask(res.x_displacement[()],
                res.piv_flags[()],
                2)
dy = apply_mask(res.y_displacement[()],
                res.piv_flags[()],
                2)"""))

cells.append(code_cells("""bins_per_pixel = 10"""))

cells.append(code_cells("""dx_subpx = dx[0,:,:]-dx[0,:,:].astype(int)
dy_subpx = dy[0,:,:]-dy[0,:,:].astype(int)

dx_subpx = dx_subpx.where(dx_subpx<0.5, dx_subpx-1).where(dx_subpx>-0.5, dx_subpx+1)
dx_subpx.attrs['standard_name'] = 'x_sub_pixel_displacement'
dy_subpx = dy_subpx.where(dy_subpx<0.5, dy_subpx-1).where(dy_subpx>-0.5, dy_subpx+1)
dy_subpx.attrs['standard_name'] = 'y_sub_pixel_displacement'"""))

cells.append(code_cells("""fig, axes = stdplt.subplots(2, 1, tight_layout=True)
fig.suptitle('Displacement:')
_ = dx.plot.hist(binwidth=1/bins_per_pixel, density=True, ax=axes[0])  # 10 bins per pixel
_ = dy.plot.hist(binwidth=1/bins_per_pixel, density=True, ax=axes[1])  # 10 bins per pixel
# axes[0].plot_normal_distribution(dx, n=100)
# axes[1].plot_normal_distribution(dy, n=100)
axes[0].set_xlim([-7.5, 7.5])
axes[1].set_xlim([0, 17.5])
stdplt.show()

fig, axes = stdplt.subplots(2, 1, tight_layout=True)
fig.suptitle('Sub-pixel displacement:')
_ = dx_subpx.plot.hist(binwidth=1/bins_per_pixel, ax=axes[0])
_ = dy_subpx.plot.hist(binwidth=1/bins_per_pixel, ax=axes[1])
stdplt.show()"""))

cells.append(code_cells("""stdplt.piv_scatter(res.x_displacement[...],
                   res.y_displacement[...],
                   flags=res.piv_flags[...],
                   fiwsize=res.final_iw_size,
                   alpha=0.1)
_ = stdplt.legend(loc='lower left')"""))

from standardpostpiv.notebook_utils.section import Section

section = Section('PDFs', label='pdfs')

for cell in cells:
    section.add_cell(cell)
