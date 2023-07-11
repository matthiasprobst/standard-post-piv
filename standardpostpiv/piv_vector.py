import xarray as xr
# noinspection PyUnresolvedReferences
from h5rdmtoolbox.extensions import magnitude

from . import utils


class PIVVectorMagnitude:

    def __init__(self, x, y, z=None):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'PIVVectorMagnitude(x={self.x}, y={self.y}, z={self.z})'

    def _compute(self):
        if self.z is None:
            vec = xr.Dataset(dict(u=self.x, v=self.y))
            name = 'inplane_velocity_magnitude'
            standard_name = 'magnitude_of_inplane_velocity'
        else:
            name = 'velocity_magnitude'
            vec = xr.Dataset(dict(u=self.x, v=self.y, w=self.z))
            standard_name = 'magnitude_of_velocity'
        return vec.magnitude.compute_from('u', 'v', name=name, inplace=False,
                                          attrs={'standard_name': standard_name})

    def isel(self, **coords):
        self.x = self.x.isel(**coords)
        self.y = self.y.isel(**coords)
        if self.z is not None:
            self.z = self.z.isel(**coords)
        return self._compute()

    def sel(self, **coords):
        self.x = self.x.sel(**coords)
        self.y = self.y.sel(**coords)
        if self.z is not None:
            self.z = self.z.sel(**coords)
        return self._compute()

    def __getitem__(self, item):
        self.x = self.x.__getitem__(item)
        self.y = self.y.__getitem__(item)
        if self.z is not None:
            self.z = self.z.__getitem__(item)
        return self._compute()


class HDFXrDatasetInterface:

    def __init__(self, hdf_datasets):
        self._hdf_datasets = hdf_datasets

    def __getitem__(self, item):
        data_vars = {ds.basename: ds.__getitem__(item) for name, ds in self._hdf_datasets.items()}
        for dv in data_vars.values():
            assert isinstance(dv, xr.DataArray)
        return xr.Dataset(data_vars)


class PIVNDData:
    __slots__ = ('filename', 'standard_name_identifier', '_return_lazy')

    def __init__(self, filename, standard_name_identifier, return_lazy=True):
        self.filename = filename
        self.standard_name_identifier = standard_name_identifier
        self._return_lazy = return_lazy

    def __getitem__(self, name):
        if isinstance(name, tuple):
            return self._get_xr_dataset(*name)
        return self.__getattr__(name)

    def __getattr__(self, item):
        if item in self.standard_name_identifier:
            h5ds = utils.get_dataset_by_standard_name(self.filename, self.standard_name_identifier[item])
            if h5ds is None:
                raise ValueError(f'No dataset with standard name {self.standard_name_identifier[item]} found in file')
            if self._return_lazy:
                return h5ds
            else:
                return h5ds[()]
        return self.__getattribute__(item)

    def _get_xr_dataset(self, *names):
        for name in names:
            if name not in self.standard_name_identifier:
                raise ValueError(f'{name} not a valid standard name identifier for this object')
        return HDFXrDatasetInterface({name: self[name] for name in names})


class PIVVector(PIVNDData):

    @property
    def mag(self):
        h5ds = utils.get_dataset_by_standard_name(self.filename, self.standard_name_identifier['mag'])
        if h5ds is None:
            return PIVVectorMagnitude(self.x, self.y)

    # def compute_magnitude(self, store_in_file=False):
    #     """Compute the magnitude of the vector field and store it in a temporary HDF5 file quick access at a later
    #     time. If store_in_file is True, the magnitude is written to the file"""
