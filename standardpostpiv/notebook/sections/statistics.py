codecell_mean_vel_mag = """vel_mag = report.velocity.mag[()]
    
print(f'Mean velocity magnitude: {vel_mag.mean():f} {vel_mag.units}')"""


def add_section(parent_section):
    section = parent_section.add_section('Statistics', 'statistics')
    section.add_cell(codecell_mean_vel_mag, 'code')
    return section
