from .core import ReportItem


class FOV(ReportItem):
    identifier = {'x': 'x_coordinate',
                  'y': 'y_coordinate',
                  'z': 'z_coordinate',
                  'xpx': 'x_pixel_coordinate',
                  'ypy': 'y_pixel_coordinate',
                  }

    @property
    def x(self):
        return self.get_dataset_by_standard_name(self.identifier['x'])

    @property
    def y(self):
        return self.get_dataset_by_standard_name(self.identifier['y'])

    @property
    def z(self):
        return self.get_dataset_by_standard_name(self.identifier['z'])

    @property
    def extent(self):
        return [[float(ds[()].min()), float(ds[()].max())] for ds in [self.x, self.y, self.z]]

    def __repr__(self):
        return f'FOV(extent={self.extent})'


