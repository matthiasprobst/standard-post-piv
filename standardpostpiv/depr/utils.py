import pathlib
from typing import List

import h5rdmtoolbox as h5tbx
import numpy as np
from IPython.display import display, Markdown


class StandardCoordinate:
    """Collection of 1D coordinates"""

    def __init__(self, name, component_names, parent):
        self._parent = parent
        self.name = name
        self.tensor_names = [c.split('_', 1) for c in component_names]
        self.components = {c: getattr(parent, c) for c in component_names}
        self.component_names = sorted(list(self.components.keys()))
        for component in component_names:
            c, _ = component.split('_', 1)
            setattr(self, c, self.components[component])

    def __iter__(self):
        return iter(self.components.values())

    def __getitem__(self, item):
        return self.components[self.component_names[0]]

    def __len__(self):
        return len(self.components)

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.name}" n={len(self.components)}>'

    @property
    def shape(self):
        return tuple([c.shape[0] for c in self.components.values() if c.ndim == 1])


class StandardTensor(StandardCoordinate):

    def get(self, *component_names):
        if len(component_names) == 1:
            if len(component_names[0]) == 1:
                raise ValueError(f'Not enough components given: {component_names}')
            component_names = [c for c in component_names[0]]
        return StandardTensor('velocity', [f'{c}_{self.name}' for c in component_names], self._parent)

    @property
    def ndim(self):
        return self[0].ndim

    def magnitude(self):
        """Compute the magnitude of the tensor"""
        square = self.components[self.component_names[0]][()] ** 2
        for c in self.component_names[1:]:
            square += self.components[c][()] ** 2
        mag = np.sqrt(square)
        units = square.units
        mag.attrs = dict()
        mag.attrs['standard_name'] = f'square_of_{self.name}'
        mag.attrs['units'] = units
        return mag

    def plot(self):
        return plot_tensor(self)


def plot_tensor(tensor):
    if tensor.ndim == 2:
        mag = tensor.magnitude()
        return mag.plot()
    raise ValueError('Only 2D tensor can be plotted like this')


class HDF5StandardInterface:
    def __init__(self,
                 hdf_filename,
                 source_group: str = '/'):
        self._hdf_filename = pathlib.Path(hdf_filename)
        self._list_of_lazy_datasets = {}

        with h5tbx.File(hdf_filename) as h5:
            standard_names = {ds.attrs['standard_name']: ds.parent.name for ds in
                              h5[source_group].find({'standard_name': {'$regex': '.*'}})}

        standard_datasets = {k: h5tbx.database.File(self._hdf_filename).find_one({'standard_name': k}) for k in
                             standard_names}

        for k, ds in standard_datasets.items():
            if ds.ndim == 0:
                setattr(self, k, ds[()])
            else:
                setattr(self, k, ds)

        unique_groups = set(standard_names.values())
        groups = {g: [] for g in unique_groups}
        for k, v in standard_names.items():
            groups[v].append(k)

        # identify tensors based on components:
        components = ('x', 'y', 'z')
        tensors_condidates = {}
        import re
        for k, v in standard_names.items():
            for c in components:
                if re.match(f'^{c}_.*$', k):
                    _, base_quantity = k.split('_', 1)
                    if base_quantity not in tensors_condidates:
                        tensors_condidates[base_quantity] = [k, ]
                    else:
                        tensors_condidates[base_quantity].append(k)

        self.tensors = []
        self.coords = []
        for k, v in tensors_condidates.items():
            if len(v) > 1:
                if all(standard_datasets[c].shape == standard_datasets[v[0]].shape for c in v[1:]):
                    vec = StandardTensor(k, v, self)
                    self.tensors.append(vec)
                    setattr(self, k, vec)
                else:
                    coord = StandardCoordinate(k, v, self)
                    self.coords.append(coord)
                    setattr(self, k, coord)
        self.standard_names = standard_names
        self.standard_datasets = standard_datasets

    @property
    def filename(self):
        return self._hdf_filename

    def __repr__(self):
        vec_names = '\n  - '.join(v.name for v in self.tensors)
        return f'<{self.__class__.__name__}\n > tensors:\n  - {vec_names}\n > others: ...>'


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
    res = h5tbx.database.File(filename).find_one({'standard_name': sn}, '$dataset')
    if res is None and tmp_filename is not None:
        res = h5tbx.database.File(tmp_filename).find_one({'standard_name': sn})
    return res


def display_as_badges(data, inline: bool = False, color_info={'__default': 'green',
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
        if '%' in _str:
            _str = _str.replace('%', '%25')
        badge_str = f'![nbviewer](https://img.shields.io/badge/{k}-{_str}-{_get_badge_color(k)}.svg)'
        if isinstance(v, str):
            if v.startswith('https://') or v.startswith('www.'):
                badge_str = f'[{badge_str}]({v})'
        _shield_strings.append(badge_str)
    if inline:
        return Markdown(' '.join(_shield_strings))
    display(Markdown('<br>'.join(_shield_strings)))
