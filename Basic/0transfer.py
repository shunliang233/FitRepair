'''
如果 fit 文件中含有错得非常离谱的点，就需要转成 gpx 文件，
手动删除这些点，再修复 gpx 文件
'''

import argparse
import gpxpy.gpx
from decimal import Decimal
import PolyLine

parser = argparse.ArgumentParser(
    description='Generate GPX file according to flight info.')
parser.add_argument('-f', '--filename',
                    help='Fit file need to be transferred.')
args = parser.parse_args()

fit = PolyLine.PolyLine.fit(args.filename)


gpx1 = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx1.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
PRECISION = '.00000001' # 0.001m
for lon, lat, t, ele, heart_rate in fit.coord:
    if ele != None:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal(PRECISION)),
                                                      Decimal(lon).quantize(Decimal(PRECISION)),
                                                      elevation=Decimal(ele).quantize(Decimal('.01')),
                                                      time=t))
    else:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal(PRECISION)),
                                                      Decimal(lon).quantize(Decimal(PRECISION)),
                                                      time=t))

# You can add routes and waypoints, too...

with open('transfer.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx1.to_xml())