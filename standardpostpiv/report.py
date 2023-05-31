"""report module. piv reports are generated based on PIV HDF5 files.

The report is generated based on a certain convention!
"""

import h5rdmtoolbox as h5tbx
import pathlib

from .core import ReportItem
from .displacement import Displacement
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
    def fiwsize(self):
        """alias for final interrogation area"""
        return self.final_interrogation_window_size

    @property
    def final_interrogation_window_size(self):
        """final interrogation area"""
        return self.get_dataset_by_standard_name('final_interrogation_window_size')

    def is_plane(self):
        return self.velocity.is_plane()

    def is_snapshot(self):
        return self.velocity.is_snapshot()

    def is_mplane(self):
        return self.velocity.is_mplane()

    def is_2D2C(self):
        return self.velocity.is_2D2C()

    def is_2D3C(self):
        return self.velocity.is_2D3C()

    @property
    def pivtype(self) -> str:
        if self.is_2D2C():
            piv_dtype = '2D2C'
        elif self.is_2D3C():
            piv_dtype = '2D3C'
        else:
            piv_dtype = '?D?C'

        if self.is_plane():
            piv_dtype += ' (Plane)'
        elif self.is_mplane():
            piv_dtype += ' (Multi-Plane)'
        elif self.is_snapshot():
            piv_dtype += ' (Snapshot)'
        else:
            piv_dtype += ' (Unknown)'
        return piv_dtype

    def add_section(self, section):
        self._sections.append(section(self))

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
    def displacement(self):
        return Displacement(self.filename)

    @property
    def velocity(self):
        return Velocity(self.filename)

    @property
    def fov(self):
        return FOV(self.filename)

    def create_notebook(self,
                        target_folder: pathlib.Path = None,
                        execute_notebook=False,
                        notebook_filename: pathlib.Path = None,
                        overwrite: bool = False,
                        inplace: bool = False,
                        to_html: bool = False,
                        to_pdf: bool = False,
                        ):
        self.notebook.create(target_folder, execute_notebook, notebook_filename, overwrite, inplace,
                             to_html=to_html, to_pdf=to_pdf)

    @property
    def notebook(self):
        """return a notebook object allowing to write a standard report on this PIV file"""
        from .notebook.notebook import PIVReportNotebook
        return PIVReportNotebook(self)
