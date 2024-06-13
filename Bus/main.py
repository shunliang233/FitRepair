import argparse
import matplotlib.pyplot as plt
import gpxpy
import gpxpy.gpx
import datetime
from BusLine import BusLine
from decimal import Decimal

parser = argparse.ArgumentParser(
    description='Repair GPX file according to busline ID.')
parser.add_argument('-i', '--id',
                    required=True,
                    help='Provide busline ID.')
args = parser.parse_args()

busline = BusLine(args.id)

# fig, ax = plt.subplots()
# ax.plot(busline.polyline_lon, busline.polyline_lat)
# ax.plot(busline.busstops_lon, busline.busstops_lat, 'o')
# plt.show()

# print(busline.validate())





gpx = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
location = busline.polyline_locations

for lon, lat in location:
    t = datetime.datetime(2024, 5, 20, 10, 0, 0)
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal('.0000001')), Decimal(lon).quantize(Decimal('.0000001')), time=t))

# You can add routes and waypoints, too...

print(gpx.to_xml())


