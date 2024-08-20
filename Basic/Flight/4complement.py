"""
第 4 步对手动修复的 Strava2.gpx 中间距过大的点进行补全，并输出最终的 Strava3.gpx 文件
然后搜索并输出将要进行自动补全的区间，并执行补全，将补全后的文件存储为 Strava3.gpx
画图显示补全前和补全后的轨迹情况，依次查看需要补全的区间是否可以被正常补全
"""

import argparse
import gpxpy.gpx
from decimal import Decimal
import matplotlib.pyplot as plt
import PolyLine


parser = argparse.ArgumentParser(
    description='Generate GPX file according to flight info.')
parser.add_argument('-f', '--filename', nargs='+',
                    help='Coord and time information files.')
args = parser.parse_args()

if args.filename[0]:
    Track = PolyLine.PolyLine.gpx(args.filename[0])
Strava1 = PolyLine.PolyLine.gpx(args.filename[1])
Strava2 = PolyLine.PolyLine.gpx(args.filename[2])
Strava3 = PolyLine.PolyLine.gpx(args.filename[2])

interval_list = Strava3.missing()
Append = Strava3.add_point(interval_list)

fig1, ax1 = plt.subplots()
if args.filename[0]:
    ax1.plot(Track.lon, Track.lat, 'o', label='Track')
ax1.plot(Strava1.lon, Strava1.lat, '-', label='Strava1')
ax1.plot(Append.lon, Append.lat, 'o', label='Append')
ax1.set_aspect(1)
ax1.legend()
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
for lon, lat, t, ele, heart_rate in Strava3.coord:
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

with open('Strava3.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx.to_xml())