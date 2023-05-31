"""standardized plots such as:

- velocity field
- scatter plot of all velocities
- histogram of all velocities
- significance map and 2d graphs

"""
import h5py
import h5rdmtoolbox as h5tbx
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from typing import Union, List, Tuple


def plot_velocity_field(h5):
    """plot the absolute velocity field including the vectors"""
    if not isinstance(h5, h5py.Group):
        with h5tbx.File(h5) as f:
            return plot_velocity_field(f)

    u = h5.find_one({'standard_name': 'x_velocity'})
    ndim = u.ndim


def piv_scatter(u: Union[np.ndarray, xr.DataArray],
                v: Union[np.ndarray, xr.DataArray],
                fiwsize: Union[int, List[int], Tuple[int]],
                color='k',
                alpha=0.5,
                marker='.',
                indicate_means: bool = True,
                **kwargs):
    """

    Parameters
    ----------
    u: Union[xr.DataArray, np.ndarray]
        x-velocity or x-displacement
    v: Union[xr.DataArray, np.ndarray]
        y-velocity or y-displacement
    fiwsize: Union[int, List[int], Tuple[int]]
        final interrogation area size in pixels or real units
    color: str
        color of the scatter plot
    alpha: float
        alpha value of the scatter plot
    marker: str
        marker of the scatter plot
    kwargs: dict
        additional keyword arguments passed to the scatter plot
    """
    ax = kwargs.pop('ax', None)
    xlabel = kwargs.pop('xlabel', None)
    ylabel = kwargs.pop('ylabel', None)
    aspect = kwargs.pop('aspect', 1)

    u_is_xr = isinstance(u, xr.DataArray)
    v_is_xr = isinstance(v, xr.DataArray)
    if u_is_xr:
        dx = u.values.ravel()
    else:
        dx = u.ravel()
    if v_is_xr:
        dy = v.values.ravel()
    else:
        dy = v.ravel()

    if isinstance(fiwsize, int):
        fiwsize = (fiwsize, fiwsize)

    if ax is None:
        fig, ax = plt.subplots()
    ax.scatter(dx, dy, color=color, alpha=alpha, marker=marker, **kwargs)
    if fiwsize is not None:
        rec = plt.Rectangle((-fiwsize[0] / 2, -fiwsize[1] / 2), fiwsize[0], fiwsize[1], edgecolor='k', facecolor='none')
        ax.axes.add_patch(rec)

    if indicate_means:
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        plt.hlines(u.mean(), *xlims, linestyle='--', color='r')
        plt.vlines(v.mean(), *ylims, linestyle='--', color='r')

    if u_is_xr and xlabel is None:
        if 'standard_name' in u.attrs:
            name = u.attrs['standard_name']
        elif 'long_name' in u.attrs:
            name = u.attrs['long_name']
        else:
            name = u.name
        xlabel = f'{name} / {u.units}'

    if v_is_xr and ylabel is None:
        if 'standard_name' in v.attrs:
            name = v.attrs['standard_name']
        elif 'long_name' in v.attrs:
            name = v.attrs['long_name']
        else:
            name = v.name
        ylabel = f'{name} / {v.units}'

    if xlabel is None:
        xlabel = 'x / ?units?'
    if ylabel is None:
        ylabel = 'y / ?units?'
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.set_aspect(aspect)
    return ax

def piv_hist(u, v, **kwargs):
    xlabel1 = kwargs.pop('xlabel1', None)
    xlabel2 = kwargs.pop('xlabel2', None)

    u_is_xr = isinstance(u, xr.DataArray)
    v_is_xr = isinstance(v, xr.DataArray)
    if u_is_xr:
        dx = u.values.ravel()
    else:
        dx = u.ravel()
    if v_is_xr:
        dy = v.values.ravel()
    else:
        dy = v.ravel()

    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].hist(dx, **kwargs)
    axs[1].hist(dy, **kwargs)

    if u_is_xr and xlabel1 is None:
        if 'standard_name' in u.attrs:
            name = u.attrs['standard_name']
        elif 'long_name' in u.attrs:
            name = u.attrs['long_name']
        else:
            name = u.name
        xlabel1 = f'{name} / {u.units}'

    if v_is_xr and xlabel2 is None:
        if 'standard_name' in v.attrs:
            name = v.attrs['standard_name']
        elif 'long_name' in v.attrs:
            name = v.attrs['long_name']
        else:
            name = v.name
        xlabel2 = f'{name} / {v.units}'

    if xlabel1 is None:
        xlabel1 = 'x / ?units?'
    if xlabel2 is None:
        xlabel2 = 'y / ?units?'
    axs[0].set_xlabel(xlabel1)
    axs[1].set_xlabel(xlabel2)
    axs[0].set_ylabel('p / -')
    axs[1].set_ylabel('p / -')

