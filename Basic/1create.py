import argparse
# import gpxpy
import gpxpy.gpx
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import PolyLine
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    description='Generate GPX file according to line info.')
parser.add_argument('--type', required=True,
                    choices=['json_GaoDe', 'kml'],
                    help='Type of input files.')
parser.add_argument('-f', '--filename', nargs='+',
                    help='Polyline information files.')
parser.add_argument('-t', '--time', nargs=2,
                    help='Start and end time of a bus/train')
parser.add_argument('--timezone', type=int, required=True)
args = parser.parse_args()

dt = timedelta(hours=args.timezone)
t1 = datetime.fromisoformat(args.time[0] + 'Z') - dt
t2 = datetime.fromisoformat(args.time[1] + 'Z') - dt

"""目前所有来源都只有 lon 和 lat 信息，没有其他信息"""
# 包括 vicc 和 Google My Map 导出的 kml 轨迹数据
if args.type == 'kml':
    no_time_line = PolyLine.PolyLine.kml(*args.filename)
# 专门针对高德地图 API 导出的轨迹数据
elif args.type == 'json_GaoDe':
    no_time_line = PolyLine.PolyLine.json_GaoDe(*args.filename)
time_line = PolyLine.PolyLine.add_times(no_time_line, t1, t2)


fig, ax = plt.subplots()
ax.plot(time_line.lon, time_line.lat, 'o', label='time_line')
ax.plot(no_time_line.lon, no_time_line.lat, '-', label='no_time_line')
ax.set_aspect(1)
ax.legend()
plt.show()


gpx = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
PRECISION = '.00000001' # 0.001m
for lon, lat, t, ele, heart_rate in time_line.coord:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal(PRECISION)),
                                                      Decimal(lon).quantize(Decimal(PRECISION)),
                                                      time=t))

# You can add routes and waypoints, too...

with open('result.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx.to_xml())


