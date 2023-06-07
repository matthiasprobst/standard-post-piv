import numpy as np
import xarray as xr

# noinspection PyUnresolvedReferences
from . import plotting, statistics
from . import report

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


@xr.register_dataset_accessor("ssp")
class ContourfAndQuiverAccessor:
    """Accessor that prints statistics of data variables"""

    def __init__(self, xarray_obj):
        """Initialize the accessor"""
        self._obj = xarray_obj

    def interactive_contourf_and_quiver(self,
                                        contourf_variable: str = 'mag',
                                        x='x', y='y',
                                        u='u', v='v', every=2,
                                        contourf_kwargs=None,
                                        quiver_kwargs=None,
                                        ax=None,
                                        initial_flag: int = None):
        flag_values = np.unique(self._obj['flags'].values)

        flag_meaning = self._obj['flags'].attrs['flag_meaning']

        mask_names = ['_'.join(report.Report.explain_flags(mark_flag, flag_meaning)) for mark_flag in flag_values]

        plotting.simple_dropdown_plot([f'{flag}-{mask_name}'  for flag, mask_name in zip(flag_values, mask_names)],
                                      plotting.contourf_and_quiver,
                                      initial_flag,
                                      self._obj,
                                      contourf_variable,
                                      x, y,
                                      u, v,
                                      every,
                                      contourf_kwargs,
                                      quiver_kwargs,
                                      ax=ax)

    def contourf_and_quiver(self,
                            contourf_variable: str = 'mag',
                            x='x', y='y',
                            u='u', v='v', every=2,
                            contourf_kwargs=None,
                            quiver_kwargs=None,
                            ax=None,
                            mark_flag: int = None):
        """plot contourf and quiver in one plot"""
        return plotting.contourf_and_quiver(self._obj,
                                            contourf_variable,
                                            x, y,
                                            u, v,
                                            every,
                                            contourf_kwargs,
                                            quiver_kwargs,
                                            ax=ax,
                                            mark_flag=mark_flag)

    def stats(self, ):
        return statistics.stats(self._obj)


@xr.register_dataarray_accessor("ssp")
class StatsAccessor:
    """Accessor that prints statistics of data variables"""

    def __init__(self, xarray_obj):
        """Initialize the accessor"""
        self._obj = xarray_obj

    def stats(self, *args, **kwargs):
        return statistics.stats(self._obj)

    def running_mean(self, *args, **kwargs):
        attrs = self._obj.attrs
        attrs.update({'standard_name': f'running_mean_of_{self._obj.standard_name}'})
        return xr.DataArray(name=f'running_mean_of_{self._obj.name}',
                            data=statistics.running_mean(self._obj.values),
                            dims=self._obj.dims,
                            coords=self._obj.coords,
                            attrs=attrs)

    def running_strd(self, ddof: int = 2):
        attrs = self._obj.attrs
        attrs.update({'standard_name': f'running_standard_deviation_of_{self._obj.standard_name}'})
        return xr.DataArray(name=f'running_std_of_{self._obj.name}',
                            data=statistics.running_std(self._obj.values, axis=0, ddof=ddof),
                            dims=self._obj.dims,
                            coords=self._obj.coords,
                            attrs=attrs)

    def running_relative_standard_deviation(self, ddof: int = 2):
        attrs = self._obj.attrs
        attrs.update(
            {'standard_name': f'running_relative_standard_deviation_of_{self._obj.standard_name}',
             'units': ''}
        )
        return xr.DataArray(name=f'running_rstd_of_{self._obj.name}',
                            data=statistics.running_relative_standard_deviation(self._obj.values, axis=0, ddof=ddof),
                            dims=self._obj.dims,
                            coords=self._obj.coords,
                            attrs=attrs)
