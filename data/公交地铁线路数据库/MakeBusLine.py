import sys
import requests
import argparse
import json

# 支持从命令行提供线路查询的关键词
parser = argparse.ArgumentParser(
    description='Output a JSON file which contains a traffic line\
                 from specified start station to end station.')
parser.add_argument('--id',
                    required=True,
                    help='The id of traffic in Gao De map.')
parser.add_argument('--start', required=True)
parser.add_argument('--end', required=True)

args = parser.parse_args()

# 固定的参数
KEY = '0657aa0795e30e72c514b023dea7956a'
EXTENSIONS = 'all'
url = 'https://restapi.amap.com/v3/bus/lineid?parameters'

# 获取线路查询结果
params = {
    'key': KEY,
    'id': args.id,
    'extensions': EXTENSIONS}
result = requests.get(url, params).json()

# 简单判断是否查询成功
status = False
if result['status'] == '1' and result['info'] == 'OK':
    if len(result['buslines']) == 0:
        print(f'ERROR: No bus line with id: {id}')
        sys.exit()
    elif len(result['buslines']) == 1:
        status = True
    else:
        print('ERROR: Multi bus line?!')
        sys.exit()
else:
    print('ERROR: Failed request!')
    sys.exit()

# 若查询成功，则将 busline 中的信息分类存储
if status == True:
    busline = result['buslines'][0]
    id_ = busline['id']
    type_ = busline['type']
    name = busline['name']
    polyline = busline['polyline'].split(';') # 列表元素是 loc 字符串
    busstops = busline['busstops'] # 列表元素是 busstop 字典

# 获取起始和结束站点的信息
start_station = None
end_station = None
for busstop in busstops:
    if busstop['name'] == args.start:
        start_station = busstop
    elif busstop['name'] == args.end:
        end_station = busstop
if not start_station or not end_station:
    if not start_station:
        print(f'ERROR: no busstop named {args.start}')
    if not end_station:
        print(f'ERROR: no busstop named {args.end}')
    print('The busstops should be:')
    for busstop in busstops:
        print(f'\t{busstop['name']}')
    sys.exit()

# 根据起始和结束站点的位置信息，截断 polyline
start_index = polyline.index(start_station['location'])
end_index = polyline.index(end_station['location'])
if start_index <= end_index:
    index = start_index
    partial_polyline = []
    while index != end_index + 1:
        partial_polyline.append(polyline[index])
        index += 1
else:
    print('ERROR: choose the opposite busline!')
    sys.exit()

# 截断成功后，将 busline 输出 JSON 文件
partial_busline = {}
partial_busline['polyline'] = partial_polyline
filename = f'{type_}{name}({start_station['name']}-{end_station['name']}).json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(partial_busline, f, indent=2, ensure_ascii=False)