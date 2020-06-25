"""A suite of decay functions to simulate demand dropoff as distance increases.

All decay functions operate on one-dimensional numpy arrays.
"""
# TODO: Add the standard gravity decay function d**(-beta).
# TODO: Add linear decay (or other polynomial interpolation).
import math

import numpy as np

# ADDED BY ESDC
def negative_power_decay(distance_array, beta): 
    return distance_array ** -beta

def exponential_decay(distance_array, beta): 
    return np.exp(-beta * distance_array)

def parabolic_decay(distance_array, scale):
    """
    Transform a measurement array using the Epanechnikov (parabolic) kernel.

    Some sample values. Measurements are in multiple of ``scale``; decay value are in fractions of
    the maximum value:

    +---------------+---------------+
    | measurement   | decay value   |
    +===============+===============+
    | 0.0           | 1.0           |
    +---------------+---------------+
    | 0.25          | 0.9375        |
    +---------------+---------------+
    | 0.5           | 0.75          |
    +---------------+---------------+
    | 0.75          | 0.4375        |
    +---------------+---------------+
    | 1.0           | 0.0           |
    +---------------+---------------+
    """
    return np.maximum(
        (scale**2 - distance_array**2) / scale**2,
        np.zeros(shape=distance_array.shape)
    )


def gaussian_decay(distance_array, sigma):
    """
    Transform a measurement array using a normal (Gaussian) distribution.

    Some sample values. Measurements are in multiple of ``sigma``; decay value are in fractions of
    the maximum value:

    +---------------+---------------+
    | measurement   | decay value   |
    +===============+===============+
    | 0.0           | 1.0           |
    +---------------+---------------+
    | 0.7582        | 0.75          |
    +---------------+---------------+
    | 1.0           | 0.60647       |
    +---------------+---------------+
    | 1.17          | 0.5           |
    +---------------+---------------+
    | 2.0           | 0.13531       |
    +---------------+---------------+
    """
    return np.exp(-distance_array**2 / sigma)


def raised_cosine_decay(distance_array, scale):
    """
    Transform a measurement array using a raised cosine distribution.

    Some sample values. Measurements are in multiple of ``scale``; decay value are in fractions of
    the maximum value:

    +---------------+---------------+
    | measurement   | decay value   |
    +===============+===============+
    | 0.0           | 1.0           |
    +---------------+---------------+
    | 0.25          | 0.853553      |
    +---------------+---------------+
    | 0.5           | 0.5           |
    +---------------+---------------+
    | 0.75          | 0.146447      |
    +---------------+---------------+
    | 1.0           | 0.0           |
    +---------------+---------------+
    """
    masked_array = np.clip(a=distance_array, a_min=0.0, a_max=scale)
    return (1.0 + np.cos((masked_array / scale) * math.pi)) / 2.0


def uniform_decay(distance_array, scale):
    """
    Transform a measurement array using a uniform distribution.

    The output is 1 below the scale parameter and 0 above it.

    Some sample values. Measurements are in multiple of ``scale``; decay value are in fractions of
    the maximum value:

    +---------------+---------------+
    | measurement   | decay value   |
    +===============+===============+
    | 0.0           | 1.0           |
    +---------------+---------------+
    | 0.25          | 1.0           |
    +---------------+---------------+
    | 0.5           | 1.0           |
    +---------------+---------------+
    | 0.75          | 1.0           |
    +---------------+---------------+
    | 1.0           | 1.0           |
    +---------------+---------------+
    """
    return (distance_array <= scale).astype(np.float64)


def get_decay_function(name):
    """
    Return the decay function with the given name.

    Parameters
    ----------
    name : str
        The name of the requested decay function.

        Available names:
            - ``'uniform'``
            - ``'raised_cosine'``
            - ``'gaussian'``
            - ``'parabolic'``

    """
    return NAME_TO_FUNCTION_MAP[name.lower()]


NAME_TO_FUNCTION_MAP = {
    'negative_power': negative_power_decay,
    'exponential': exponential_decay,
    'uniform': uniform_decay,
    'raised_cosine': raised_cosine_decay,
    'gaussian': gaussian_decay,
    'parabolic': parabolic_decay,
    'epanechnikov': parabolic_decay
}
