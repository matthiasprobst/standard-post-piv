import xarray as xr

from .statistics import developing_relative_standard_deviation, developing_mean, developing_std


@xr.register_dataarray_accessor('stdpiv')
class StdPIVDAAccessor:
    def __init__(self, obj):
        self._obj = obj

    def apply_mask(self, mask, value):
        """Apply a mask to a DataArray"""
        assert self._obj.ndim == mask.ndim
        assert self._obj.dims == mask.dims
        return self._obj.where(~mask & value)

    def mean(self, dim=None, **kwargs):
        """wrapper for xarray.DataArray.mean() that
         generates new standard_name"""
        new_obj = self._obj.mean(dim=dim, **kwargs)
        sn = self._obj.attrs.get('standard_name', None)
        if sn:
            new_obj.attrs['standard_name'] = f'arithmetic_mean_of_{sn}'
        return new_obj

    def compute_developing_mean(self, dim):
        """Compute the running mean along a dimension"""
        dim_axis = 0
        for d in self._obj.dims:
            if dim == d:
                break
            dim_axis += 1
        dims = self._obj.dims

        attrs = self._obj.attrs
        attrs.update({'standard_name': f'developing_mean_of_{self._obj.standard_name}'})
        return xr.DataArray(name=f'developing_mean_of_{self._obj.name}',
                            data=developing_mean(self._obj.values, dim_axis),
                            dims=dims,
                            coords={d: self._obj.coords[d] for d in dims},
                            attrs=attrs)

    def compute_developing_std(self, dim, ddof):
        """Compute the running standard deviation along a dimension"""
        dim_axis = 0
        for d in self._obj.dims:
            if dim == d:
                break
            dim_axis += 1
        dims = self._obj.dims

        attrs = self._obj.attrs
        attrs.update({'standard_name': f'developing_mean_of_{self._obj.standard_name}'})
        return xr.DataArray(name=f'developing_mean_of_{self._obj.name}',
                            data=developing_std(self._obj.values, dim_axis, ddof),
                            dims=dims,
                            coords={d: self._obj.coords[d] for d in dims},
                            attrs=attrs)

    def compute_developing_relative_standard_deviation(self, dim, ddof=0) -> xr.DataArray:
        """Compute the running relative standard deviation using the running
        mean as normalization. Useful to judge the convergence of PIV

        Parameters
        ----------
        dim : str
            dimension along which to compute the running relative standard deviation
        ddof : int
            degrees of freedom for the standard deviation

        Returns
        -------
        xr.DataArray
            running relative standard deviation
        """
        dim_axis = 0
        for d in self._obj.dims:
            if dim == d:
                break
            dim_axis += 1
        dims = self._obj.dims
        return xr.DataArray(developing_relative_standard_deviation(self._obj.to_numpy(), axis=dim_axis, ddof=ddof),
                            dims=dims,
                            coords={d: self._obj.coords[d] for d in dims},
                            attrs={'standard_name': f'developing_relative_standard_deviation_of_{self._obj.name}',
                                   'units': ''})


@xr.register_dataset_accessor('stdpiv')
class StdPIVDSAccessor:
    def __init__(self, obj):
        self._obj = obj

    def compute_magnitude(self, data_vars=None):
        """helper function to compute the magnitude of the velocity vector"""
        if vars is not None:
            data_vars = self._obj.data_vars
        from .utils import compute_magnitude
        return compute_magnitude(*[self._obj[dv] for dv in data_vars])
