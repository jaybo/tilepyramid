"""Tile geometries and tiles from geometries."""

from types import GeneratorType

# import pytest
from shapely.geometry import Point, Polygon, shape

from tilematrix import Tile, TilePyramid


def test_top_left_coord():
    """Top left coordinate."""
    # tp = TilePyramid({
    #     "shape": (1, 1),  # tile rows and columns at zoom level 0
    #     "bounds": (-180.0, -85.051129, 180.0, 85.051129),  # pyramid bounds in pyramid CRS
    #     "is_global": True,  # if false, no antimeridian handling
    #     "srs": {"epsg": 4326},  # EPSG code for CRS
    # })

    tp = TilePyramid("mercator")

    tile = tp.tile(5, 3, 3)
    #tile = tp.tile(1, 0, 0)
    print(tile.bounds())
    print(tile.left, tile.bottom, tile.right, tile.top )

    tp = TilePyramid("geodetic")
    tile = tp.tile(5, 3, 3)
    assert tile.bounds() == (-163.125, 67.5, -157.5, 73.125)

test_top_left_coord()