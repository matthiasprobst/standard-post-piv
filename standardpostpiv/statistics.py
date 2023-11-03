"""statistics module"""
import numpy as np
import pandas as pd
import xarray as xr
from functools import wraps
from scipy.stats import anderson, shapiro, normaltest
from typing import Union


def stats(target):
    """compute stats for the target. dataset including flags is ignored"""
    if isinstance(target, xr.DataArray):
        return pd.DataFrame(
            {
                target.name: {
                    'min': target.min().values,
                    'max': target.max().values,
                    'mean': target.mean().values,
                    'std': target.std().values
                }
            }
        )
    elif isinstance(target, xr.Dataset):
        df = [stats(v) for k, v in target.items() if 'flags' not in k]
        return pd.concat(df, axis=1)
    else:
        raise NotImplementedError(f'stats is not implemented for {type(target)}')


def next_std(sum_of_x, sum_of_x_squared, n, xnew, ddof):
    """computes the standard deviation after adding one more data point to an array.
    Avoids computing the standard deviation from the beginning of the array by using
    math, yeah :-)

    Parameters
    ----------
    sum_of_x : `float`
        The sum of the array without the new data point
    sum_of_x_squared : `float`
        The sum of the squared array without the new data point
    n : `int`
        Number of data points without the new data point
    xnew : `float`
        The new data point
    ddof : `int`, optional=0
        Means Delta Degrees of Freedom. See doc of numpy.std().
    """
    sum_of_x = sum_of_x + xnew
    sum_of_x_squared = sum_of_x_squared + xnew ** 2
    n = n + 1  # update n
    return sum_of_x, sum_of_x_squared, np.sqrt(1 / (n - ddof) * (sum_of_x_squared - 1 / n * (sum_of_x) ** 2))


def next_mean(mu, n_mu, new_val):
    """Computes the mean of an array after adding a new value to it.

    Note:
    -----
    If the new value is a NaN, NaN is returned.

    Parameters
    ----------
    mu : float`
        Mean value of the array before adding the new value
    n_mu : `int`
        Number of values in the array before adding the new value
    new_val : `float`
        The new value
    """
    return (mu * n_mu + new_val) / (n_mu + 1)


def developing_mean(x: np.ndarray, axis: int):
    """computing the running mean of an array along a given axis"""

    if x.ndim == 1:
        return developing_mean_1d(x)

    if axis == -1:
        axis = x.ndim
    if axis >= x.ndim:
        raise ValueError("Invalid axis value.")
    if axis == 0:
        _x = x
    else:
        _x = np.moveaxis(x, axis, 0)
    xm = np.zeros_like(_x)
    m = _x[0, :]
    for i in range(1, _x.shape[0]):
        m = next_mean(m, i, _x[i, :])
        xm[i, :] = m
    if axis == 0:
        return xm
    return np.moveaxis(xm, 0, axis)


def developing_mean_1d(arr):
    developing_sum = 0
    developing_means = arr.copy()

    for i, value in enumerate(arr, start=1):
        developing_sum += value
        mean = developing_sum / i
        developing_means[i - 1] = mean

    return developing_means


def developing_std(x, axis, ddof=0):
    """shape of x : nt x ndata"""

    if axis == -1:
        axis = x.ndim
    if axis >= x.ndim:
        raise ValueError("Invalid axis value.")
    if axis == 0:
        _x = x
    else:
        _x = np.moveaxis(x, axis, 0)

    x2 = _x ** 2
    std = np.zeros_like(_x)
    sum_of_x = np.sum(_x[0:ddof + 1], axis=0)
    sum_of_x_squared = np.sum(x2[0:ddof + 1], axis=0)
    std[0:ddof + 1] = np.nan
    for i in range(ddof + 1, _x.shape[0]):
        sum_of_x, sum_of_x_squared, std[i, :] = next_std(sum_of_x, sum_of_x_squared, i, _x[i, :], ddof=ddof)

    if axis == 0:
        return std
    return np.moveaxis(std, 0, axis)


def developing_relative_standard_deviation(x, axis, ddof=0):
    """Computes the running relative standard deviation using the running
    mean as normalization."""
    if axis == -1:
        axis = x.ndim
    if axis >= x.ndim:
        raise ValueError("Invalid axis value.")
    if axis == 0:
        _x = x
    else:
        _x = np.moveaxis(x, axis, 0)

    rrstd = developing_std(_x, axis=0, ddof=ddof) / developing_mean(_x, axis=0)

    if axis == 0:
        return rrstd
    return np.moveaxis(rrstd, 0, axis)


