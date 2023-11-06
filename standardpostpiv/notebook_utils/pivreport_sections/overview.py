markdown_overview_subsection = """Get a first idea of the data:"""

codecells_info = """spp.utils.display_as_badges(
    report.info(), inline=False
)"""


def add_section(parent_section):
    section = parent_section.add_section('Overview/General Information', 'overview')
    section.add_cell(markdown_overview_subsection, 'markdown')
    section.add_cell(codecells_info, 'code')
    return section
