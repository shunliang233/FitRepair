import argparse
import matplotlib.pyplot as plt
import gpxpy
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
parser.add_argument('-t', '--time', nargs=2,
                    help='Start and end time of a bus/train')
parser.add_argument('--timezone', type=int, default=8)
args = parser.parse_args()

dt = timedelta(hours=args.timezone)
t1 = datetime.fromisoformat(args.time[0]) - dt
t2 = datetime.fromisoformat(args.time[1]) - dt

if args.mode == 'train':
    polyline = PolyLine.PolyLine.train_vicc(*args.filename)
elif args.mode == 'bus':
    polyline = PolyLine.PolyLine.bus_GaoDe(*args.filename)
polyline.add_times(t1, t2)

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
for lon, lat, t in polyline.coord:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal('.0000001')),
                                                      Decimal(lon).quantize(Decimal('.0000001')),
                                                      time=t))

# You can add routes and waypoints, too...

with open('result.gpx', 'w', encoding='utf-8') as file:
    file.write(gpx.to_xml())


