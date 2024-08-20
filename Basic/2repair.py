import argparse
import matplotlib.pyplot as plt
# import gpxpy
import gpxpy.gpx
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import PolyLine
import sys

parser = argparse.ArgumentParser(
    description='Repair fit file according to line info.')
parser.add_argument('--LineType', required=True,
                    choices=['json_GaoDe', 'kml', 'gpx'],
                    help='Traffic line file type.')
parser.add_argument('--FileType', required=True,
                    choices=['tcx', 'gpx', 'fit'],
                    help='The type of file to be repaired.')
parser.add_argument('-l', '--line', nargs='+',
                    help='Polyline information files.')
parser.add_argument('-f', '--file',
                    help='A file which needs to be repaired.')
parser.add_argument('--start', default=None)
parser.add_argument('--end', default=None)
parser.add_argument('--timezone', default=None, type=int)
args = parser.parse_args()

# 读入数据库提供的准确轨迹
if args.LineType == 'kml':
    polyline = PolyLine.PolyLine.kml(*args.line)
elif args.LineType == 'json_GaoDe':
    polyline = PolyLine.PolyLine.json_GaoDe(*args.line)
elif args.LineType == 'other':
    polyline = PolyLine.PolyLine.gpx(*args.line, 0.0001)
polyline.add_sequence()
polyline.analytical()

# 读入测量的轨迹
# TODO: 如果用 repaired = measured 会导致两者表示同一个对象
if args.FileType == 'tcx':
    measured = PolyLine.PolyLine.tcx(args.file)
    repaired = PolyLine.PolyLine.tcx(args.file)
elif args.FileType == 'gpx':
    measured = PolyLine.PolyLine.gpx(args.file)
    repaired = PolyLine.PolyLine.gpx(args.file)
elif args.FileType == 'fit':
    measured = PolyLine.PolyLine.fit(args.file)
    repaired = PolyLine.PolyLine.fit(args.file)
repaired.add_percent()

# 根据数据库中的准确轨迹修复测量的轨迹
if args.start or args.end:
    if args.timezone:
        dt = timedelta(hours=args.timezone)
    else:
        print("ERROR: Must provide timezone when give time!")
        sys.exit()
    if args.start:
        start = datetime.fromisoformat(args.start + 'Z') - dt
    else:
        start = None
    if args.end:
        end = datetime.fromisoformat(args.end + 'Z') - dt
    else:
        end = None
else:
    start = None
    end = None
repaired.repair(polyline, start, end)

# 检查修复是否有问题
fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.plot(polyline.lon, polyline.lat, '-', label='True Line')
ax1.plot(measured.lon, measured.lat, 'o-', label='Original Measured')
ax1.set_aspect(1)
ax1.legend()
ax2.plot(polyline.lon, polyline.lat, '-', label='True Line')
ax2.plot(repaired.lon, repaired.lat, 'o-', label='Repaired')
ax2.set_aspect(1)
ax2.legend()
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
for lon, lat, t, ele, heart_rate in repaired.coord:
    if ele == None:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal(PRECISION)),
                                                          Decimal(lon).quantize(Decimal(PRECISION)),
                                                          time=t))
    else:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal(PRECISION)),
                                                          Decimal(lon).quantize(Decimal(PRECISION)),
                                                          elevation=Decimal(ele).quantize(Decimal('.01')),
                                                          time=t))
# You can add routes and waypoints, too...

with open('result.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx.to_xml())


