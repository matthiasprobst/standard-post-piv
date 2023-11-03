import matplotlib.pyplot as plt
import numpy as np

from standardpostpiv.statistics import is_gaussian

arr1d_norm = np.random.normal(0, 1, 100)
arr1d_notnorm = np.random.uniform(0, 1, 100)

assert is_gaussian(arr1d_norm, axis=0, method='shapiro', alpha=0.05)
assert is_gaussian(arr1d_notnorm, axis=0, method='shapiro', alpha=0.05) is False

arr2d_norm = np.random.normal(0, 1, (100, 50))
arr2d_notnorm = np.random.uniform(0, 1, (100, 50))

is_gauss2d_nrom = is_gaussian(arr2d_norm, axis=0, method='shapiro', alpha=0.05)
assert is_gauss2d_nrom.shape == (50,)
assert is_gauss2d_nrom.sum() > 40

is_gauss2d_nrom = is_gaussian(arr2d_norm, axis=0, method='anderson_darling', alpha=0.05)

plt.figure()
for i in range(arr2d_norm.shape[1]):
    plt.hist(arr2d_norm[:, i])
plt.show()
