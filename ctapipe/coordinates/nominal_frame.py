'''
The code in this module is basically a copy of
http://docs.astropy.org/en/stable/_modules/astropy/coordinates/builtin_frames/skyoffset.html

We are just not creating a metaclass and a factory but directly building the
corresponding class.
'''
from astropy.coordinates.matrix_utilities import (
    rotation_matrix,
    matrix_product,
    matrix_transpose,
)
from astropy.coordinates import (
    frame_transform_graph,
    FunctionTransform,
    DynamicMatrixTransform,
    SphericalRepresentation,
    SphericalCosLatDifferential,
    BaseCoordinateFrame,
    CoordinateAttribute,
    TimeAttribute,
    EarthLocationAttribute,
)

from .horizon_frame import HorizonFrame


class NominalFrame(BaseCoordinateFrame):
    """
    Telescope coordinate frame.

    Cartesian system describing the angular offset of a given position in reference
    to the pointing direction of a given telescope.

    This makes use of small angle approximations of the position of interest and
    the pointing direction.

    Frame attributes:

    * ``origin``
        Coordinate of the telescope pointing in HorizonFrame
    * ``obstime``
        Observation time
    * ``location``
        Location of the telescope
    """
    default_representation = SphericalRepresentation
    default_differential = SphericalCosLatDifferential

    origin = CoordinateAttribute(default=None, frame=HorizonFrame)

    obstime = TimeAttribute(default=None)
    location = EarthLocationAttribute(default=None)


@frame_transform_graph.transform(FunctionTransform, NominalFrame, NominalFrame)
def skyoffset_to_skyoffset(from_telescope_coord, to_telescope_frame):
    """Transform between two skyoffset frames."""

    intermediate_from = from_telescope_coord.transform_to(
        from_telescope_coord.origin
    )
    intermediate_to = intermediate_from.transform_to(
        to_telescope_frame.origin
    )
    return intermediate_to.transform_to(to_telescope_frame)


@frame_transform_graph.transform(DynamicMatrixTransform, HorizonFrame, NominalFrame)
def reference_to_skyoffset(reference_frame, telescope_frame):
    """Convert a reference coordinate to an sky offset frame."""

    # Define rotation matrices along the position angle vector, and
    # relative to the origin.
    origin = telescope_frame.origin.spherical
    mat1 = rotation_matrix(-telescope_frame.rotation, 'x')
    mat2 = rotation_matrix(-origin.lat, 'y')
    mat3 = rotation_matrix(origin.lon, 'z')
    return matrix_product(mat1, mat2, mat3)


@frame_transform_graph.transform(DynamicMatrixTransform, NominalFrame, HorizonFrame)
def skyoffset_to_reference(skyoffset_coord, reference_frame):
    """Convert an sky offset frame coordinate to the reference frame"""

    # use the forward transform, but just invert it
    R = reference_to_skyoffset(reference_frame, skyoffset_coord)
    # transpose is the inverse because R is a rotation matrix
    return matrix_transpose(R)