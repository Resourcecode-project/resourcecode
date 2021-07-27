#!/usr/bin/env python3
# coding: utf-8

from scipy.constants import g
from scipy.optimize import minimize
import numpy as np


def dispersion(
    frequencies: np.ndarray,
    depth: float = float("inf"),
    n_iter: int = 200,
    tol: float = 1e-6,
) -> np.ndarray:
    """Compute the dispersion relation of waves
        Find *k* s.t. (2.pi.f)^2 = g.k.tanh(k.d)

    Parameters
    ----------

    freq:
        the frequency vector
    depth:
        the depth
    n_iter:
        the maximum number of iterations in the non linear solver algorithm.
    tol:
        Tolerance for termination. When tol is specified, the selected
        minimization algorithm sets some relevant solver-specific tolerance(s)
        equal to tol. For detailed control, use solver-specific options.

    Returns
    -------

    out: the wave numbers (same size as freq)

    Example
    -------

    .. doctest:

        >>> import pylab as p
        >>> from resourcecode.spectrum import dispersion
        >>> freq = p.arange(0, 1, 0.01)
        >>> k1 = dispersion(freq, depth=1)
        >>> k10 = dispersion(freq, depth=10)
        >>> kInf = dispersion(freq, depth=float("inf"))
        >>> p.plot(freq, k1)
        >>> p.plot(freq, k10)
        >>> p.plot(freq, kInf)
        >>> p.show()

    """

    frequencies = np.array(frequencies)
    infinite_depth_dispersion = (4 * np.pi ** 2 / g) * frequencies ** 2

    if not np.isfinite(depth):
        return infinite_depth_dispersion

    def to_minimize(k):
        return sum(((2 * np.pi * frequencies) ** 2 - g * k * np.tanh(k * depth)) ** 2)

    result = minimize(
        to_minimize,
        x0=infinite_depth_dispersion,
        tol=tol,
        options={"maxiter": n_iter},
    )
    if result.success:
        return result.x

    raise ValueError(result.message)