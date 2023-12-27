import math
from pyproj import Transformer
import json
from shapely.geometry import shape
from shapely import from_geojson
from shapely.geometry.polygon import Polygon
from tilematrix import Tile, TilePyramid

geos = """{
  "id": "4187b9f5-0aee-497e-b21d-a67451ecc2c6",
  "pk": "",
  "name": "unsaved trip",
  "type": "trip",
  "access": "public",
  "bboxPolygon": {
    "type": "Feature",
    "bbox": [
      null,
      null,
      null,
      null
    ],
    "properties": {},
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            null,
            null
          ],
          [
            null,
            null
          ],
          [
            null,
            null
          ],
          [
            null,
            null
          ],
          [
            null,
            null
          ]
        ]
      ]
    }
  },
  "events": {
    "pre": [],
    "during": [],
    "post": []
  },
  "featureCollection": {
    "type": "FeatureCollection",
    "features": [
      {
        "id": "581486ab552bc6495318301f65570213",
        "type": "Feature",
        "properties": {
          "isRoute": true,
          "name": "route 1",
          "color": "#ff0000",
          "isVisible": true,
          "length": 387.73835,
          "colorOuter": "#FFFFFF",
          "speed": 6,
          "departureTime": "2023-12-26T17:57:21.000Z",
          "arrivalTime": "2023-12-29T10:34:44.008Z"
        },
        "geometry": {
          "coordinates": [
            [
              -122.6223,
              48.39416
            ],
            [
              -124.79846,
              48.49026
            ],
            [
              -125.00316,
              47.39116
            ],
            [
              -124.3922,
              46.79512
            ],
            [
              -122.18454,
              46.89421
            ],
            [
              -121.87906,
              47.85601
            ],
            [
              -122.58451,
              48.34604
            ]
          ],
          "type": "LineString"
        }
      }
    ],
    "bbox": [
      null,
      null,
      null,
      null
    ]
  },
  "routeCount": 1,
  "routesTotalLength": 387.73835,
  "routesTotalDurationInDays": 2.69263,
  "markerCount": 0,
  "trackCount": 0,
  "tracksTotalLength": 0
}"""

geo = json.loads(geos)
fc = geo["featureCollection"]
feature = fc["features"][0]
polygon: Polygon = shape(feature["geometry"])

# kk = from_geojson(fc)



lon = 95.99
lat = 15.15

t4326 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
utm = t4326.transform(lon, lat)
print (utm)

t3857 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
lonlat = t3857.transform(utm[0], utm[1])
print (lonlat)

xx = list(map(lambda p:p[0], polygon.coords))
yy = list(map(lambda p:p[1], polygon.coords))

mm = t4326.transform(xx, yy)
meters = list(zip(mm[0], mm[1]))
polym = Polygon(meters)

tp = TilePyramid("mercator")
tiles = tp.tiles_from_geom(polym, 5)
for tile in tiles:
    print (tile)







