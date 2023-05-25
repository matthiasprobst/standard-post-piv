"""report module. piv reports are generated based on PIV HDF5 files.

The report is generated based on a certain convention!
"""

import pathlib
from typing import Dict

import h5rdmtoolbox as h5tbx

from .core import ReportItem
from .fov import FOV
from .velocity import Velocity

attribute_sn_dict = {'u': 'x_velocity',
                     'v': 'y_velocity',
                     'w': 'z_velocity',
                     'c': 'magnitude_of_velocity',
                     'x': 'x_coordinate',
                     'y': 'y_coordinate',
                     'z': 'z_coordinate',
                     'xpx': 'x_pixel_coordinate',
                     'ypy': 'y_pixel_coordinate',
                     }

DEFAULT_REPORT_DICT = {'general': True,
                       'contour': {'mean_velocity_magnitude': True}
                       }


class Report(ReportItem):
    """Report class"""

    identifier = {'x': 'x_coordinate',
                  'y': 'y_coordinate',
                  'ix': 'x_pixel_coordinate',
                  'iy': 'y_pixel_coordinate', }

    @property
    def x(self):
        """x-velocity"""
        return self.get_dataset_by_standard_name(self.identifier['x'])

    @property
    def y(self):
        """y-velocity"""
        return self.get_dataset_by_standard_name(self.identifier['y'])

    @property
    def ix(self):
        """x-velocity"""
        return self.get_dataset_by_standard_name(self.identifier['ix'])

    @property
    def iy(self):
        """y-velocity"""
        return self.get_dataset_by_standard_name(self.identifier['iy'])

    @property
    def pivtype(self) -> str:
        if self.velocity.is_2D2C():
            piv_dtype = '2D2C'
        elif self.velocity.is_2D3C():
            piv_dtype = '2D3C'
        else:
            piv_dtype = '?D?C'

        if self.velocity.is_plane():
            piv_dtype += ' (Plane)'
        elif self.velocity.is_mplane():
            piv_dtype += ' (Multi-Plane)'
        elif self.velocity.is_snapshot():
            piv_dtype += ' (Snapshot)'
        else:
            piv_dtype += ' (Unknown)'
        return piv_dtype

    def info(self):
        """return general information about the file"""
        import pandas as pd
        return pd.Series({'contact': self.contact,
                          'pivtype': self.pivtype,
                          'FOV': self.fov})

    @property
    def contact(self):
        with h5tbx.File(self.filename) as h5:
            return h5.attrs['contact']

    @property
    def velocity(self):
        return Velocity(self.filename)

    @property
    def fov(self):
        return FOV(self.filename)

    @property
    def notebook(self):
        """return a notebook object allowing to write a standard report on this PIV file"""
        from .notebook import PIVReportNotebook
        return PIVReportNotebook(self.filename)


