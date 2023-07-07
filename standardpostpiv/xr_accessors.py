import re
import warnings

import h5rdmtoolbox as h5tbx
import numpy as np
# noinspection PyUnresolvedReferences
import pint_xarray
import xarray as xr
from typing import Union

from standardpostpiv import get_config
# noinspection PyUnresolvedReferences
from . import plotting, statistics, standardplots
from .flags import explain_flags


def calc_dwdz(dudx, dvdy):
    """
    Calculates dwdz from solving continuity equation:
        div(v) = 0
    This is only valid for incompressible flows (=0 on right side of equation)!

    Parameters
    ----------
    dudx : `array_like`
    dvdy : `array_like`

    Returns
    -------
    dwdz : `array_like`
    """
    return -dudx[:] - dvdy[:]


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


@xr.register_dataarray_accessor("piv")
class PivDataArrayAccessor:
    """Xarray accessor for PIV data arrays"""

    def __init__(self, xarray_obj):
        """Initialize the accessor"""
        self._obj = xarray_obj

    def differentiate(self, coord, edge_order=1, **kwargs) -> xr.DataArray:
        """Call xr.DataArray.differentiate and add standard_name attribute to the resulting DataArray."""
        this_sn = self._obj.standard_name
        this_units = self._obj.units
        other_sn = self._obj[coord].standard_name
        other_units = self._obj[coord].units

        ureg = h5tbx.get_ureg()

        q1 = (1 * ureg.Unit(this_units)).to_base_units()
        q2 = (1 * ureg.Unit(other_units)).to_base_units()

        corr_factor = q1.magnitude / q2.magnitude

        dobj = self._obj.differentiate(coord, edge_order, **kwargs)
        dobj.attrs['standard_name'] = f'derivative_of_{this_sn}_wrt_{other_sn}'
        dobj.attrs['units'] = f'{q1.units / q2.units}'
        dobj.name = f'd{self._obj.name}d{coord}'
        return dobj * corr_factor

    @property
    def can_be_converted_to_moving_frame(self) -> bool:
        """Returns True if the data array can be converted to a moving frame of reference.
        For this to be possible, one coordinate with standard name containing
        moving_frame must be present.

        Returns
        -------
        bool
            True if the data array can be converted to a moving frame of reference.
        """
        # first identify the coordinate with the moving frame standard name:
        for k, moving_frame in self._obj.coords.items():
            # use regex to find the moving_frame in string:
            if re.search('moving_frame', moving_frame.attrs['standard_name']):
                # found it, return True:
                return True
        return False

    def in_moving_frame(self, enable=True) -> xr.DataArray:
        """Returns the data array in the moving frame of reference.
        For this to be possible, one coordinate with standard name containing
        moving_frame must be present.
        The resulting values will be computed as:
        new_values = values - values_of_moving_frame

        The standard name is appended with '_in_moving_frame'.
        The coordinate with the moving frame standard name is dropped.

        Parameters
        ----------
        enable: bool
            If True, the data array is returned in the moving frame of reference.

        Returns
        -------
        new_ds: xr.DataArray
            Data array in moving frame of reference

        Raises
        ------
        ValueError
            If no coordinate with standard name containing 'moving_frame' is found.
        """
        if not enable:
            return self._obj
        # first identify the coordinate with the moving frame standard name:
        for k, moving_frame in self._obj.coords.items():
            # use regex to find the moving_frame in string:
            if re.search('moving_frame', moving_frame.attrs['standard_name']):
                # found it, return the relative values:
                new_ds = (self._obj.pint.quantify() - moving_frame.pint.quantify()).pint.dequantify()
                new_ds.attrs['standard_name'] = self._obj.attrs['standard_name'] + '_in_moving_frame'
                new_ds.attrs['ANCILLARY_DATASETS'].remove(k)
                return new_ds.drop(k)
        raise ValueError('No coordinate with "moving_frame" found.')

    def contour(self, flag=1, **kwargs) -> None:
        """Call contourf on the data array"""
        flag_ds = None
        for k, v in self._obj.coords.items():
            if v.attrs['standard_name'] == 'piv_flags':
                flag_ds = v
                break

        kwargs['cmap'] = kwargs.pop('cmap', get_config('cmap'))

        if flag_ds is None:
            warnings.warn('No flags found for this dataset!')
            return self._obj.plot.contour(**kwargs)
        return self._obj.where(flag_ds & flag).plot.contour(**kwargs)

    def contourf(self, flag=1, **kwargs) -> None:
        """Call contourf on the data array"""
        flag_ds = self.flags

        kwargs['cmap'] = kwargs.pop('cmap', get_config('cmap'))

        if flag_ds is None:
            warnings.warn('No flags found for this dataset!')
            return self._obj.plot.contourf(**kwargs)
        return self._obj.where(flag_ds & flag).plot.contourf(**kwargs)

    @property
    def flags(self):
        for k, v in self._obj.coords.items():
            if v.attrs['standard_name'] == 'piv_flags':
                return v
        return None

    def flag_where(self, flag):
        return self._obj.where(self.flags & flag)

    @property
    def active(self):
        return self.flag_where(1)

    def running_mean(self, *args, **kwargs):
        attrs = self._obj.attrs
        attrs.update({'standard_name': f'running_mean_of_{self._obj.standard_name}'})
        return xr.DataArray(name=f'running_mean_of_{self._obj.name}',
                            data=statistics.running_mean(self._obj.values),
                            dims=self._obj.dims,
                            coords=self._obj.coords,
                            attrs=attrs)

    @property
    def mask(self, flag: int = 2):
        """Returns the mask as boolean array by bitwise comparison of the flag dataset with the provided flag"""
        mask = self._obj.piv_flags & flag == 0
        mask.attrs['standard_name'] = 'piv_mask'
        mask.attrs['long_name'] = 'PIV mask'
        mask['name'] = 'mask'
        return mask.drop(mask.attrs.pop('ANCILLARY_DATASET', {}))


