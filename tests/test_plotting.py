import unittest

import matplotlib.pyplot as plt
import numpy as np

from standardpostpiv import plotting


class TestPlotting(unittest.TestCase):
    """Tests plotting module"""

    def test_piv_scatter(self):
        """Not a real unittest. Check result manually!"""
        u = np.random.rand(10, 10)
        v = np.random.rand(10, 10)
        fig, axs = plotting.subplots(1, 3)
        ax = plotting.piv_scatter(u, v, ax=axs[0])
        plt.show()