# class _Report:
#     """Report class"""
#
#     def get_dataset_by_standard_name(self, sn):
#         """returns lazy object. See `h5rdmtoolbox.database.lazy`"""
#         return h5tbx.FileDB(self.filename).find_one({'standard_name': sn})
#
#     def __getattr__(self, item):
#         if item in attribute_sn_dict:
#             return self.get_dataset_by_standard_name(attribute_sn_dict[item])
#         return super().__getattribute__(item)
#
#     def __init__(self, filename, report_vel_units=None, report_coord_units=None):
#         self.filename = pathlib.Path(filename)
#
#         self.report_vel_units = report_vel_units  # if None take it from the file
#         self.report_coord_units = report_coord_units  # if None take it from the file
#
#         self._ndim = None
#
#         # with h5tbx.File(self.filename) as h5:
#         #     x = self.x[()]
#         #     self.xmin = x.min()
#         #     self.xmax = x.max()
#         #     y = self.y[()]
#         #     self.ymin = y.min()
#         #     self.ymax = y.max()
#         #     self.dx = self.x[0] - self.x[1]
#         #     self.dy = self.y[0] - self.y[1]
#         #
#         #     if self.report_vel_units is None:
#         #         self.report_vel_units = self.ds_dict['u'].attrs['units']
#         #
#         #     assert all(ds.attrs['units'] == self.report_vel_units for ds in self.ds_dict.values()), \
#         #         'All velocity components must have the same units!'
#         #
#         #     self.ds_dict['x'] = h5.find_one({'standard_name': 'x_coordinate'})
#         #     self.ds_dict['z'] = h5.find_one({'standard_name': 'y_coordinate'})
#         #
#         #     if self.report_coord_units is None:
#         #         self.report_coord_units = self.ds_dict['x'].attrs['units']
#         #
#         #     assert all(ds.attrs['units'] == self.report_coord_units for ds in self.ds_dict.values()), \
#         #         'All coordinate components must have the same units!'
#         #
#         #     self.data_cube_dim = self.ds_dict['u'].ndim
#         #     assert all(ds.ndim == self.data_cube_dim for ds in self.ds_dict.values()), \
#         #         'All velocity components must have the same number of dimensions!'
#         #
#         #     # TODO: For now assume, that coords are correct!
#         #     # 2D -> y, x
#         #     # 3D -> t, y, x
#         #     # 4D -> z, t, y, x
#         #     # if self.data_cube_dim.ndim == 2:
#         #     #     # check if the dimensions are x and y and not something else!
#         #
#         #     self.ds_dict['cabs'] = h5.find_one({'standard_name': 'magnitude_of_velocity'})
#         #
#         #     self.ds_dict['x'] = h5.find_one({'standard_name': 'x_pixel_coordinate'})
#
#     def __call__(self, report_dict: Dict = None):
#         if report_dict is None:
#             report_dict = DEFAULT_REPORT_DICT
#         for k, v in report_dict.items():
#             if k == 'general':
#                 print(self.general())
#             if k == 'contour':
#                 for kk, vv in v.items():
#                     if kk == 'mean_velocity_magnitude':
#                         self.plot_velocity_field(mean=True)
#
#     def general(self) -> str:
#         out = 'PIV Report\n----------'
#         out += f'\nPIV data type: {self.pivtype}'
#         return out
#
#     @property
#     def pivtype(self) -> str:
#         if self.is_2D2C():
#             piv_dtype = '2D2C'
#         elif self.is_2D3C():
#             piv_dtype = '2D3C'
#         else:
#             piv_dtype = '?D?C'
#
#         if self.is_plane():
#             piv_dtype += ' (Plane)'
#         elif self.is_mplane():
#             piv_dtype += ' (Multi-Plane)'
#         elif self.is_snapshot():
#             piv_dtype += ' (Snapshot)'
#         else:
#             piv_dtype += ' (Unknown)'
#         return piv_dtype
#
#     def ndim(self) -> int:
#         if self._ndim is None:
#             self._ndim = self.u.ndim
#         return self._ndim
#
#     def is_snapshot(self) -> bool:
#         return self.ndim == 2
#
#     def is_plane(self) -> bool:
#         return self.ndim == 3
#
#     def is_mplane(self) -> bool:
#         return self.ndim == 4
#
#     def is_2D2C(self) -> bool:
#         """If there is no w-component in the file, the data is 2d"""
#         return self.w is None
#
#     def is_2D3C(self) -> bool:
#         """If there is no w-component in the file, the data is 2d"""
#         return not self.is_2d2d()
#
#     @property
#     def velocity_vector(self):
#         with h5tbx.File(self.filename) as h5:
#             return h5.Vector(u=self.velocity.x.name, v=self.velocity.y.name)[:]
#
#     def compute_abs_velocity(self, write_to_file=True):
#         """compute magnitude of velocity vectors for all times and planes"""
#         if self.c is None:
#             # noinspection PyUnresolvedReferences
#             from h5rdmtoolbox.extensions import vector, magnitude
#             mode = 'r+' if write_to_file else 'r'
#             with h5tbx.File(self.filename, mode) as h5:
#                 vec = h5.Vector(u=self.velocity.x.name, v=self.velocity.y.name)[:]
#                 vec.magnitude.compute_from(self.velocity.x.basename, self.velocity.y.basename,
#                                            name='velocity_magnitude',
#                                            attrs={'standard_name': 'magnitude_of_velocity'})
#                 if write_to_file:
#                     if 'report' not in h5:
#                         h5.create_group('report')
#                     h5['report'].create_dataset_from_xarray_dataarray(vec.velocity_magnitude)
#                 return vec
#
#         # if self.ds_dict['cabs'] is None:
#         #     raise NotImplementedError('Compute cabs from u and v')
#         #     with h5tbx.File(self.filename) as h5:
#         #         u = self.ds_dict['u'][:]
#         #         v = self.ds_dict['u'][:]
#         #
#         # if self.data_cube_dim == 3:
#         #     return self.ds_dict['cabs'][:].average(axis=0)
#         # elif self.data_cube_dim == 4:
#         #     warnings.warn('May be very time and memory consuming!')
#         #     return self.ds_dict['cabs'][:].average(axis=1)
#
#     def plot_velocity_field(self,
#                             mean: bool = True,
#                             quiver: bool = True,
#                             contour: bool = True):
#         if not mean:
#             raise NotImplementedError('Only mean velocity implemented for now')
#         vec = self.compute_abs_velocity(write_to_file=False)
#         if self.c is None:
#             c = vec.velocity_magnitude
#         else:
#             c = self.c
#         if contour:
#             c[:].mean('time').plot()
#         if quiver:
#             vec.mean('time').plot.quiver('x', 'y', 'u', 'v')
