import xarray as xr

from .core import ReportItem


class Displacement(ReportItem):
    """Report displacement interface class"""
    identifier = {'u': 'x_displacement',
                  'v': 'y_displacement',
                  'mag_inplane': 'inplane_displacement',
                  'mag': 'magnitude_of_displacement',
                  }

    @property
    def x(self):
        """x-displacement"""
        return self.get_dataset_by_standard_name(self.identifier['u'])

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
        # alias for `inplane_vector`
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
