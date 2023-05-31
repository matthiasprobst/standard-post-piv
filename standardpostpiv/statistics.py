"""statistics module"""
import numpy as np
import pandas as pd
import xarray as xr



def stats(target):
    """compute stats for the target"""
    if isinstance(target, xr.DataArray):
        return pd.DataFrame(
            {target.name: {
                'min': target.min().values,
                'max': target.max().values,
                'mean': target.mean().values,
                'std': target.std().values, }
            }
        )
    elif isinstance(target, xr.Dataset):
        df = [stats(v) for k, v in target.items()]
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


def _transpose_and_reshape_input(x, axis):
    return x.transpose([axis, *[ax for ax in range(x.ndim) if ax != axis]]).reshape(
        (x.shape[axis], x.size // x.shape[axis]))


def _transpose_and_reshape_back_to_original(x, orig_shape, axis):
    ndim = len(orig_shape)
    transpose_order = np.zeros(ndim).astype(int)
    transpose_order[axis] = 0
    k = 1
    for j in range(ndim):
        if j != axis:
            transpose_order[j] = k
            k += 1
    return x.reshape([orig_shape[axis], *[orig_shape[ax] for ax in range(ndim) if ax != axis]]).transpose(
        transpose_order)


def running_mean(x: np.ndarray, axis=0):
    """computing the running mean of an array along a given axis"""
    if axis == -1:
        axis = x.ndim
    _x = _transpose_and_reshape_input(x, axis)
    xm = np.zeros_like(_x)
    m = _x[0, :]
    for i in range(1, _x.shape[0]):
        m = next_mean(m, i, _x[i, :])
        xm[i, :] = m
    return _transpose_and_reshape_back_to_original(xm, x.shape, axis)


def running_std(x, axis, ddof=0):
    """shape of x : nt x ndata"""
    if axis == -1:
        axis = x.ndim
    _x = _transpose_and_reshape_input(x, axis)
    x2 = _x ** 2
    std = np.zeros_like(_x)
    sum_of_x = np.sum(_x[0:ddof + 1], axis=0)
    sum_of_x_squared = np.sum(x2[0:ddof + 1], axis=0)
    std[0:ddof + 1] = np.nan
    for i in range(ddof + 1, _x.shape[0]):
        sum_of_x, sum_of_x_squared, std[i, :] = next_std(sum_of_x, sum_of_x_squared, i, _x[i, :], ddof=ddof)
    return _transpose_and_reshape_back_to_original(std, x.shape, axis)


def running_relative_standard_deviation(x, axis, ddof=0):
    """Computes the running relative standard deviation using the running
    mean as normalization."""
    return running_std(x, axis, ddof) / running_mean(x, axis)
