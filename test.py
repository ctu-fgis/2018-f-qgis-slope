import fiona
import rasterio
from shapely.geometry import LineString, Point, shape, mapping
from pprint import pprint
from fiona.crs import from_epsg

def interpolatePoints(line, lenghtOfSegment):

    # preparations

    # distance counter
    tmpDistance = 0

    # array of output points
    outputPoints = []

    length = line.length

    point = None
    while tmpDistance <= length:
        point = line.interpolate(tmpDistance)
        outputPoints.append(point)
        tmpDistance += lenghtOfSegment  # == tmpDistance = tmpDistance + lengthOfSegment

    outputPoints.append(point)
    return outputPoints


raster_loc = r"C:\Users\patmic\Desktop\CVZ_CVUT\Free_software_gis\Data\DTM\krnap_dtm_5m\krnap_dtm_5mtif.tif"
raster = rasterio.open(raster_loc)
#print(raster.crs, raster.driver)

vector_loc = r"C:\Users\patmic\Desktop\CVZ_CVUT\Free_software_gis\Data\silnice_clip_krnapII.shp"
vector = fiona.open(vector_loc, "r")

lenghtOfSegment = 15

vector_output = r"C:\Users\patmic\Desktop\CVZ_CVUT\Free_software_gis\Data\silnice_clip_krnapII_output.shp"
schema={
  'geometry': 'Point',
  'properties': {
      'X':'float',
      'Y': 'float'}}
with fiona.open(vector_output, 'w',crs=from_epsg(5514),driver='ESRI Shapefile', schema=schema) as output:

    for feature in vector:
        line = shape(feature["geometry"])

        # there are some geometries of type MultiLineString, which i am throwing away for now
        if line.type == 'LineString':
            points = interpolatePoints(line, lenghtOfSegment)
            for point in points:
                prop = {'X': float(point.x), 'Y': float(point.y)}
                output.write({'geometry': mapping(point), 'properties': prop})