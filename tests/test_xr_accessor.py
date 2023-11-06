import xarray as xr

# noinspection PyUnresolvedReferences
import standardpostpiv

da = xr.DataArray(data=[1, 2, 3, 4, 5, 6], dims='reltime', attrs=dict(standard_name='x_velocity'))

assert da.attrs['standard_name'] == 'x_velocity'
da_mean = da.stdpiv.mean('reltime')
assert da_mean.attrs['standard_name'] == 'arithmetic_mean_of_x_velocity'
da_mean = da.stdpiv.mean('reltime')
assert da_mean.attrs['standard_name'] == 'arithmetic_mean_of_x_velocity'

da_dmean = da.stdpiv.compute_developing_mean('reltime')
assert da_dmean.attrs['standard_name'] == 'developing_mean_of_x_velocity'

da_mean_of_dmean = da_dmean.stdpiv.mean('reltime')
assert da_mean_of_dmean.attrs['standard_name'] == 'arithmetic_mean_of_developing_mean_of_x_velocity'
