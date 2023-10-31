"""statistics module"""
import numpy as np
import pandas as pd
import xarray as xr


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
    """Computes the mean of an array after adding a new value to it

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


def running_mean(x: np.ndarray, axis: int):
    """computing the running mean of an array along a given axis"""
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


def running_std(x, axis, ddof=0):
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


def running_relative_standard_deviation(x, axis, ddof=0):
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

    rrstd = running_std(_x, axis=0, ddof=ddof) / running_mean(_x, axis=0)

    if axis == 0:
        return rrstd
    return np.moveaxis(rrstd, 0, axis)
