"""standardized plots such as:

- velocity field
- scatter plot of all velocities
- histogram of all velocities
- significance map and 2d graphs

"""
import h5py
import h5rdmtoolbox as h5tbx


def plot_velocity_field(h5):
    """plot the absolute velocity field including the vectors"""
    if not isinstance(h5, h5py.Group):
        with h5tbx.File(h5) as f:
            return plot_velocity_field(f)

    u = h5.find_one({'standard_name': 'x_velocity'})
    ndim = u.ndim
