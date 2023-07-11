codecell_mean_vel_mag = """vel_mag = report.velocity.mag[()]
    
print(f'Mean velocity magnitude: {vel_mag.mean():f} {vel_mag.units}')"""

codecell_vdp = """spp.utils.display_as_badges({'vdp': f'{report.flags[()].piv.compute_vdp()*100:.2f}%'}, color_info={'vdp': 'orange'})"""


def add_section(parent_section):
    section = parent_section.add_section('Statistics', 'statistics')
    section.add_cell('**Mean velocity magnitude:**', 'markdown')
    section.add_cell(codecell_mean_vel_mag, 'code')
    section.add_cell('**Velocity detection probability (VDP):**', 'markdown')
    section.add_cell(codecell_vdp, 'code')
    return section
