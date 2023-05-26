from xarray.plot import accessor


def contourf_and_quiver(self, contourf_variable: str = 'mag',
                        x='x', y='y',
                        u='u', v='v', every=2,
                        contourf_kwargs=None, quiver_kwargs=None):
    if contourf_kwargs is None:
        contourf_kwargs = {}
    if quiver_kwargs is None:
        quiver_kwargs = {}
    self._ds[contourf_variable].plot.contourf(**contourf_kwargs)

    color = quiver_kwargs.pop('color', 'k')
    self._ds.every(every).plot.quiver(x, y, u, v, color=color, **quiver_kwargs)


# make the function available as a method of the accessor
accessor.DatasetPlotAccessor.contourf_and_quiver = contourf_and_quiver
