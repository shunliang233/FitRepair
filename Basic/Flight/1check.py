"""
第 1 步仅画图，检查 Strava 测量值有问题的地方
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
Strava = PolyLine.PolyLine.fit(args.filename[2])
if args.filename[3]:
    Garmin = PolyLine.PolyLine.fit(args.filename[3])


fig, ax = plt.subplots()
ax.plot(FlightAware.lon, FlightAware.lat, 'o', label='FlightAware')
if args.filename[1]:
    ax.plot(VariFlight.lon, VariFlight.lat, 'o', label='VariFlight')
ax.plot(Strava.lon, Strava.lat, 'o', label='Strava')
if args.filename[3]:
    ax.plot(Garmin.lon, Garmin.lat, 'o', label='Garmin')
ax.set_aspect(1)
ax.legend()
plt.show()