# Normality tests (taken from https://www.kaggle.com/code/shashwatwork/guide-to-normality-tests-in-python):


def xrwrapper(func):
    @wraps(func)
    def wrapper(data, method, axis, alpha):
        if isinstance(data, xr.DataArray):
            res = func(data.values, method, axis, alpha)
            coords = {k: v for i, (k, v) in enumerate(data.coords.items()) if i != axis}
            dims = [k for i, k in enumerate(data.dims) if i != axis]
            return xr.DataArray(res, coords=coords, dims=dims)
        return func(data, method, axis, alpha)

    return wrapper


@xrwrapper
def is_gaussian(data, method: str, axis=0, alpha: float = 0.05) -> Union[bool, np.ndarray]:
    """Tests if the data is Gaussian distributed.
    Available methods are:
    - 'shapiro' (the fastest)
    - 'anderson_darling'
    - 'agostino_pearson'

    Parameters
    ----------
    data : `np.ndarray`
        The data to test
    method : `str`
        The method to use
    axis : `int`
        The axis along which to test
    alpha : `float`
        The significance level

    Returns
    -------
    `bool` or `np.ndarray`
        True if the data is Gaussian distributed, False otherwise.
    """
    if method == 'agostino_pearson':
        return agostino_pearson_test(data, axis=axis, alpha=alpha)

    if method == 'shapiro':
        mfunc = shapiro_wilk
    elif method == 'anderson_darling':
        mfunc = anderson_darling_test
        alpha = _get_anderson_critical_value_index(alpha)
    else:
        raise ValueError(f"Unknown method: {method}")

    if data.ndim == 1:
        return mfunc(data, alpha=alpha)

    if data.ndim == 2:
        if axis == 0:
            return np.asarray([mfunc(data[:, i], alpha=alpha) for i in range(data.shape[1])])
        # elif axis == 1:
        return np.asarray([mfunc(data[i, :], alpha=alpha) for i in range(data.shape[0])])

    if data.ndim == 3:
        if axis == 0:
            _, ny, nx = data.shape
            return np.asarray(
                [[mfunc(data[:, i, j], alpha=alpha) for i in range(ny)] for j in range(nx)]).T
        elif axis == 1:
            ny, _, nx = data.shape
            return np.asarray(
                [[mfunc(data[i, :, j], alpha=alpha) for i in range(ny)] for j in range(nx)]).T
        # elif axis == 2:
        ny, nx, _ = data.shape
        return np.asarray(
            [[mfunc(data[i, j, :], alpha=alpha) for i in range(ny)] for j in range(nx)]).T

    raise ValueError(f'data.ndim must be 1, 2 or 3 but got {data.ndim}')


def _get_anderson_critical_value_index(alpha) -> int:
    """Returns the index of the critical value for the Anderson-Darling test"""
    alpha_ls = {v: i for i, v in enumerate((0.15, 0.1, 0.05, 0.025, 0.01))}
    i_alpha = alpha_ls.get(alpha, None)
    if i_alpha is None:
        raise ValueError(f'alpha must be one of {alpha_ls.keys()} but got {alpha}')
    return i_alpha


def anderson_darling_test(data, alpha: int) -> float:
    """Anderson-Darling test for normality
    Note, that alpha is used differently here
    """
    res = anderson(np.asarray(data))
    return res.statistic < res.critical_values[alpha]


def shapiro_wilk(data, alpha=0.05) -> bool:
    """Shapiro-Wilk test for normality"""
    if data.ndim != 1:
        raise ValueError('data must be 1D')
    stat, p = shapiro(data)
    # interpret results
    # alpha = 0.05
    # if p > alpha:
    #     print('Sample looks Gaussian (fail to reject H0)')
    # else:
    #     print('Sample does not look Gaussian (reject H0)')
    return p > alpha


def agostino_pearson_test(data, axis, alpha=0.05):
    """D'Agostino and Pearson's Test for normality"""
    stat, p = normaltest(data, axis=axis)
    # print('Statistics=%.3f, p=%.3f' % (stat, p))
    # interpret results
    # alpha = 0.05
    # if p > alpha:
    #     print('Sample looks Gaussian (fail to reject H0)')
    # else:
    #     print('Sample does not look Gaussian (reject H0)')
    return p > alpha
