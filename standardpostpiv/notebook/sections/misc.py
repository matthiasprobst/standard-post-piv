def add_section(parent_section):
    section = parent_section.add_section('Misc', 'misc')
    section.add_cell(["import h5rdmtoolbox as h5tbx",
                      "h5tbx.dump(piv_filename)"], 'code')
    return section
