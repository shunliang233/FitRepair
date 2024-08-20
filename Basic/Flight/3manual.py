"""
最好以 Strava 为核心来创建飞行轨迹，而不是 ADSB 组合文件 Track
因为 Strava 记录的时间间隔更小，轨迹更加平滑，在 FlightAware 和 VariFlight 上的轨迹都不够平滑
第 3 步先手动删除 Strava1.gpx 中不好的点，并从 Track.gpx 中手动添加合适的点，将新文件保存为 Strava2.gpx
如果能通过后续自动补全进行修复的话，仅删除 Strava 中的点即可，不用从 Track.gpx 中拷贝轨迹进来
画图查看 Strava2 相对于 Strava1 的变化，这个过程需要反复进行多次
"""

import argparse
import matplotlib.pyplot as plt
import PolyLine


parser = argparse.ArgumentParser(
    description='Generate GPX file according to flight info.')
parser.add_argument('-f', '--filename', nargs='+',
                    help='Coord and time information files.')
args = parser.parse_args()

FlightAware = PolyLine.PolyLine.gpx(args.filename[0])
if args.filename[1] and args.filename[2]:
    VariFlight = PolyLine.PolyLine.gpx(args.filename[1])
    Track = PolyLine.PolyLine.gpx(args.filename[2])
Strava1 = PolyLine.PolyLine.gpx(args.filename[3])
if args.filename[4]:
    Garmin1 = PolyLine.PolyLine.gpx(args.filename[4])
Strava2 = PolyLine.PolyLine.gpx(args.filename[5])

fig1, ax1 = plt.subplots()
if args.filename[1] and args.filename[2]:
    ax1.plot(Track.lon, Track.lat, 'o', label='Track')
    ax1.plot(VariFlight.lon, VariFlight.lat, 'o', label='VariFlight')
ax1.plot(FlightAware.lon, FlightAware.lat, 'o', label='FlightAware')
ax1.plot(Strava2.lon, Strava2.lat, 'o-', label='Strava2')
if args.filename[4]:
    ax1.plot(Garmin1.lon, Garmin1.lat, 'o', label='Garmin1')
ax1.plot(Strava1.lon, Strava1.lat, '-', label='Strava1')
ax1.set_aspect(1)
ax1.legend()
plt.show()
