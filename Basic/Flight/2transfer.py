"""
第 2 步输出文件，将 FlightAware, VariFlight, Strava 的数据格式统一转化为 gpx 格式
画图检查 Track 是否正确地组合了 FlightAware 和 VariFlight 这两组数据
主要检查起飞和降落阶段是否出现最短距离方法连接到错误的点
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


FlightAware = PolyLine.PolyLine.kml(args.filename[0])
if args.filename[1]:
    VariFlight = PolyLine.PolyLine.json_VariFlight(args.filename[1])
    Track = PolyLine.PolyLine.combine(FlightAware, VariFlight)
Strava = PolyLine.PolyLine.fit(args.filename[2])
if args.filename[3]:
    Garmin = PolyLine.PolyLine.fit(args.filename[3])

fig, ax = plt.subplots()
if args.filename[1]:
    ax.plot(Track.lon, Track.lat, 'o', label='Track')
    ax.plot(VariFlight.lon, VariFlight.lat, 'o', label='VariFlight')
ax.plot(FlightAware.lon, FlightAware.lat, 'o', label='FlightAware')
ax.set_aspect(1)
ax.legend()
plt.show()


gpx1 = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx1.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
PRECISION = '.00000001' # 0.001m
for lon, lat, t, ele, heart_rate in FlightAware.coord:
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

with open('FlightAware.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx1.to_xml())




if args.filename[1]:
    gpx2 = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx2.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    PRECISION = '.00000001' # 0.001m
    for lon, lat, t, ele, heart_rate in VariFlight.coord:
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

    with open('VariFlight.gpx', 'w', encoding='utf-8') as file:
        file.write(gpx2.to_xml())





gpx3 = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx3.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
PRECISION = '.00000001' # 0.001m
for lon, lat, t, ele, heart_rate in Strava.coord:
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

with open('Strava1.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx3.to_xml())


if args.filename[3]:
    gpx4 = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx4.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    PRECISION = '.00000001' # 0.001m
    for lon, lat, t, ele, heart_rate in Garmin.coord:
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

    with open('Garmin1.gpx', 'w', encoding='utf-8') as file:
        file.write(gpx4.to_xml())




if args.filename[1]:
    gpx5 = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx5.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    PRECISION = '.00000001' # 0.001m
    for lon, lat, t, ele, heart_rate in Track.coord:
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

    with open('Track.gpx', 'w', encoding='utf-8') as file:
        file.write(gpx5.to_xml())