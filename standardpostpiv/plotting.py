

def contourf_and_quiver(dataset,
                        contourf_variable: str = 'mag',
                        x='x', y='y',
                        u='u', v='v', every=2,
                        contourf_kwargs=None,
                        quiver_kwargs=None,
                        ax=None):
    """plot contourf and quiver in one plot"""
    if contourf_kwargs is None:
        contourf_kwargs = {}
    if quiver_kwargs is None:
        quiver_kwargs = {}
    dataset[contourf_variable].plot.contourf(ax=ax, **contourf_kwargs)

    color = quiver_kwargs.pop('color', 'k')
    return dataset.every(every).plot.quiver(x, y, u, v, color=color, **quiver_kwargs, ax=ax)


