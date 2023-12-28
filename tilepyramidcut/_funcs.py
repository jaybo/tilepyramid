import math
from pyproj import Transformer
import json
from shapely.geometry import shape
from shapely import from_geojson
from shapely.geometry import Polygon, MultiPolygon 
from tilematrix import Tile, TilePyramid
import numpy as np
import os, sys
import shutil


def dir_is_empty(path):
  """ returns True if diretory exists and is empty, False if not empty, and None if doesn't exist """
  if os.path.isdir(path):
    with os.scandir(path) as it:
      if any(it):
        return False
      return True
  return None


def dir_delete_if_empty(path):
  """ Delete the directory if empty """
  if os.path.isdir(path):
    with os.scandir(path) as it:
      if not any(it):
        os.rmdir(path)


def tuple_to_path (root, zyx):
  """ Given a root directory and a zyx tuple, create the .png path """
  z, y, x = zyx
  full = os.path.join(root, f"Z{z}/{y}/{x}.png")
  return full


def geojson_to_multipolygon (path):
  """ Given a JSON file containing a DeepZoom feature list of one or more LineStrings, convert it to a shapely multipolygon"""
  with open(path, "r") as read_file:
    geo = json.load(read_file)
    featureCollection = geo["featureCollection"]
    features = featureCollection["features"]

    t4326 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    allPolygons = []
    for feature in features:
      xx = list(map(lambda p:p[0], feature["geometry"]["coordinates"]))
      yy = list(map(lambda p:p[1], feature["geometry"]["coordinates"]))
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

  for zoom in range(args.zbegin, args.zend):
    tiles = tp.tiles_from_geom(multiPolygon, zoom)  
    for tile in tiles:
      src_path = tuple_to_path(args.src, tile)
      print (src_path)
      if args.op == "prune":
        os.remove(src_path)
        dir_path = os.path.dirname(src_path)
        dir_delete_if_empty(dir_path)
      elif args.op == "copy":
        dst_path = tuple_to_path(args.dst, tile)
        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok = True)
        shutil.copy2(src_path, dst_path)




