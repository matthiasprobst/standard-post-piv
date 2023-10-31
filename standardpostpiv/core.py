import h5rdmtoolbox as h5tbx


def to_quantity(da):
    if da.ndim == 0:
        return h5tbx.get_ureg().Quantity(da.data, units=da.units)
    raise ValueError('DataArray must be 0D')


class StandardPIVResult:
    """Interface class to PIV results stored in a HDF5 file"""

    def __init__(self, hdf_filename):
        self.hdf_filename = hdf_filename
        distinct_standard_names = h5tbx.distinct(self.hdf_filename, 'standard_name')
        for dsn in distinct_standard_names:
            setattr(self, dsn, h5tbx.FileDB(self.hdf_filename).find_one({'standard_name': dsn}))
        with h5tbx.File(self.hdf_filename) as h5:
            self._param_grp_name = h5.find_one({'piv_method': {'$exists': True}}).name

    @property
    def eval_method(self):
        with h5tbx.File(self.hdf_filename) as h5:
            return h5[self._param_grp_name].attrs['piv_method']

    @property
    def final_iw_size(self):  # -> Tuple[int, int]:
        with h5tbx.File(self.hdf_filename) as h5:
            x = int(h5[self._param_grp_name]['x_final_iw_size'][()])
            y = int(h5[self._param_grp_name]['y_final_iw_size'][()])
        return x, y

    @property
    def overlap(self):  # -> Tuple[int, int]:
        with h5tbx.File(self.hdf_filename) as h5:
            x = int(h5[self._param_grp_name]['x_final_iw_overlap_size'][()])
            y = int(h5[self._param_grp_name]['y_final_iw_overlap_size'][()])
        return x, y

    @property
    def piv_dim(self):
        with h5tbx.File(self.hdf_filename) as h5:
            z_displacement = h5.find_one({'standard_name': 'z_displacement'})
            is2d2c = z_displacement is None
            if is2d2c:
                return '2D2C'
            else:
                return '2D3C'

    @property
    def piv_type(self):
        with h5tbx.File(self.hdf_filename) as h5:
            x_velocity = h5.find_one({'standard_name': 'x_velocity'})
            if x_velocity.ndim == 2:
                return 'snapshot'
            if x_velocity.ndim == 3:
                return 'plane'
            if x_velocity.ndim == 3:
                return 'mplane'

    def get_mask(self):
        return self.piv_flags[()] & 2

    # def get_displacement_vector(self,
    #                             dx='x_displacement',
    #                             dy='y_displacement',
    #                             dz='z_displacement',
    #                             mask:int=None) -> xr.Dataset:
    #     """Get displacement vector from a PIV file"""
    #     from .utils import build_vector
    #     dx = getattr(self, dx, None)
    #     dy = getattr(self, dy, None)
    #     dz = getattr(self, dz, None)
    #     data = {'dx': dx, 'dy': dy, 'dz': dz}
    #     return build_vector(**{k: v for k, v in data.items() if v is not None})
