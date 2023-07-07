"""report module. piv reports are generated based on PIV HDF5 files.

The report is generated based on a certain convention!
"""

import logging

from . import monitor_points
from . import piv_vector
from . import utils

logger = logging.getLogger(__package__)
logger.setLevel('ERROR')

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


class PIVReport:
    """PIV report class. Interface to HDF5 file providing
    a high-level interface to the results.

    Examples
    --------
    Consider a multi plane measurement (multi plane packed into one file) of
    2D2C PIV data.
    We want to plot the 7th timestep of the 3rd plane:
    >>> piv_report = PIVReport
    >>> piv_report.velocity.isel(time=7, z=3)
    """

    def __init__(self, filename):
        self.filename = filename
        self.standard_name_identifier = {'flags': 'piv_flags'}
        self._monitor_points = monitor_points.MonitorPoints(self.coordinates.x,
                                                            self.coordinates.y)

    @property
    def coordinates(self):
        """PIV coordinates"""
        return piv_vector.PIVVector(self.filename, {'x': 'x_coordinate',
                                                    'y': 'y_coordinate',
                                                    'z': 'z_coordinate'})

    @property
    def displacement(self):
        """PIV displacement"""
        return piv_vector.PIVVector(self.filename, {'x': 'x_displacement',
                                                    'y': 'y_displacement',
                                                    'z': 'z_displacement'})

    @property
    def velocity(self):
        """Velocity Vector"""
        return piv_vector.PIVVector(self.filename, {'x': 'x_velocity',
                                                    'y': 'y_velocity',
                                                    'z': 'z_velocity',
                                                    'mag': 'magnitude_of_velocity'})

    @property
    def flags(self):
        return utils.get_dataset_by_standard_name(self.filename, self.standard_name_identifier['flags'])

    @property
    def mask(self) -> "PIVMask":
        from . import piv_mask
        return piv_mask.PIVMask(self.flags)

    @property
    def monitor_points(self):
        return self._monitor_points

