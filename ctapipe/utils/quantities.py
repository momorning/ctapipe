from astropy.units import Quantity

def all_to_value(*args, unit):
    '''converts all args to value if convertible to the same unit.

    - does not copy the data
    - the unit returned, will be the one of the 1st arg
    - makes sure all args are convertible to the same unit
    - return the values of all args and the unit
    - Raise a meaningful error in case the args are not of a convertible unit.

    Returns: *args_without_unit
    '''
    return tuple(
        Quantity(arg, copy=False).to_value(unit)
        for arg in args
    )