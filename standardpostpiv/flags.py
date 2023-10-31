import numpy as np
import xarray as xr


def apply_mask(da, flag):
    """Apply a mask to a DataArray"""
    if da.dims == flag.dims:
        return da.where(~flag & 2)
    raise ValueError('Dimensions of DataArray and flag do not match')


def eval_flags(flag_data: xr.DataArray, dim='reltime'):
    """Evaluate flags and return a dictionary of DataArrays
    with the number of flags per time step"""
    coord0 = flag_data.coords[dim]
    nt = len(coord0)
    flag_series = {v: xr.DataArray(name='INTERPOLATED',
                                   dims=dim,
                                   data=np.empty(nt).astype(int),
                                   coords={dim: coord0}) for v in
                   flag_data.flag_meaning.values()}

    for i in range(nt):
        nflags = {v: np.sum((flag_data.isel({dim: i}).data & int(k)).astype(bool)) for k, v in
                  flag_data.flag_meaning.items()}
        for k, v in nflags.items():
            flag_series[k][i] = v
    return flag_series