# class Report(ReportItem):
#     """Report class"""
#
#     identifier = {'x': 'x_coordinate',
#                   'y': 'y_coordinate',
#                   'ix': 'x_pixel_coordinate',
#                   'iy': 'y_pixel_coordinate', }
#
#     def __init__(self, filename):
#         super().__init__(filename)
#         self._mask = None
#         self._seeding_points = None
#
#     @property
#     def x(self):
#         """x-velocity"""
#         return self.get_dataset_by_standard_name(self.identifier['x'])
#
#     @property
#     def y(self):
#         """y-velocity"""
#         return self.get_dataset_by_standard_name(self.identifier['y'])
#
#     @property
#     def ix(self):
#         """x-velocity"""
#         return self.get_dataset_by_standard_name(self.identifier['ix'])
#
#     @property
#     def iy(self):
#         """y-velocity"""
#         return self.get_dataset_by_standard_name(self.identifier['iy'])
#
#     @property
#     def fiwsize(self):
#         """alias for final interrogation window size"""
#         return self.final_interrogation_window_size
#
#     @property
#     def final_interrogation_window_size(self) -> Dict:
#         """final interrogation window size"""
#         return {'x': self.x_final_interrogation_window_size,
#                 'y': self.y_final_interrogation_window_size}
#
#     @property
#     def x_final_interrogation_window_size(self):
#         """final interrogation window size in x-direction"""
#         fiws = self.get_dataset_by_standard_name('x_final_interrogation_window_size')
#         if fiws is None:
#             return None
#         return fiws[()]
#
#     @property
#     def y_final_interrogation_window_size(self):
#         """final interrogation window size in y-direction"""
#         fiws = self.get_dataset_by_standard_name('y_final_interrogation_window_size')[()]
#         if fiws is None:
#             return None
#         return fiws[()]
#
#     @property
#     def x_final_interrogation_window_overlap_size(self):
#         """final interrogation window size in x-direction"""
#         fiwos = self.get_dataset_by_standard_name('x_final_interrogation_window_overlap_size')
#         if fiwos is None:
#             return None
#         return fiwos[()]
#
#     @property
#     def y_final_interrogation_window_overlap_size(self):
#         """final interrogation window size in y-direction"""
#         fiwos = self.get_dataset_by_standard_name('y_final_interrogation_window_overlap_size')[()]
#         if fiwos is None:
#             return None
#         return fiwos[()]
#
#     def is_plane(self):
#         return self.velocity.is_plane()
#
#     def is_snapshot(self):
#         return self.velocity.is_snapshot()
#
#     def is_mplane(self):
#         return self.velocity.is_mplane()
#
#     def is_2D2C(self):
#         return self.velocity.is_2D2C()
#
#     def is_2D3C(self):
#         return self.velocity.is_2D3C()
#
#     @property
#     def flags(self):
#         return self.get_dataset_by_standard_name('piv_flags')[()]
#
#     @property
#     def unique_flags(self):
#         return np.unique(self.velocity.flags[:])
#
#     def explain_flags(self) -> List[str]:
#         """Explain the flags"""
#         flag_arr = np.unique(self.velocity.flags[:])
#         flag_meaning = self.velocity.flags.attrs['flag_meaning']
#         flag_meaning = {int(k): v for k, v in flag_meaning.items()}
#         return explain_flags(flag_arr, flag_meaning)
#
#     def get_flag_statistic(self):
#         unique_flags = self.unique_flags
#         flags = self.flags
#         flag_meaning = self.velocity.flags.attrs['flag_meaning']
#         ntot = flags.size
#         out = {}
#         for u in unique_flags:
#             n = np.count_nonzero(flags == u)
#             out[u] = {'name': explain_flags(u, flag_meaning), 'count': n, 'percentage': n / ntot * 100}
#             print(f'{u}: {explain_flags(u, flag_meaning)} ({n}, {n / ntot * 100:.2f})')
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
#     def add_section(self, section):
#         self._sections.append(section(self))
#
#     @property
#     def software(self):
#         with h5tbx.File(self.filename) as h5:
#             return h5.attrs['software']
#
#     def info(self):
#         """return general information about the file"""
#         import pandas as pd
#         return pd.Series({'contact': self.contact,
#                           'software': self.software,
#                           'pivtype': self.pivtype,
#                           'fov': self.fov,
#                           'pivmethod': self.piv_method,
#                           'final_iw_size': [int(self.x_final_interrogation_window_size.values),
#                                             int(self.y_final_interrogation_window_size.values)],
#                           'final_ov_size': [int(self.x_final_interrogation_window_overlap_size.values),
#                                             int(self.y_final_interrogation_window_overlap_size.values)],
#                           })
#
#     @property
#     def piv_method(self):
#         pm = self.get_dataset_by_standard_name('piv_method')
#         if pm is None:
#             return 'unknown'
#         return pm[()]
#
#     @property
#     def contact(self):
#         with h5tbx.File(self.filename) as h5:
#             return h5.attrs['contact']
#
#     @property
#     def displacement(self):
#         return Displacement(self.filename)
#
#     @property
#     def velocity(self):
#         return Velocity(self.filename)
#
#     @property
#     def fov(self):
#         return FOV(self.filename)
#
#     def create_notebook(self,
#                         target_folder: pathlib.Path = None,
#                         execute_notebook=False,
#                         notebook_filename: pathlib.Path = None,
#                         overwrite: bool = False,
#                         inplace: bool = False,
#                         to_html: bool = False,
#                         to_pdf: bool = False,
#                         ):
#         self.notebook.create(target_folder, execute_notebook, notebook_filename, overwrite, inplace,
#                              to_html=to_html, to_pdf=to_pdf)
#
#     @property
#     def notebook(self):
#         """return a notebook object allowing to write a standard report on this PIV file"""
#         from .notebook.notebook import PIVReportNotebook
#         return PIVReportNotebook(self)
#
#     @property
#     def seeding_points(self):
#         if self._seeding_points is not None:
#             return self._seeding_points
#
#         logger.info('Seeding points are generated randomly based on settings.\n'
#                     'You may set user-defined seeding points by e.g. \n'
#                     '>>> report = spp.Report(piv_filename)'
#                     '\n>>> report.seeding_points = [(10, 41), (31, 13)]')
#         from .utils import generate_seeding_points
#         self._seeding_points = generate_seeding_points(self.mask,
#                                                        n=get_config('n_seeding_pts'),
#                                                        min_dist=get_config('min_seeding_point_distance'))
#         return self._seeding_points
#
#     @seeding_points.setter
#     def seeding_points(self, seeding_points: List[Tuple[int, int]]):
#         self._seeding_points = seeding_points
#
#     @property
#     def mask(self):
#         """return the mask of the PIV file"""
#         if self._mask is not None:
#             return self._mask
#         if self.is_plane():
#             _mask = self.displacement.x[0, :, :].piv_flags & 2
#         elif self.is_mplane():
#             _mask = self.displacement.x[0, 0, :, :].piv_flags & 2
#         else:
#             _mask = self.displacement.x[:, :].piv_flags & 2
#         self._mask = _mask != 0
#         return self._mask
