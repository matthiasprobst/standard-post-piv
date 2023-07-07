# Standard Post PIV

This package provides the interface and post-processing tools to work with standardized PIV data stored in HDF5 files.
The PIV files are converted from their original file format using the
package [piv2hdf](https://git.scc.kit.edu/piv/piv2hdf). Meta data is partly standardized using `standard_names`. A list
of standard names can is managed by the package piv-convention [piv-convention]().

## Motivation

The fundamental variables in PIV result data remain consistent regardless of the specific flow problem under
investigation. By adhering to a common standard for data storage, a standardized interface can be established. This
package facilitates this standardized interface and enables automated analysis of the data. Additionally, it offers the
capability to generate an automated report in the form of a Jupyter notebook. Users can further customize and expand
upon this notebook by incorporating their own analyses.

### Installation

```bash
pip install standardpostpiv
```

## Examples

### Accessing velocity data

```python
import standardpostpiv as spp

report = spp.PIVReport('path/to/file.hdf')

# get the x-velocity of the 10th timestep in the second plane:
u_vel = report.velocity.x.sel(time=10, z=2)

# get the magnitude of the velocity at time approx. to 3.12s:
mag_vel = report.velocity.magnitude.sel(time=3.12, method='nearest')
```

### Get scalar PIV variables:

```python
import standardpostpiv as spp

report = spp.PIVReport('path/to/file.hdf')

# get piv flags at time step 0
report.flags.isel(time=0).plot(cmap='binary')

# get mask at time step 0
report.mask.isel(time=0).plot(cmap='binary')
```

### Compute derivatives:

```python

import standardpostpiv as spp

report = spp.PIVReport('path/to/file.hdf')

# compute the derivative of the x-velocity w.r.t. the y-cordinate
dudy = report.velocity.x.sel(time=10, z=2).piv.differentiate('y')
```

### Generate the (jupyter notebook) report:

```python
import standardpostpiv as spp

report = spp.PIVReport('path/to/file.hdf')
report.generate_notebook(excecute=True)
```

