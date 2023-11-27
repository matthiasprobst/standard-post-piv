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

### Build a standard evaluation report:

```python
import standardpostpiv as spp

report = spp.get_basic_2D2C_report('piv_test_data.hdf')
ntb = report.create(
    notebook_filename='piv_test_data_evaluation.ipynb',
    execute_notebook=True,
    overwrite=True,
    inplace=True,
    to_html=True,
)

# you now got a jupyter notebook `piv_test_data_evaluation.ipynb` and
# a html file `piv_test_data_evaluation.html`
```