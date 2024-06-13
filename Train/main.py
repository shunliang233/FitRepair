import argparse
import matplotlib.pyplot as plt
import gpxpy
import gpxpy.gpx
import datetime
from decimal import Decimal
from TrainLine import TrainLine

parser = argparse.ArgumentParser(
    description='Generate GPX file according to flight info.')
parser.add_argument('-f', '--filename', required=True,
                    help='Train information file in KML format\
                          downloaded from https://vicc.wang:4443/')
args = parser.parse_args()

with open(args.filename, 'r', encoding='utf-8') as file:
    trainline = TrainLine(file)

# fig, ax = plt.subplots()
# ax.plot(flightline.polyline_lon, flightline.polyline_lat, 'o')
# plt.show()


gpx = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
for lon, lat in trainline.coord:
    t = datetime.datetime(2023, 7, 1, 17, 0, 0)
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal('.0000001')),
                                                      Decimal(lon).quantize(Decimal('.0000001')),
                                                      time=t))

# You can add routes and waypoints, too...

with open(f'{args.filename}.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx.to_xml())


