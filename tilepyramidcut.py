#!/usr/bin/env python3
"""
Prunes and copies portions of a tile pyramid such as one used in Google Earth or Mapbox.
The boundary polygon can be defined in DeepZoom (www.deepzoom.com) as one or more routes.
The routes will be converted to shapely Polygons and used as bondaries for the prune or
copy operation.
"""

__author__ = "Jay Borseth"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import json
import os
import shutil

import numpy as np
from logzero import logger
from pyproj import Transformer
from shapely import from_geojson
from shapely.geometry import MultiPolygon, Polygon, shape

from tilematrix import Tile, TilePyramid


def dir_is_empty(path):
  """ returns True if diretory exists and is empty, False if not empty, and None if doesn't exist """
  if os.path.isdir(path):
    with os.scandir(path) as it:
      if any(it):
        return False
      return True
  return None


def dir_delete_if_empty(args, tp: TilePyramid, tile: Tile, path: str):
  """ Delete the directory if empty, and walk up the pyramid recursively deleting any empty ancestor directories.
   return True if directory was deleted """
  if os.path.isdir(path):
    with os.scandir(path) as it:
      if not any(it):
        # dir is empty
        os.rmdir(path)
        # recursively walk up the pyramid checking if parent is empty
        parent = tile.get_parent()
        if parent and parent.zoom >= args.zbegin:
          parent_path = tuple_to_path(args.src, parent)
          parent_dir = os.path.dirname(parent_path)
          while dir_delete_if_empty(args, tp, parent, parent_dir):
            return True
  return False


def tuple_to_path (root, zyx):
  """ Given a root directory and a zyx tuple, create the .png path """
  z, y, x = zyx
  full = os.path.join(root, f"Z{z}/{y}/{x}.png")
  return full


def geojson_to_multipolygon (path):
  """ Given a JSON file containing containing LatLng LINESTIRNGS OR POLYGONS,
  as either a DeepZoom feature list or else a normal geojson feature list, 
  convert it to a shapely multipolygon in ESPG:3857 (UTM meters) units."""
  with open(path, "r") as read_file:
    geo = json.load(read_file)
    if "featureCollection" in geo:
        # geojson is embedded in a DeepZoom trip
        featureCollection = geo["featureCollection"]
    else:
      # regular geoson
      featureCollection = geo
    features = featureCollection["features"]

    t4326 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    allPolygons = []
    for feature in features:
      xx = list(map(lambda p:p[0], feature["geometry"]["coordinates"]))
      yy = list(map(lambda p:p[1], feature["geometry"]["coordinates"]))
      # following not needed: shapely autoconverts LINESTRING to POLYGON
      # xx.append(xx[0])
      # yy.append(yy[0])
      mxx, myy = t4326.transform(xx, yy)

      meters = [(i, j) for i, j in zip(mxx, myy)]  

      # print (meters)
      polym = Polygon(meters)
      allPolygons.append(polym)

    multiPolygon = MultiPolygon(allPolygons)
    return multiPolygon


def test (args):
  """ LatLng to UTM and back """
  tp = TilePyramid("mercator")

  lon = 95.99
  lat = 15.15

  t4326 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
  utm = t4326.transform(lon, lat)
  print (utm)

  t3857 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
  lonlat = t3857.transform(utm[0], utm[1])
  print (lonlat)


def op(args):
  """ The point of it all """
  tp = TilePyramid("mercator")

  multiPolygon = geojson_to_multipolygon(args.polyfile)

  for zoom in range(args.zbegin, args.zend+1):
    tiles = tp.tiles_from_geom(multiPolygon, zoom)  
    for tile in tiles:
      src_path = tuple_to_path(args.src, tile)

      if os.path.isfile(src_path):
        if args.op == "prune":
          print ("prune: ", src_path)
          os.remove(src_path)
          dir_path = os.path.dirname(src_path)
          dir_delete_if_empty(args, tp, tile, dir_path)
        elif args.op == "copy":
          dst_path = tuple_to_path(args.dst, tile)
          dst_dir = os.path.dirname(dst_path)
          os.makedirs(dst_dir, exist_ok = True)
          shutil.copy2(src_path, dst_path)
      else:
        print (src_path)


def main(args):
    logger.info("tilepyramidcut")
    
    if not os.path.isdir(args.src):
        logger.error (f"Source directory (--src) {args.src} does not exist")

    if not os.path.isfile(args.polyfile):
        logger.error (f"Polygon file (--polyfile) {args.polyfile} does not exist")

    # "prune" doesn't use a dst directory, but copy requires one
    if args.op == "copy" and not os.path.isdir(args.dst):
        logger.error (f"Destination directory (--dst) {args.src} does not exist")

    logger.info(args)

    op(args)

    logger.info("completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("--src", help="source directory to process", dest="src", required=True)
    parser.add_argument("--dst", action="store", dest="dst", help="destination directory for copy op")
    parser.add_argument("--polyfile", action="store", dest="polyfile", required=True, type=str, help="json file containing geojson geometry of Polygon(s) to prune or copy")
    parser.add_argument("--op", action="store", choices=["prune", "copy"], required=True, help="the operation to perform")
    parser.add_argument("--zbegin", action="store", dest="zbegin", required=True, type=int, help= "start zoom")
    parser.add_argument("--zend", action="store", dest="zend", required=True, type=int, help="end zoom")
    
    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)