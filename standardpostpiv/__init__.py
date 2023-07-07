import xarray as xr

from standardpostpiv._cfg import set_config, get_config
from . import _logging
from . import plotting
from . import standardplots
from . import utils
from . import xr_accessors
from ._version import __version__
# from .report import Report
from .report import PIVReport
from .statistics import stats

xr.set_options(keep_attrs=True)
core_logger = _logging.create_package_logger('standardpostpiv')
_logging.set_loglevel(core_logger, 'DEBUG')

__all__ = ['__version__', 'set_config', 'get_config', ]
