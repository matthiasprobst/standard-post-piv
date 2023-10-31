"""standardized plots such as:

- velocity field
- scatter plot of all velocities
- histogram of all velocities
- significance map and 2d graphs

"""
from typing import Union, List, Tuple, Dict

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr


def _add_winsize_to_plot(ax, fiwsize, edgecolor='r'):
    if isinstance(fiwsize, dict):
        fiwsize = (int(fiwsize['x']), int(fiwsize['y']))
    elif isinstance(fiwsize, int):
        fiwsize = (int(fiwsize), int(fiwsize))
    else:
        fiwsize = tuple(map(int, fiwsize))

    if fiwsize is not None:
        if fiwsize[0] is not None and fiwsize[1] is not None:
            rec = plt.Rectangle((-fiwsize[0] / 2, -fiwsize[1] / 2), fiwsize[0], fiwsize[1],
                                edgecolor=edgecolor,
                                facecolor='none')
            ax.axes.add_patch(rec)
        else:
            print('Unable to plot interrogation window size')
    return ax


def xr_piv_scatter(dataset,
                   xname,
                   yname,
                   flagname='piv_flags',
                   fiwsize: Union[int, List[int], Tuple[int], Dict] = None):
    x = dataset[xname]
    y = dataset[yname]
    piv_flags = dataset[flagname]

    fig, ax = plt.subplots()
    ax.scatter(x.where(piv_flags == 1), y.where(piv_flags == 1), marker='o', s=10, color='k', alpha=0.5,
               label='active')
    ax.scatter(x.where(piv_flags & 32), y.where(piv_flags & 33), marker='o', s=10, color='r', alpha=0.5,
               label='active+interpolated')
    ax.scatter(x.where(piv_flags & 64), y.where(piv_flags & 65), marker='o', s=10, color='b', alpha=0.5,
               label='active+replaced')

    if fiwsize:
        _add_winsize_to_plot(ax, fiwsize)

    ax.set_xlabel(f'{x.standard_name} [{x.units}]')
    ax.set_ylabel(f'{y.standard_name} [{y.units}]')

    title_arr_names = [f'{c}={x[c].values[()]:f} [{x[c].units}]' for c in x.coords if x[c].ndim == 0]
    ax.set_title(' '.join(title_arr_names))

    return ax


def piv_scatter(u: Union[np.ndarray, xr.DataArray],
                v: Union[np.ndarray, xr.DataArray],
                fiwsize: Union[int, List[int], Tuple[int], Dict, None] = None,
                flags: xr.DataArray = None,
                color='k',
                edgecolor='r',
                alpha=0.5,
                marker='.',
                s=20,
                indicate_means: bool = True,
                **kwargs):
    """

    Parameters
    ----------
    u: Union[xr.DataArray, np.ndarray]
        x-velocity or x-displacement
    v: Union[xr.DataArray, np.ndarray]
        y-velocity or y-displacement
    fiwsize: Union[int, List[int], Tuple[int], Dict, None]
        final interrogation window size in pixels or real units
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

    show_window_size = fiwsize is not None

    if ax is None:
        fig, ax = plt.subplots()
    if flags is not None:
        ax.scatter(u.where(flags == 1),
                   v.where(flags == 1), marker=marker, s=s, color='k', alpha=0.5,
                   label='active')
        mask32 = flags & 32
        ax.scatter(u.where(mask32).data.ravel(),
                   v.where(mask32).data.ravel(), marker=marker, s=s, color='r', alpha=0.5,
                   label='active+interpolated')
        mask64 = flags & 64
        ax.scatter(u.where(mask64).data.ravel(),
                   v.where(mask64).data.ravel(), marker=marker, s=s, color='b', alpha=0.5,
                   label='active+replaced')
    else:
        ax.scatter(dx, dy, color=color, alpha=alpha, marker=marker, **kwargs)

    umean = u.mean()
    vmean = v.mean()

    if show_window_size:

        if isinstance(fiwsize, dict):
            fiwsize = (int(fiwsize['x']), int(fiwsize['y']))
        elif isinstance(fiwsize, int):
            fiwsize = (int(fiwsize), int(fiwsize))
        else:
            fiwsize = tuple(map(int, fiwsize))

        if fiwsize is not None:
            if fiwsize[0] is not None and fiwsize[1] is not None:
                rec = plt.Rectangle((umean - fiwsize[0] / 2, vmean - fiwsize[1] / 2), fiwsize[0], fiwsize[1],
                                    edgecolor=edgecolor,
                                    facecolor='none')
                ax.axes.add_patch(rec)
            else:
                print('Unable to plot interrogation window size')

    if indicate_means:
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        plt.hlines(vmean, *xlims, linestyle='--', color='r')
        plt.vlines(umean, *ylims, linestyle='--', color='r')

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


def piv_hist(u, v, ax=None, **kwargs):
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

    if ax is None:
        fig, axs = plt.subplots(2, 1, sharex=True)
    else:
        if not len(ax) == 2:
            raise ValueError('ax must be a list of two axes')
        axs = ax

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
