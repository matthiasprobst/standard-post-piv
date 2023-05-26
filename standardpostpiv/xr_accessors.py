import xarray as xr


@xr.register_dataset_accessor("every")
class Every:
    """Accessor to slice data array every n-th element"""

    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._center = None

    def __call__(self, factor):
        if isinstance(factor, int):
            slice_dict = {k: slice(None, None, factor) for k in self._obj.dims}
        else:
            slice_dict = {k: slice(None, None, 1) for k in self._obj.dims}
            for k, f in zip(self._obj.dims, factor):
                slice_dict[k] = slice(None, None, f)
        return self._obj.isel(**slice_dict)


@xr.register_dataarray_accessor("every")
class Every:
    """Accessor to slice data array every n-th element"""

    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._center = None

    def __call__(self, factor):
        if isinstance(factor, int):
            slice_dict = {k: slice(None, None, factor) for k in self._obj.dims}
        else:
            slice_dict = {k: slice(None, None, 1) for k in self._obj.dims}
            for k, f in zip(self._obj.dims, factor):
                slice_dict[k] = slice(None, None, f)
        return self._obj.isel(**slice_dict)
