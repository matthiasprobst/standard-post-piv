import xarray as xr
from h5rdmtoolbox import File
from typing import Dict

from .core import ReportItem


class PIVDataset:
    """Interface class to HDF datasets. Data is only loaded when requested (sliced).
    Otherwise file is closed."""
    __obj_attrs = ('file', 'name', 'attrs',
                   'ndim', 'shape', 'dtype', 'size',
                   'chunks', 'compression', 'compression_opts',
                   'shuffle', 'dims')

    def __init__(self, name, dataset, properties):
        self.dataset = dataset
        self.name = name
        self.properties = properties

    def __getattr__(self, item):
        if item in self.properties:
            return self.properties[item]
        if item in self.__obj_attrs:
            with File(self.dataset.filename) as h5:
                if item == 'attrs':
                    return dict(h5[self.dataset.name].attrs)
                return h5[self.dataset.name].__getattribute__(item)
        return super().__getattribute__(item)

    def __repr__(self):
        # TODO: add dims/coords to shape repr
        sn = self.standard_name
        return f'PIVDataset(name="{self.name}", standard_name="{sn}", shape={self.dataset.shape})'

    def sel(self, *args, **kwargs):
        with File(self.dataset.filename) as h5:
            target_dataset = h5[self.dataset.name]
            piv_flag = h5.find_one({'standard_name': 'piv_flags'}, '$dataset')
            if piv_flag is None:
                raise ValueError('HDF5 Dataset with standard name attribute "piv_flags" not found in file')
            return xr.Dataset({self.name: target_dataset.sel(*args, **kwargs),
                               'flags': piv_flag.sel(*args, **kwargs)},
                              attrs=target_dataset.attrs)

    def __getitem__(self, item):
        with File(self.dataset.filename) as h5:
            target_dataset = h5[self.dataset.name]
            piv_flag = h5.find_one({'standard_name': 'piv_flags'}, '$dataset')
            if piv_flag is None:
                raise ValueError('HDF5 Dataset with standard name attribute "piv_flags" not found in file')
            return xr.Dataset({self.name: target_dataset[item], 'flags': piv_flag[item]},
                              attrs=target_dataset.attrs)


class Displacement(ReportItem):
    """Report displacement interface class"""

    identifier = {'u': 'x_displacement',
                  'v': 'y_displacement',
                  'mag_inplane': 'inplane_displacement',
                  'mag': 'magnitude_of_displacement',
                  }

    def __build_piv_datasets(self, standard_names: Dict) -> xr.Dataset:
        """builds a dataset with the HDF5 dataset based on the given standard_name and provides piv flag as
        additional dataset"""
        flag = self.flags[:]
        data = {name: self.get_dataset_by_standard_name(sn)[()] for name, sn in standard_names.items()}
        data['flag'] = flag
        return xr.Dataset(data)

    def __build_piv_dataset(self, name, standard_name) -> xr.Dataset:
        """builds a dataset with the HDF5 dataset based on the given standard_name and provides piv flag as
        additional dataset"""
        if name is None:
            name = standard_name
        return self.__build_piv_datasets({name: standard_name})

    @property
    def flags(self):
        """return piv flag data array"""
        return self.get_dataset_by_standard_name('piv_flags')

    @property
    def x(self):
        """x-displacement"""
        h5ds = self.get_dataset_by_standard_name(self.identifier['u'])
        if h5ds is None:
            raise ValueError(f'No dataset with standard name {self.identifier["u"]} found in file')
        return h5ds
        # return PIVDataset(
        #     'u',
        #     h5ds,
        #     properties=dict(h5ds.attrs)
        # )

    @property
    def y(self):
        """y-displacement"""
        return self.get_dataset_by_standard_name(self.identifier['v'])

    @property
    def inplane_displacement(self):
        """in-plane displacement magnitude"""
        mag_inplane = self.get_dataset_by_standard_name('mag_inplane')
        if mag_inplane is None:
            return self.compute_inplane_displacement().inplane_displacement_magnitude

    @property
    def mean_inplane_displacement(self):
        return self.inplane_vector.mean('time')

    @property
    def vector(self):
        """alias for `inplane_vector`"""
        return self.inplane_vector

    @property
    def inplane_vector(self):
        """displacement vector"""
        u = self.x[:]
        v = self.y[:]
        mag = self.inplane_displacement[:]
        return xr.Dataset(dict(u=u, v=v, mag=mag))

    @property
    def mean_inplane_vector(self):
        """mean displacement vector"""
        with xr.set_options(keep_attrs=True):
            return self.inplane_vector.mean('time')

    @property
    def magnitude(self):
        """displacement magnitude"""
        return self.get_dataset_by_standard_name('mag')

    @property
    def ndim(self) -> int:
        return self.x.ndim

    def is_snapshot(self) -> bool:
        return self.ndim == 2

    def is_plane(self) -> bool:
        return self.ndim == 3

    def is_mplane(self) -> bool:
        return self.ndim == 4

    def compute_inplane_displacement(self, write_to_file=True):
        """compute magnitude of displacement vectors for all times and planes"""

        # noinspection PyUnresolvedReferences
        from h5rdmtoolbox.extensions import vector, magnitude
        import h5rdmtoolbox as h5tbx
        mode = 'r+' if write_to_file else 'r'
        with h5tbx.File(self.filename, mode) as h5:
            vec = h5.Vector(u=self.x.name, v=self.y.name)[:]
            vec.magnitude.compute_from('u', 'v',
                                       name='inplane_displacement_magnitude',
                                       attrs={'standard_name': 'inplane_displacement'})
            if write_to_file:
                with h5tbx.File(self.tmp_filename, 'r+') as h5tmp:
                    h5tmp.create_dataset_from_xarray_dataarray(vec.inplane_displacement_magnitude)
            return vec

    def compute_magnitude(self, write_to_file=True):
        """compute magnitude of displacement vectors for all times and planes"""

        if self.is_2D2C():
            vec = self.compute_inplane_displacement()
            vec.attrs['name'] = 'displacement_magnitude'
            vec.attrs['standard_name'] = 'magnitude_of_displacement'
            return vec

        # noinspection PyUnresolvedReferences
        from h5rdmtoolbox.extensions import vector, magnitude
        import h5rdmtoolbox as h5tbx
        mode = 'r+' if write_to_file else 'r'
        with h5tbx.File(self.filename, mode) as h5:
            vec = h5.Vector(u=self.x.name, v=self.y.name, w=self.z.name)[:]
            vec.magnitude.compute_from(self.x.basename, self.y.basename, self.z.basename,
                                       name='inplane_displacement_magnitude',
                                       attrs={'standard_name': 'inplane_displacement'})
            if write_to_file:
                with h5tbx.File(self.tmp_filename, 'r+') as h5tmp:
                    h5tmp.create_dataset_from_xarray_dataarray(vec.inplane_displacement_magnitude)
            return vec

    def plot_mean_inplane_displacement(self, contourf=True, quiver=True):
        """plot mean in-plane displacement"""
        if contourf:
            self.inplane_vector.mag.mean('time').plot.contourf(cmap='viridis')

        if quiver:
            self.inplane_vector.mean('time').every([4, 8]).plot.quiver('x', 'y', 'u', 'v', scale=200,
                                                                       color='k')
