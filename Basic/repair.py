import argparse
import matplotlib.pyplot as plt
# import gpxpy
import gpxpy.gpx
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import PolyLine

parser = argparse.ArgumentParser(
    description='Generate GPX file according to flight info.')
parser.add_argument('-m', '--mode', required=True,
                    choices=['bus', 'train'],
                    help='Work mode of this script.')
parser.add_argument('-f', '--filename', nargs='+',
                    help='Polyline information files.')
parser.add_argument('-r', '--repair',
                    help='A gpx file which needs to be repaired.')
args = parser.parse_args()

# 读入数据库提供的准确轨迹
if args.mode == 'train':
    polyline = PolyLine.PolyLine.train_vicc(*args.filename)
elif args.mode == 'bus':
    polyline = PolyLine.PolyLine.bus_GaoDe(*args.filename)
polyline.analytical()

# 读入测量的轨迹
measured = PolyLine.PolyLine.gpx(args.repair)

# 根据数据库中的准确轨迹修复测量的轨迹
measured.repair(polyline)

for i in measured.coord:
    print(type(i))
    print(i)

# fig, ax = plt.subplots()
# ax.plot(polyline.lon, polyline.lat, '-')
# ax.plot(measured.lon, measured.lat, 'o')
# plt.show()


# gpx = gpxpy.gpx.GPX()

# # Create first track in our GPX:
# gpx_track = gpxpy.gpx.GPXTrack()
# gpx.tracks.append(gpx_track)

# # Create first segment in our GPX track:
# gpx_segment = gpxpy.gpx.GPXTrackSegment()
# gpx_track.segments.append(gpx_segment)

# # Create points:
# for lon, lat, t in polyline.coord:
#     gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal('.0000001')),
#                                                       Decimal(lon).quantize(Decimal('.0000001')),
#                                                       time=t))

# # You can add routes and waypoints, too...

# with open('result.gpx', 'w', encoding='utf-8') as file:
#     file.write(gpx.to_xml())


