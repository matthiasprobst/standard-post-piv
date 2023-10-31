"""package configuration"""
from typing import Dict

CONFIG = dict(cmap='viridis',
              n_seeding_pts=4,
              min_seeding_point_distance=4,
              )

_VALIDATORS = {
    'cmap': lambda x: isinstance(x, str),
    'n_seeding_pts': lambda x: isinstance(x, int),
    'min_seeding_point_distance': lambda x: isinstance(x, int)
}


class ConfigSetter:
    """Set the configuration parameters."""

    def __enter__(self):
        return

    def __exit__(self, *args, **kwargs):
        self._update(self.old)

    def __init__(self):
        self.old = {}

    def __call__(self, **kwargs):
        self.old = {}
        for k, v in kwargs.items():
            if k in _VALIDATORS and not _VALIDATORS[k](v):
                raise ValueError(f'PIV parameter {k} has invalid value: {v}')
            if k not in CONFIG:
                raise KeyError(f'Not a configuration key: {k}')
            self.old[k] = CONFIG[k]
        self._update(kwargs)

    def _update(self, options_dict: Dict):
        CONFIG.update(options_dict)


set_config = ConfigSetter()


def get_config(key=None):
    """Return the configuration parameters."""
    if key is None:
        return CONFIG
    else:
        return CONFIG[key]
