"""report module. piv reports are generated based on PIV HDF5 files.

The report is generated based on a certain convention!
"""
import logging
import pathlib
from typing import Union, Dict

import h5rdmtoolbox as h5tbx
import pandas as pd

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

from .utils import HDF5StandardInterface


class PIVReport(HDF5StandardInterface):
    def __init__(self,
                 hdf_filename,
                 source_group: str = '/'):
        super().__init__(hdf_filename=hdf_filename, source_group=source_group)

    def is_2D2C(self):
        """check if the PIV data is 2D2C"""
        return len(self.velocity) == 2 and len(self.coordinate.shape) == 2

    @property
    def notebook(self):
        """return a notebook object allowing to write a standard report on this PIV file"""
        from .notebook.notebook import PIVReportNotebook
        return PIVReportNotebook(self)

    def is_snapshot(self) -> bool:
        return self.coordinate.z.ndim == 0 and self.time.ndim == 0

    def is_plane(self) -> bool:
        return self.coordinate.z.ndim == 0 and self.time.ndim == 1

    def is_multiplane(self) -> bool:
        return self.coordinate.z.ndim == 1 and self.time.ndim == 1


class _PIVReport:
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

    def __init__(self, filename: Union[str, pathlib.Path]):
        self.filename = pathlib.Path(filename)
        self.standard_name_identifier = {'flags': 'piv_flags'}
        self._monitor_points = monitor_points.MonitorPoints(self.coordinates.x,
                                                            self.coordinates.y)
        self.attributes = {'software': 'software',
                           'contact': 'contact',
                           }
        self._attrs = None

    def __getattr__(self, item):
        if item in self.attributes:
            return self.attrs[self.attributes[item]]
        return super().__getattribute__(item)

    def __repr__(self):
        return f'<{self.__class__.__name__} ({self.filename})>'

    @property
    def piv_method(self):
        pm = utils.get_dataset_by_standard_name(self.filename, 'piv_method')
        if pm is None:
            return 'unknown'
        return pm[()]

    @property
    def attrs(self) -> Dict:
        """Return the root attributes of the HDF5 file as dictionary"""
        if self._attrs is None:
            with h5tbx.File(self.filename) as h5:
                self._attrs = dict(h5.attrs)
        return self._attrs

    @property
    def piv_type(self) -> str:
        """Return the PIV type of the measurement"""
        if self.is_2D2C():
            piv_dtype = '2D2C'
        elif self.is_2D3C():
            piv_dtype = '2D3C'
        else:
            piv_dtype = '?D?C'

        if self.is_plane():
            piv_dtype += ' (Plane)'
        elif self.is_multiplane():
            piv_dtype += ' (Multi-Plane)'
        elif self.is_snapshot():
            piv_dtype += ' (Snapshot)'
        else:
            piv_dtype += ' (Unknown)'
        return piv_dtype

    @property
    def notebook(self):
        """return a notebook object allowing to write a standard report on this PIV file"""
        from .notebook.notebook import PIVReportNotebook
        return PIVReportNotebook(self)

    @property
    def n_planes(self):
        if self.coordinates.z.ndim == 0:
            return 1
        return self.coordinates.z.size

    @property
    def n_timesteps(self):
        if self.coordinates.time.ndim == 0:
            return 1
        return self.coordinates.time.size

    @property
    def shape(self):
        """return the shape of the PIV data"""
        return self.velocity.x.shape

    def is_multiplane(self):
        """check if the PIV data is multiplane"""
        return self.coordinates.z[()].ndim == 1 and self.coordinates.time.ndim == 1

    def is_2D2C(self):
        """check if the PIV data is 2D2C"""
        try:
            self.velocity.z
            return False
        except ValueError:
            return True

    def is_2D3C(self):
        """check if the PIV data is 2D3C"""
        return not self.is_2D2C()

    @property
    def coordinates(self):
        """PIV coordinates (spatial and temporal)

        Available attributes:
            x: physical x-coordinate
            y: physical y-coordinate
            z: physical z-coordinate
            ix: pixel x-coordinate
            iy: pixel y-coordinate
            time: time coordinate
        """
        return piv_vector.PIVVector(self.filename, {'x': 'x_coordinate',
                                                    'y': 'y_coordinate',
                                                    'z': 'z_coordinate',
                                                    'ix': 'x_pixel_coordinate',
                                                    'iy': 'y_pixel_coordinate',
                                                    'time': 'time'})

    @property
    def displacement(self):
        """PIV displacement"""
        return piv_vector.PIVVector(self.filename, {'x': 'x_displacement',
                                                    'y': 'y_displacement',
                                                    'z': 'z_displacement',
                                                    'mag': 'magnitude_of_velocity'})

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

    def is_snapshot(self) -> bool:
        return self.coordinates.z.ndim == 0 and self.coordinates.time.ndim == 0

    def is_plane(self) -> bool:
        return self.coordinates.z.ndim == 0 and self.coordinates.time.ndim == 1

    def is_multiplane(self) -> bool:
        return self.coordinates.z.ndim == 1 and self.coordinates.time.ndim == 1

    def final_interrogation_window_size(self) -> dict:
        """final interrogation window size"""
        x_fiwsize = utils.get_dataset_by_standard_name(
            self.filename, 'x_final_interrogation_window_size')
        y_fiwsize = utils.get_dataset_by_standard_name(
            self.filename, 'y_final_interrogation_window_size')
        return {'x': x_fiwsize[()],
                'y': y_fiwsize[()]}

    @property
    def final_interrogation_window(self):
        return piv_vector.PIVNDData(self.filename, {'x': 'x_final_interrogation_window_size',
                                                    'y': 'y_final_interrogation_window_size'},
                                    return_lazy=False)

    @property
    def final_interrogation_window_overlap(self):
        return piv_vector.PIVNDData(self.filename, {'x': 'x_final_interrogation_window_overlap_size',
                                                    'y': 'y_final_interrogation_window_overlap_size'},
                                    return_lazy=False)

    def info(self) -> pd.Series:
        """return general information about the file"""
        return pd.Series({'contact': self.contact,
                          'software': self.software,
                          'pivtype': self.piv_type,
                          'pivmethod': self.piv_method,
                          'final_iw_size': [int(self.final_interrogation_window.x),
                                            int(self.final_interrogation_window.y)],
                          'final_ov_size': [int(self.final_interrogation_window_overlap.x),
                                            int(self.final_interrogation_window_overlap.y)],
                          })
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
