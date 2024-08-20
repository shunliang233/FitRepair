import argparse
import xml.etree.ElementTree as ET
from decimal import Decimal
import PolyLine
import gpxpy.gpx


parser = argparse.ArgumentParser(
    description='Convert kml and gpx files.')
parser.add_argument('--to', required=True, choices=['kml', 'gpx'])
parser.add_argument('-f', '--file', required=True)
args = parser.parse_args()

# 判断原文件的类型
tree = ET.parse(args.file)
root = tree.getroot()
ns = {'kml': 'http://www.opengis.net/kml/2.2',
      'gpx': "http://www.topografix.com/GPX/1/1"}
if root.tag == '{http://www.opengis.net/kml/2.2}kml':
    track = PolyLine.PolyLine.kml(args.file)
elif root.tag == '{http://www.topografix.com/GPX/1/1}gpx':
    track = PolyLine.PolyLine.gpx(args.file)

filename = 'result.' + args.to
if args.to == 'kml':
    # 输出 result.kml 文件
    content = \
'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
\t<Document>
\t\t<Placemark>
\t\t\t<name>shunliang</name>
\t\t\t<LineString>
\t\t\t\t<coordinates>
'''
    for coord in track._coords:
        content += f'\t\t\t\t\t{coord.lon:.7f},{coord.lat:.7f}\n'
    content += \
'''\t\t\t\t</coordinates>
\t\t\t</LineString>
\t\t</Placemark>
\t</Document>
</kml>
'''
elif args.to == 'gpx':
    # 输出 result.gpx 文件
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    PRECISION = '.0000001' # 0.01m
    for lon, lat, t, ele, heart_rate in track.coord:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(Decimal(lat).quantize(Decimal(PRECISION)),
                                                          Decimal(lon).quantize(Decimal(PRECISION)),
                                                          time=t))
    content = gpx.to_xml()

# 保存为文件
with open(filename, 'w') as file:
    file.write(content)

