import requests
import argparse

# 支持从命令行提供线路查询的关键词
parser = argparse.ArgumentParser(
    description='Search for public traffic lines according to keywords.')
parser.add_argument('-c', '--city',
                    default='全国',
                    help='Search traffic lines in which city.')
parser.add_argument('-k', '--keyword',
                    required=True,
                    help='The keyword for searching traffic lines.')
parser.add_argument('-v', '--verbose',
                    type=int,
                    choices=[0, 1],
                    default=0,
                    help='Set the verbose level of output.')
args = parser.parse_args()

# 线路查询所需的固定信息
KEY = '0657aa0795e30e72c514b023dea7956a'
EXTENSIONS = 'all' # 获取途径站点

# 进行线路查询，查询到完整的信息存入 result
url = 'https://restapi.amap.com/v3/bus/linename?parameters'
params = {
    'key': KEY,
    'keywords': args.keyword,
    'city': args.city,
    'extensions': EXTENSIONS}
result = requests.get(url, params).json() # 字典

# 定义不同冗余度的输出函数
def output_v0(buslines: list):
    for busline in buslines:
        print(f'ID: {busline['id']}    线路名称: {busline['name']}')

def output_v1(buslines: list):
    for busline in buslines:
        print(f'ID: {busline['id']}    线路名称: {busline['name']}')
        for busstop in busline['busstops']:
            print(f'    {busstop['sequence']:<2}: {busstop['name']}')
        print()

# 简化高德返回的数据
if result['status'] == '1' and result['info'] == 'OK':
    buslines = result['buslines']
    if args.verbose == 0:
        output_v0(buslines)
    elif args.verbose == 1:
        output_v1(buslines)
else:
    print("ERROR: Failed request!")
    

