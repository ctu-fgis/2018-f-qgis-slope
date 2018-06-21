import fiona
import rasterio
from shapely.geometry import LineString, Point, shape, mapping
from pprint import pprint
from fiona.crs import from_epsg

def prepareLine(line, lenghtOfSegment):
    points = list(line.coords)
    previousPoint = None
    outputPoints = []
    for p in points:
        point = Point(p[0], p[1])
        outputPoints.append(point)
        if previousPoint is not None:
            dst = previousPoint.distance(point)
            if dst >= lenghtOfSegment:
                additionsCnt = int(dst/lenghtOfSegment)
                dX = point.x - previousPoint.x
                dY = point.y - previousPoint.y
                additionsX = dX / additionsCnt
                additionsY = dY / additionsCnt
                for i in range (0, additionsCnt):
                    newX = previousPoint.x + additionsX*(i+1)
                    newY = previousPoint.y + additionsY*(i+1)
                    outputPoints.append(Point(newX,newY))
        previousPoint = point
    return outputPoints


def cutLine(line, lenghtOfSegment):

    # preparations

    # distance counter
    tmpDistance = 0

    # point n-1
    previousPoint = None

    # array of output points
    outputPoints = []

    # iterate through all points
    for point in line:
        # 1. increase tmpDistance and set previous point
        if previousPoint is None:
            previousPoint = point
            outputPoints.append(point)
        else:
            dst = previousPoint.distance(point)
            tmpDistance = tmpDistance + dst
            previousPoint = point

            # 2. add point to output list, if my limit was exceeded
            if tmpDistance >= lenghtOfSegment:
                outputPoints.append(point)
                tmpDistance=0


    # add last vertices to the output points
    verticesCount = len(line)
    outputPoints.append(line[verticesCount-1])
    return outputPoints


raster_loc = r"C:\Users\patmic\Desktop\CVZ_CVUT\Free_software_gis\Data\DTM\krnap_dtm_5m\krnap_dtm_5mtif.tif"
raster = rasterio.open(raster_loc)
#print(raster.crs, raster.driver)

vector_loc = r"C:\Users\patmic\Desktop\CVZ_CVUT\Free_software_gis\Data\silnice_clip_krnapII.shp"
vector = fiona.open(vector_loc, "r")

lenghtOfSegment = 5

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
            preparedLine = prepareLine(line,1)
            points = cutLine(preparedLine, lenghtOfSegment)
            for point in points:
                prop = {'X': float(point.x), 'Y': float(point.y)}
                output.write({'geometry': mapping(point), 'properties': prop})