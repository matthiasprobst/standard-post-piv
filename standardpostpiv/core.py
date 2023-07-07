import h5rdmtoolbox as h5tbx
import pathlib

from . import utils


class ReportItem:
    """Report class"""

    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self._tmp_filename = None

    @property
    def tmp_filename(self):
        if self._tmp_filename is None:
            self._tmp_filename = h5tbx.generate_temporary_filename(prefix='standardpostpiv_report_',
                                                                   suffix='.hdf', touch=True)
        return self._tmp_filename

    def get_dataset_by_standard_name(self, sn):
        """returns lazy object. See `h5rdmtoolbox.database.lazy`.
        Searches in original file and if none found in temporary file"""
        return utils.get_dataset_by_standard_name(self.filename, sn, self.tmp_filename)
