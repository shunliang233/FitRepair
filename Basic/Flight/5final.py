"""
第 5 步画图检查最终的 Strava3.gpx 文件
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

FlightAware = PolyLine.PolyLine.gpx(args.filename[0])
if args.filename[1]:
    VariFlight = PolyLine.PolyLine.gpx(args.filename[1])
Strava1 = PolyLine.PolyLine.gpx(args.filename[2])
Strava3 = PolyLine.PolyLine.gpx(args.filename[3])

fig1, ax1 = plt.subplots()
ax1.plot(FlightAware.lon, FlightAware.lat, 'o', label='FlightAware')
if args.filename[1]:
    ax1.plot(VariFlight.lon, VariFlight.lat, 'o', label='VariFlight')
ax1.plot(Strava3.lon, Strava3.lat, 'o', label='Strava3')
ax1.plot(Strava1.lon, Strava1.lat, '-', label='Strava1')
ax1.set_aspect(1)
ax1.legend()
plt.show()