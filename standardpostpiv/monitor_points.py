import numpy as np
from typing import List, Tuple


def get_closes_index(arr, val):
    return int(np.abs((arr - val)).argmin())


def _is_valid(mask, point, min_dist):
    """validates the given point. It must be surrounded by unmasked
    points only and have a distance to the borders and other points"""
    iy, ix = point
    ny, nx = mask.shape
    assert mask.ndim == 2
    ixmin = ix - min_dist
    if ixmin < 0:
        return False
    ixmax = ix + min_dist
    if ixmax >= nx:
        return False
    iymin = iy - min_dist
    if iymin < 0:
        return False
    iymax = iy + min_dist
    if iymax >= ny:
        return False
    surrounding = mask[iymin:iymax, ixmin:ixmax]

    if surrounding.size < min_dist ** 2:
        return False

    return np.all(~surrounding.values.ravel())


class MonitorPoints:
    """Monitor Point class mainly for assisting with automated
    monitor point generation based on mask data"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._ipoints = []
        self._manual_set = None

        self._current_index = 0

    def __repr__(self):
        if self._manual_set is None:
            return f'<Monitor Points n={self.__len__()}>'
        if self._manual_set:
            return f'<Monitor Points n={self.__len__()} (manual set)>'
        return f'<Monitor Points n={self.__len__()} (auto generated)>'

    def __len__(self):
        return len(self._ipoints)

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < self.__len__():
            point = self.points[self._current_index]
            self._current_index += 1
            return point
        else:
            self._current_index = 0
            raise StopIteration()

    @property
    def points(self):
        """Return points in physical coordinates"""
        if self.__len__() == 0:
            raise ValueError('No points available')
        return [(self.x[ix], self.y[iy]) for ix, iy in self._ipoints]

    @property
    def indices(self):
        return self._ipoints

    def plot(self, mask, ax=None, **kwargs):
        if ax is None:
            import matplotlib.pyplot as plt
            ax = plt.gca()
        mask.plot(cmap='binary', ax=ax)
        marker = kwargs.pop('marker', '+')
        red = kwargs.pop('red', 'r')
        for i, xy in enumerate(self.points):
            ax.scatter(*xy, color=red, marker=marker, **kwargs)

    def iset(self, point_indices: List[Tuple[int, int]]):
        """set monitor points based on coordinate indices"""
        self._ipoints = point_indices
        return self._ipoints
        # return self.set([(self.x[a], self.y[b]) for a, b in point_indices])

    def set(self, points: List[Tuple[float, float]]):
        """manually setting the points"""
        self._manual_set = True
        if not isinstance(points, (list, tuple)):
            raise TypeError(f'Expecting list or tuple of points but got {type(points)}')
        self._ipoints = [(get_closes_index(self.x[()], a),
                          get_closes_index(self.y[()], b)) for a, b in points]
        return self._ipoints

    def generate(self, mask, n, min_dist, ref: bool = False):
        """generate seeding points"""
        self._manual_set = False
        unmasked_indices = np.where(mask == ref)

        num_unmasked = len(unmasked_indices[0])

        if num_unmasked == n:
            raise ValueError("No unmasked locations found.")

        if num_unmasked <= n:
            raise ValueError(
                f"Impossible to seed {n} points because there are not enough unmasked area: {num_unmasked}")

        monitor_indices = []
        n_seeded = 0
        counter = 0
        max_counter = 10 * n

        while n_seeded < n and counter <= max_counter:
            counter += 1
            idx = np.random.randint(num_unmasked)

            point = (unmasked_indices[1][idx], unmasked_indices[0][idx])

            if _is_valid(mask, point, min_dist):
                monitor_indices.append(point)
                n_seeded += 1

        return self.iset(monitor_indices)
