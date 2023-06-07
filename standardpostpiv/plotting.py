import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display
from typing import Union

from .flags import explain_flags


def simple_dropdown_plot(dropdown_values, func, initial_value, *args, **kwargs):
    dropdown = widgets.Dropdown(options=['None', *dropdown_values], description='Mask Threshold:')
    out = widgets.Output()

    # Define the plot function
    def update_plot(*args, **kwargs):
        with out:
            out.clear_output()
            func(*args, **kwargs)
            plt.show()

    # Register the callback function on dropdown value change
    dropdown.observe(lambda change: update_plot(*args, **kwargs, mark_flag=change.new), 'value')

    vbox = widgets.VBox([dropdown, out, ])

    # Display the dropdown widget
    display(vbox)

    # Initial plot
    with out:
        func(*args, **kwargs, mark_flag=initial_value)
        plt.show()


def interactive_contourf_and_quiver(dataset,
                                    contourf_variable: str = 'mag',
                                    x='x', y='y',
                                    u='u', v='v', every=2,
                                    contourf_kwargs=None,
                                    quiver_kwargs=None):
    fig, ax = plt.subplots()
    contourf_and_quiver(dataset, contourf_variable, x, y, u, v, every, contourf_kwargs, quiver_kwargs, ax=ax)


def contourf_and_quiver(dataset,
                        contourf_variable: str = 'mag',
                        x='x', y='y',
                        u='u', v='v', every=2,
                        contourf_kwargs=None,
                        quiver_kwargs=None,
                        ax=None,
                        mark_flag: Union[None, int] = None):
    """plot contourf and quiver in one plot"""
    if contourf_kwargs is None:
        contourf_kwargs = {}
    if quiver_kwargs is None:
        quiver_kwargs = {}
    dataset[contourf_variable].plot.contourf(ax=ax, **contourf_kwargs)

    if ax is None:
        ax = plt.gca()

    _ = dataset.every(every).plot.quiver(x, y, u, v, color=quiver_kwargs.pop('color', 'k'), **quiver_kwargs, ax=ax)

    if mark_flag is None or mark_flag == 'None':
        return ax

    if isinstance(mark_flag, str):
        mark_flag = int(mark_flag.split('-')[0])

    flags = dataset['flags']
    flag_meaning = flags.attrs['flag_meaning']

    mask_name = '_'.join(explain_flags(mark_flag, flag_meaning))
    dataset.where(flags == mark_flag).every(every).plot.quiver(x, y, u, v,
                                                               color='r',
                                                               **quiver_kwargs,
                                                               ax=ax,
                                                               label=mask_name)

    ax.legend()
    ax.legend(loc='center left', bbox_to_anchor=(1.4, 0.5))
    return ax
