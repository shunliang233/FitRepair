import matplotlib as plt
import xml.etree.ElementTree as ET
import pykml.parser
from datetime import datetime

file = './test/FlightAware_CCA759_ZBAA_RJGG_20240706.kml'
# tree = ET.parse(file)
# root = tree.getroot()
# ns = {'kml': 'http://www.opengis.net/kml/2.2',
#       'gx': 'http://www.google.com/kml/ext/2.2'}
# track = root.find('.//gx:Track', namespaces=ns)
# coord = track.findall('kml:when', namespaces=ns)
# print(coord)
# print(root.findall('.//kml:name', namespaces=ns))



# file_google = './test/空港線(TA22常滑-TA24中部国際空港)-polyline.kml'
# with open(file_google, 'r', encoding='utf-8') as f:
#     data2 = parser.parse(f).getroot()
#     for pm in data2.Document.Placemark:
#         print(pm.name)

coord_str_list = []
with open(file, 'r', encoding='utf-8') as f:
    data = pykml.parser.parse(f).getroot()
ns = {'kml': 'http://www.opengis.net/kml/2.2',
      'gx': 'http://www.google.com/kml/ext/2.2'}
coordinates = data.find('.//gx:coord', namespaces=ns)

# coord_str_list = []
# data = ET.parse(file)
# ns = {'kml': 'http://www.opengis.net/kml/2.2',
#       'gx': 'http://www.google.com/kml/ext/2.2'}
# coordinates = data.find('.//kml:coordinates', namespaces=ns)

# print(coordinates)
# for coords in coordinates:
#     for coord in str(coords).split():
#         if not coord_str_list:
#             coord_str_list.append(coord)
#         elif coord != coord_str_list[-1]:
#             coord_str_list.append(coord)

# print(coord_str_list)
print(str(coordinates).split(), type(coordinates))

# for coords in coordinates:
#     print(coords)