@xr.register_dataset_accessor("piv")
class PivDatasetAccessor:

    def __init__(self, xarray_obj):
        """Initialize the accessor"""
        self._obj = xarray_obj

    @property
    def flags(self):
        for k, v in self._obj.coords.items():
            if v.attrs['standard_name'] == 'piv_flags':
                return v
        return None

    def flag_where(self, flag):
        return self._obj.where(self.flags & flag)

    @property
    def active(self):
        return self.flag_where(1)

    def scatter(self, x: str = None, y: str = None, fiwsize=None):
        """Plot scatter data. Therefore dataset must have two data variables.

        Parameters
        ----------
        x : str, optional
            Name of the x data variable, by default None. If None, the
            dataset must have exactly two data variables and the first one
            is used.
        y : str, optional
            Name of the y data variable, by default None. If None, the
            dataset must have exactly two data variables and the second one
            is used.
        fiwsize : tuple, optional
            Figure size, by default None. If not None, the window size is
            plotted.

        Returns
        -------
        ax: matplotlib.axes.Axes
        """
        if x is None and y is None:
            data_vars = list(self._obj.data_vars)
            if len(data_vars) != 2:
                raise ValueError('Only two data variables allowed')
            x = data_vars[0]
            y = data_vars[1]
        elif x is not None and y is not None:
            pass
        else:
            raise ValueError('Either both or none of x and y must be given')
        return standardplots.xr_piv_scatter(self._obj, xname=x, yname=y, fiwsize=fiwsize)

    def _get_by_standard_name(self, standard_name, counts: Union[int, None]):
        """if counts is not matched, then an error is raised"""
        res = []
        for da in self._obj.coords:
            if self._obj[da].standard_name == standard_name:
                res.append(da)
        if counts:
            if len(res) != counts:
                raise ValueError(
                    f'Found {len(res)} variables with standard name {standard_name}, but expected {counts}')
        return res


@xr.register_dataset_accessor("pivplot")
class PivPlotAccessor:
    """Accessor that plots PIV data"""

    def __init__(self, xarray_obj):
        """Initialize the accessor"""
        self._obj = xarray_obj

    def contour(self, flag=1, **kwargs) -> None:
        """Call contourf on the dataset. Expected is to have two items, 'flags' and the data variable."""
        data_vars = list(self._obj.data_vars)
        data_vars.remove('flags')
        if len(data_vars) != 1:
            raise ValueError('Only one data variable allowed')
        data = self._obj.where(self._obj['flags'].values & flag)
        return data[data_vars[0]].plot.contour(**kwargs)

    def contourf(self, flag=1, **kwargs) -> None:
        """Call contourf on the dataset. Expected is to have two items, 'flags' and the data variable."""
        print(kwargs['cmap'])
        data_vars = list(self._obj.data_vars)
        data_vars.remove('flags')
        if len(data_vars) != 1:
            raise ValueError('Only one data variable allowed')
        data = self._obj.where(self._obj['flags'].values & flag)
        return data[data_vars[0]].plot.contourf(**kwargs)

    # def icontourf(self):
    #     """interactive contourf allowing to select flags"""
    #     flag_values = np.unique(self._obj['flags'].values)
    #
    #     flag_meaning = self._obj['flags'].attrs['flag_meaning']
    #
    #     mask_names = ['_'.join(explain_flags(mark_flag, flag_meaning)) for mark_flag in flag_values]
    #
    #     plotting.simple_dropdown_plot([f'{flag}-{mask_name}' for flag, mask_name in zip(flag_values, mask_names)],
    #                                   plotting.contourf_and_quiver,
    #                                   initial_flag,
    #                                   self._obj,
    #                                   contourf_variable,
    #                                   x, y,
    #                                   u, v,
    #                                   every,
    #                                   contourf_kwargs,
    #                                   quiver_kwargs,
    #                                   ax=ax)


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

        mask_names = ['_'.join(explain_flags(mark_flag, flag_meaning)) for mark_flag in flag_values]

        plotting.simple_dropdown_plot([f'{flag}-{mask_name}' for flag, mask_name in zip(flag_values, mask_names)],
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

    def running_std(self, ddof: int = 2):
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
