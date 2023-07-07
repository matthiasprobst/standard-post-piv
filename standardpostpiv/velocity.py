import xarray as xr

from .displacement import Displacement


class MovigReferenceFrameVelocity:
    identifier = {'u': 'x_velocity_of_moving_frame',
                  'v': 'y_velocity_of_moving_frame',
                  'w': 'z_velocity_of_moving_frame',
                  }

    def __init__(self, filename):
        self.filename = filename



class Velocity(Displacement):
    """Report velocity interface class"""
    identifier = {'u': 'x_velocity',
                  'v': 'y_velocity',
                  'w': 'z_velocity',
                  'mag_inplane': 'inplane_velocity',
                  'mag': 'magnitude_of_velocity',
                  }

    @property
    def moving_reference_frame(self):
        return

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

        mag = mag_inplane[:]
        flags = self.flags[:]
        return xr.Dataset(dict(u=self.x, v=self.y, mag=mag, flags=flags))

    @property
    def mean_inplane_velocity(self):
        # TODO: This is too simple: If there are values masked along the way, the mean will be wrong
        with xr.set_options(keep_attrs=True):
            return self.inplane_velocity.where(self.inplane_velocity.flags & 1).mean('time')

    @property
    def inplane_vector(self):
        """velocity vector"""
        u = self.x[:]
        v = self.y[:]
        mag = self.inplane_velocity[:]
        flags = self.flags[:]
        return xr.Dataset(dict(u=u, v=v, mag=mag, flags=flags))

    @property
    def inplane_vector_in_moving_frame(self):
        u = self.x[:].piv.in_moving_frame()
        v = self.y[:].piv.in_moving_frame()
        import numpy as np
        mag = (np.sqrt(u.pint.quantify() ** 2 + v.pint.quantify() ** 2)).pint.dequantify()

        mag.attrs['standard_name'] = 'magnitude_of_velocity_in_moving_frame'
        ds = xr.Dataset(dict(u=u, v=v, mag=mag))
        return ds

    @property
    def mean_inplane_vector(self):
        """mean velocity vector. The return data considers only active vectors (piv flag == 1)"""
        with xr.set_options(keep_attrs=True):
            return self.inplane_vector.where(self.inplane_vector.flags & 1).mean('time')

    @property
    def magnitude(self):
        """velocity magnitude"""
        res = self.get_dataset_by_standard_name(self.identifier['mag'])
        if res is None:
            vel_vec = self.compute_magnitude()
            return vel_vec

    def time_average(self, piv_flag=1):
        """compute the time average of the velocity vector for all vectors that are bitwise-true for the given flag"""
        with xr.set_options(keep_attrs=True):
            return self.inplane_vector.where(self.inplane_vector.flags & piv_flag).mean('time')

    def is_2D2C(self) -> bool:
        """If there is no w-component in the file, the data is 2d"""
        return self.z is None

    def is_2D3C(self) -> bool:
        """If there is no w-component in the file, the data is 2d"""
        return not self.is_2D2C()

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
