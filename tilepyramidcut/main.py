#!/usr/bin/env python3
"""
Prunes and copies portions of a tile pyramid such as one used in Google Earth or Mapbox.
"""

__author__ = "Jay Borseth"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import os
from logzero import logger
from _funcs import geojson_to_multipolygon, op


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("--src", help="source directory to process")
    parser.add_argument("--dst", action="store", dest="dst", help="destination directory for copy op")
    parser.add_argument("--polyfile", action="store", dest="polyfile", required=True, type=str, help="json file containing geojson geometry of Polygon(s) to prune or copy")
    parser.add_argument("--op", action="store", choices=["prune", "copy"], required=True, help="the operation to perform")
    parser.add_argument("--zbegin", action="store", dest="zbegin", required=True, type=int, help= "start zoom")
    parser.add_argument("--zend", action="store", dest="zend", required=True, type=int, help="end zoom NOT INCLUSIVE")
    
    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)