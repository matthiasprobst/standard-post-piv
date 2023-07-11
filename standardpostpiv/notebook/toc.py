import numpy as np

USECHAPTER = 1  # level 1 is considered chapter and will not get a number

STYLE_HTML = """<style>
.dropdown-toc summary {
  list-style-type: none;
  outline: none;
  cursor: pointer;
}
.dropdown-toc ul {
  padding-left: 20px;
}
.dropdown-toc ul ul {
  padding-left: 40px;
}
</style>

"""


def generate_toc_html(section_data):
    def generate_table_of_contents(section_data):
        toc = "<ul>"
        current_indentation = section_data[0][0]
        level_counts = np.zeros(10, dtype=int)

        for level, title, label in section_data:

            use_level = level - USECHAPTER
            if use_level > 0:
                level_counts[use_level - 1] += 1
                level_counts[use_level:] = 0
                section_number_str = '.'.join([str(_level) for _level in level_counts[:use_level]])
                new_title = f'{section_number_str}. {title}'
                title = new_title

            if level > current_indentation:
                if label:
                    # open a new list with a link
                    toc += "<ul>" + f'<li><a href="#piv-{label}">{title}</a></li>'
                else:
                    # open a new list without a link
                    toc += "<ul>" + f"<li>{title}</li>"

            elif level == current_indentation:
                if label:
                    #
                    toc += f'<li><a href="#piv-{label}">{title}</a></li>'
                else:
                    toc += f"</li>{title}<li>"
            else:
                # close the current list and open a new list
                toc += "</ul>" * (current_indentation - level + 1)
                if label:
                    # open a new list with a link
                    toc += "<ul>" + f'<li><a href="#piv-{label}">{title}</a></li>'
                else:
                    # open a new list without a link
                    toc += "<ul>" + f"<li>{title}</li>"

            current_indentation = level
        toc += "</ul>" * current_indentation
        return toc

    TOC_HTML = STYLE_HTML + f"""<div class="dropdown-toc">
      <details open>
        <summary>Table of Contents</summary>
        <div>
          {generate_table_of_contents(section_data)}
        </div>
      </details>
    </div>"""
    return TOC_HTML
