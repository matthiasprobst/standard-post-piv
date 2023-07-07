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


class PIVVector:
    __slots__ = ('filename', 'standard_name_identifier')

    def __init__(self, filename, standard_name_identifier):
        self.filename = filename
        self.standard_name_identifier = standard_name_identifier

    @property
    def mag(self):
        h5ds = utils.get_dataset_by_standard_name(self.filename, self.standard_name_identifier['mag'])
        if h5ds is None:
            return PIVVectorMagnitude(self.x, self.y)

    # def compute_magnitude(self, store_in_file=False):
    #     """Compute the magnitude of the vector field and store it in a temporary HDF5 file quick access at a later
    #     time. If store_in_file is True, the magnitude is written to the file"""

    def __getattr__(self, item):
        if item in self.standard_name_identifier:
            h5ds = utils.get_dataset_by_standard_name(self.filename, self.standard_name_identifier[item])
            if h5ds is None:
                raise ValueError(f'No dataset with standard name {self.standard_name_identifier[item]} found in file')
            return h5ds
        return self.__getattribute__(item)
