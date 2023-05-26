def calc_dwdz(dudx, dvdy):
    """
    Calculates dwdz from solving continuity equation:
        div(v) = 0
    This is only valid for incompressible flows (=0 on right side of equation)!

    Parameters
    ----------
    dudx : `array_like`
    dvdy : `array_like`

    Returns
    -------
    dwdz : `array_like`
    """
    return -dudx[:] - dvdy[:]
