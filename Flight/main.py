import argparse
import matplotlib.pyplot as plt
import gpxpy
import gpxpy.gpx
import datetime
from decimal import Decimal
from FlightLine import FlightLine

parser = argparse.ArgumentParser(
    description='Generate GPX file according to flight info.')
parser.add_argument('-f', '--filename', required=True,
                    help='Flight information file in JSON format\
                          downloaded from Variflight.')
args = parser.parse_args()

with open(args.filename, 'r', encoding='utf-8') as file:
    flightline = FlightLine(file)

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
for lon, lat, ele, t in flightline.coord:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal('.0000001')),
                                                      Decimal(lon).quantize(Decimal('.0000001')),
                                                      Decimal(ele).quantize(Decimal('.01')),
                                                      time=t))

# You can add routes and waypoints, too...

with open(f'{args.filename}.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx.to_xml())


