import numpy as np
import xarray as xr


def apply_mask(da, flags, value):
    """Apply a mask to a DataArray"""
    if da.dims == flags.dims:
        return da.where(~flags & value)
    raise ValueError('Dimensions of DataArray and flag do not match')


def compute_magnitude(*args):
    """compute magnitude of a vector"""
    if len(args) < 2:
        raise ValueError('Need at least two components')
    c = args[0] ** 2
    for arg in args[1:]:
        c += arg ** 2
    return np.sqrt(c)


def build_vector(**kwargs) -> xr.Dataset:
    """Build a xr.Dataset from two components"""
    return xr.Dataset({k: v[()] for k, v in kwargs.items()})


class MaskSeeder:
    """Class to generate seeding points based on a mask input"""
    __slots__ = ('mask', 'n', 'min_dist', 'ny', 'nx', 'x', 'y')

    def __init__(self, mask, x, y, n, min_dist):
        assert mask.ndim == 2
        self.mask = mask
        self.ny, self.nx = mask.shape
        self.n = n
        self.min_dist = min_dist
        self.x = x
        self.y = y

    def is_valid(self, point):
        """validates the given point. It must be surrounded by unmasked
        points only and have a distance to the borders and other points"""
        iy, ix = point
        ixmin = ix - self.min_dist
        if ixmin < 0:
            return False
        ixmax = ix + self.min_dist
        if ixmax >= self.nx:
            return False
        iymin = iy - self.min_dist
        if iymin < 0:
            return False
        iymax = iy + self.min_dist
        if iymax >= self.ny:
            return False
        surrounding = self.mask[iymin:iymax, ixmin:ixmax]

        if surrounding.size < self.min_dist ** 2:
            return False

        return np.all(~surrounding.values.ravel())

    def generate(self, ref: bool = False, ret_indices: bool = False):
        """generate seeding points"""
        unmasked_indices = np.where(self.mask == ref)

        num_unmasked = len(unmasked_indices[0])

        if num_unmasked == self.n:
            raise ValueError("No unmasked locations found.")

        if num_unmasked <= self.n:
            raise ValueError(
                f"Impossible to seed {self.n} points because there are not enough unmasked area: {num_unmasked}")

        seed_indices = []
        n_seeded = 0
        counter = 0
        max_counter = 10 * self.n

        while n_seeded < self.n and counter <= max_counter:
            counter += 1
            idx = np.random.randint(num_unmasked)

            point = (unmasked_indices[0][idx], unmasked_indices[1][idx])

            if self.is_valid(point):
                seed_indices.append(point)
                n_seeded += 1
        if ret_indices:
            return seed_indices
        return [(self.x[a], self.y[b]) for b, a in seed_indices]
