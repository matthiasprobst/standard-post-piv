# Standard Post PIV

This package let's you design and run standardized PIV evaluation on our data. Currently, some prerequisite apply:

- data is stored in HDF5 files
- datasets are labeled with the attribute "standard_name"

To convert PIV results into HDF5 files adhering to the naming convention, use the
[pvi2hdf package](https://gitlab.kit.edu/kit/its/academics/piv/piv2hdf).

## Quickstart

### Installation:

```bash
git clone https://github.com/matthiasprobst/standard-post-piv
cd standardpostpiv
pip install .
```

### Run a standard pre-defined report (basic 2D2C):

```python
import standardpostpiv as spp

report = spp.get_basic_2D2C_report('piv_test_data.hdf')
filenames = report.create(
    notebook_filename='piv_test_data_evaluation.ipynb',
    execute_notebook=True,
    overwrite=True,
    inplace=True,
    to_html=True,
)

# you now got a jupyter notebook `piv_test_data_evaluation.ipynb` and
# an HTML file `piv_test_data_evaluation.html`

# You may let python open the HTML report in web browser:
import webbrowser

webbrowser.open_new(filenames['html'])
```

### Build your own report:

```python
from .notebook import PIVReportNotebook
from .notebook_utils.pivreport_sections import imports, statistics, pdfs, \
    displacement, monitor


report = PIVReportNotebook('piv_test_data.hdf')

report.add_section(imports.section, level=2)
report.add_section(statistics.section_with_badge, level=2)
report.add_section(pdfs.section, level=2)
report.add_section(displacement.main_section, level=2)
report.add_section(displacement.section_mean_displacement, level=3)
report.add_section(displacement.section_instantaneous_velocity, level=3)
report.add_section(monitor.points(), level=2)
report.add_section(monitor.convergence(), level=3)
report.add_section(monitor.line(None), level=3)
```