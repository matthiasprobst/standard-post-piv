import locale
from typing import Union, List, Tuple, Dict

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from scipy.stats import norm

from .utils import build_vector
import itertools

golden_ratio = (np.sqrt(5.0) - 1.0) / 2.0  # Aesthetic ratio (you could change this)
golden_mean = 9 / 16  # This is suited for widescreen ppt

LATEX_TEXTWIDTH_MM = 160  # mm
LATEX_TEXTWIDTH_IN = LATEX_TEXTWIDTH_MM / 25.4  # in

markers = itertools.cycle(('+', '.', 'o', '*', 's', '<', '>', '^'))
gray_colors = itertools.cycle([str(i) for i in np.linspace(0.0, 0.5, 4)])



def goldenfigsize(scale, hscale=1, gr=True) -> List[float]:
    """Set figure size to golden ratio

    Parameter
    ---------
    scale : float
        Scale factor for the figure size
    hscale : float
        Scale factor for the height of the figure
    gr : bool
        If True, use golden ratio, else use golden mean

    Returns
    -------
    fig_size : list[float]
        Figure size in inches
    """
    fig_width_inch = mpl.rcParams.get('figure.figsize')[0]
    if gr:
        ratio = golden_ratio  # Aesthetic ratio (you could change this)
    else:
        ratio = golden_mean  # This is suited for widescreen ppt
    fig_width = fig_width_inch * scale  # width in inches
    fig_height = fig_width * ratio * hscale  # height in inches
    fig_size = [fig_width, fig_height]
    return fig_size


def get_normal_distribution_from_data(data, n=100, step=None) -> Tuple[np.ndarray, np.ndarray]:
    """Get normal distribution from data. Returns x and y values"""
    if step is None and n is None:
        raise ValueError("Either step or n must be specified")
    if step is None:
        step = (np.nanmax(data) - np.nanmin(data)) / n
    x_axis = np.arange(np.nanmin(data), np.nanmax(data), step)
    return x_axis, norm.pdf(x_axis, data.mean(), data.std())


def figure(*args, **kwargs):
    scale = kwargs.pop('scale', 1)
    figsize = kwargs.pop('figsize', goldenfigsize(scale))
    f = plt.figure(*args, figsize=figsize, **kwargs)

    class _add_subplot:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            kwargs['projection'] = kwargs.get('projection', 'stdaxes')
            return self.func(*args, **kwargs)

    orig_func = f.add_subplot
    f.add_subplot = _add_subplot(orig_func)
    return f


def subplots(*args, **kwargs):
    """Create a figure with subplots using the standard axes"""
    subplot_kw = kwargs.pop('subplot_kw', {})
    subplot_kw['projection'] = 'stdaxes'
    kwargs['subplot_kw'] = subplot_kw
    kwargs['figsize'] = kwargs.get('figsize', goldenfigsize(kwargs.pop('scale', 1)))
    return plt.subplots(*args, **kwargs)


class StandardAxes(plt.Axes):
    """Standard axes class for plotting"""

    name = 'stdaxes'

    def __enter__(self,
                  style='gray',
                  keep_latex: bool = False,
                  de: bool = False):
        if de:
            locale.setlocale(locale.LC_ALL, 'de_DE')
            # self.curr_rc_params["axes.formatter.use_locale"] = True
        else:
            locale.setlocale(locale.LC_ALL, 'en_US')
        self.curr_rc_params = mpl.rcParams.copy()
        if style == 'gray':
            # Define a grayscale color cycle
            _gray_scales = [str(i) for i in np.linspace(0.0, 0.5, 4)]
            _linestyles = ['-', '--', '-.', ':']

            grayscale_cycle = plt.cycler('color', [g for _ in _linestyles for g in _gray_scales])
            linestyle_cycle = plt.cycler('linestyle', [l for l in _linestyles for _ in _gray_scales])
            self.set_prop_cycle(grayscale_cycle + linestyle_cycle)

    def __exit__(self, *args, **kwargs):
        plt.rcParams.update(self.curr_rc_params)

    def hist(self, data, binwidth=None, **kwargs):
        color = kwargs.pop('color', 'lightgray')
        edgecolor = kwargs.pop('edgecolor', 'k')
        bins = kwargs.pop('bins', None)
        if bins is None:
            if binwidth is None:
                raise ValueError('Either binwidth or bins must be provided')
            bins = np.arange(np.nanmin(data), np.nanmax(data) + binwidth, binwidth)
        super().hist(data, bins=bins, color=color, edgecolor=edgecolor, **kwargs)
        if isinstance(data, xr.DataArray):
            xlabel = data.attrs.get('standard_name', data.attrs.get('long_name', None))
            if xlabel is None:
                xlabel = data.name
            self.set_xlabel(xlabel)
        if kwargs.get('density'):
            self.set_ylabel('density')
        else:
            self.set_ylabel('count')
        return self

    def plot_normal_distribution(self, data, n=None, step=None, **kwargs):
        """Plot a normal distribution using the mean and standard deviation of the data"""
        with self:
            self.plot(*get_normal_distribution_from_data(data, n, step), **kwargs)
            if isinstance(data, xr.DataArray):
                xlabel = data.attrs.get('standard_name', data.attrs.get('long_name', None))
                if xlabel is None:
                    xlabel = data.name
                self.set_xlabel(xlabel)
            return self

    def pivquiver(self, u, v, w=None, every=1, **kwargs):
        """Plot a quiver plot of the given vector field"""
        if not u.ndim == 2:
            raise ValueError('u must be 2D')
        if not v.ndim == 2:
            raise ValueError('v must be 2D')
        if w is not None and not w.ndim == 2:
            raise ValueError('w must be 2D')
        if isinstance(every, int):
            every = (every, every)
        data = {'u': u, 'v': v}
        if w is not None:
            data['w'] = w
        disp = build_vector(**{k: v[::every[1], ::every[0]] for k, v in data.items()})
        disp.plot.quiver(x='x', y='y', u='u', v='v', ax=self, **kwargs)

    def pivstreamplot(self, u, v, w=None, **kwargs):
        if not u.ndim == 2:
            raise ValueError('u must be 2D')
        if not v.ndim == 2:
            raise ValueError('v must be 2D')
        if w is not None and not w.ndim == 2:
            raise ValueError('w must be 2D')
        data = {'u': u, 'v': v}
        if w is not None:
            data['w'] = w
        disp = build_vector(**{k: v[()] for k, v in data.items()})
        disp.plot.streamplot(x='x', y='y', u='u', v='v', **kwargs)


tight_layout = plt.tight_layout
legend = plt.legend

import matplotlib.projections as proj

proj.register_projection(StandardAxes)


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
        fig, ax = subplots(1, 1, tight_layout=True)
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
