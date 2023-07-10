import h5rdmtoolbox as h5tbx
import numpy as np
from IPython.display import display, Markdown
from typing import List


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

    def generate(self, ref: bool = False):
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

        return [(self.x[a], self.y[b]) for a, b in seed_indices]


def generate_monitor_points(piv_mask, x, y, n, min_dist):
    """Generate seeding pts"""
    assert piv_mask.ndim == 2
    seeder = MaskSeeder(piv_mask, x, y, n, min_dist)
    seeding_points = seeder.generate()
    return seeding_points


def find_nearest_index(arr, target_value) -> int:
    """Find the index of the nearest value in x to the target value"""
    abs_diff = np.abs(arr - target_value)

    # Find the index of the minimum absolute difference
    nearest_index = abs_diff.argmin().item()

    return nearest_index


def find_nearest_indices(arr, target_values) -> List[int]:
    """Find the indices of the nearest values in x to the target values"""
    return [find_nearest_index(arr, t) for t in target_values]


def get_dataset_by_standard_name(filename, sn, tmp_filename=None):
    """returns lazy object. See `h5rdmtoolbox.database.lazy`.
    Searches in original file and if none found in temporary file"""
    res = h5tbx.FileDB(filename).find_one({'standard_name': sn}, '$dataset')
    if res is None and tmp_filename is not None:
        res = h5tbx.FileDB(tmp_filename).find_one({'standard_name': sn})
    return res


def display_as_badges(data, inline:bool=False,color_info={'__default': 'green',
                                        'contact': 'red',
                                        'type': 'green',
                                        'pivtype': 'blue',
                                        'software': 'blue',
                                        'pivmethod': 'lightgreen'}):
    def _get_badge_color(_k):
        if _k in color_info:
            return color_info[_k]
        return color_info['__default']

    _shield_strings = []
    for k, v in data.items():
        _str = f'{v}'.replace(' ', '_').replace('-', '--')
        _shield_strings.append(f'![nbviewer](https://img.shields.io/badge/{k}-{_str}-{_get_badge_color(k)}.svg)')
    if inline:
        return Markdown(' '.join(_shield_strings))
    display(Markdown('<br>'.join(_shield_strings)))
