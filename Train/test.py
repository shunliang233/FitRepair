
from pykml import parser

# 读取 KML 文件
with open('data.kml', 'r') as f:
    root = parser.parse(f).getroot()

# 获取地理位置数据
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
coordinates = root.findall('.//kml:coordinates', namespaces=ns)
for coord in coordinates:
    for i in range(0, 10):
        print(coord.text[i])
# print(len(coordinates))