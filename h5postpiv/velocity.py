import xarray as xr

from .core import ReportItem


class Velocity(ReportItem):
    """Report velocity interface class"""
    identifier = {'u': 'x_velocity',
                  'v': 'y_velocity',
                  'w': 'z_velocity',
                  'mag_inplane': 'inplane_velocity',
                  'mag': 'magnitude_of_velocity',
                  }

    @property
    def x(self):
        """x-velocity"""
        return self.get_dataset_by_standard_name(self.identifier['u'])

    @property
    def y(self):
        """y-velocity"""
        return self.get_dataset_by_standard_name(self.identifier['v'])

    @property
    def z(self):
        """y-velocity"""
        return self.get_dataset_by_standard_name(self.identifier['w'])

    @property
    def inplane_velocity(self):
        """in-plane velocity magnitude"""
        mag_inplane = self.get_dataset_by_standard_name('mag_inplane')
        if mag_inplane is None:
            return self.compute_inplane_velocity().inplane_velocity_magnitude

    @property
    def mean_inplane_velocity(self):
        return self.inplane_vector.mean('time')

    @property
    def inplane_vector(self):
        """velocity vector"""
        u = self.x[:]
        v = self.y[:]
        mag = self.inplane_velocity[:]
        return xr.Dataset(dict(u=u, v=v, mag=mag))

    @property
    def mean_inplane_vector(self):
        """mean velocity vector"""
        with xr.set_options(keep_attrs=True):
            return self.inplane_vector.mean('time')

    # def quiver(self, mean=True):
    #     vec =

    @property
    def magnitude(self):
        """velocity magnitude"""
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

    def is_2D2C(self) -> bool:
        """If there is no w-component in the file, the data is 2d"""
        return self.z is None

    def is_2D3C(self) -> bool:
        """If there is no w-component in the file, the data is 2d"""
        return not self.is_2d2d()

    def compute_inplane_velocity(self, write_to_file=True):
        """compute magnitude of velocity vectors for all times and planes"""

        # noinspection PyUnresolvedReferences
        from h5rdmtoolbox.extensions import vector, magnitude
        import h5rdmtoolbox as h5tbx
        mode = 'r+' if write_to_file else 'r'
        with h5tbx.File(self.filename, mode) as h5:
            vec = h5.Vector(u=self.x.name, v=self.y.name)[:]
            vec.magnitude.compute_from(self.x.basename, self.y.basename,
                                       name='inplane_velocity_magnitude',
                                       attrs={'standard_name': 'inplane_velocity'})
            if write_to_file:
                with h5tbx.File(self.tmp_filename, 'r+') as h5tmp:
                    h5tmp.create_dataset_from_xarray_dataarray(vec.inplane_velocity_magnitude)
            return vec

    def compute_magnitude(self, write_to_file=True):
        """compute magnitude of velocity vectors for all times and planes"""

        if self.is_2D2C():
            vec = self.compute_inplane_velocity()
            vec.attrs['name'] = 'velocity_magnitude'
            vec.attrs['standard_name'] = 'magnitude_of_velocity'
            return vec

        # noinspection PyUnresolvedReferences
        from h5rdmtoolbox.extensions import vector, magnitude
        import h5rdmtoolbox as h5tbx
        mode = 'r+' if write_to_file else 'r'
        with h5tbx.File(self.filename, mode) as h5:
            vec = h5.Vector(u=self.x.name, v=self.y.name, w=self.z.name)[:]
            vec.magnitude.compute_from(self.x.basename, self.y.basename, self.z.basename,
                                       name='inplane_velocity_magnitude',
                                       attrs={'standard_name': 'inplane_velocity'})
            if write_to_file:
                with h5tbx.File(self.tmp_filename, 'r+') as h5tmp:
                    h5tmp.create_dataset_from_xarray_dataarray(vec.inplane_velocity_magnitude)
            return vec

    def plot_mean_inplane_velocity(self, contourf=True, quiver=True):
        """plot mean in-plane velocity"""
        if contourf:
            self.inplane_vector.mag.mean('time').plot.contourf(cmap='viridis')

        if quiver:
            self.inplane_vector.mean('time').every([4, 8]).plot.quiver('x', 'y', 'u', 'v', scale=200,
                                                                       color='k')
