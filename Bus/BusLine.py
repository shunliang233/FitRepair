"""
测试 BusLine 类
    >>> second = BusLine('110100023099')

测试属性是否正常::
    >>> second._busline['id']
    '110100023099'
    >>> second._id
    '110100023099'
    >>> second._type
    '地铁'
    >>> second._name
    '地铁2号线外环(西直门--西直门)'
    >>> type(second._polyline)
    <class 'PolyLine.PolyLine'>
    >>> len(second._polyline)
    237
    >>> type(second._busstops)
    <class 'BusStops.BusStops'>
    >>> len(second._busstops)
    19

测试 validate() 函数是否正常工作
    >>> second.validate()
    True
    >>> fake_dict = {'id': 'BV10001595', 'location': '720.35,278.84',\
                     'name': '假的站点', 'sequence': '100'}
    >>> fake_busstop = BusStop(**fake_dict)
    >>> second._busstops.append(fake_busstop)
    >>> second.validate()
    False
    >>> second._busstops.pop()
    >>> second.validate()
    True
"""

import requests
import numpy as np
from BusStop import BusStop
from BusStops import BusStops
from PolyLine import PolyLine
from Basic.Coordinate import distance
from Basic.Coordinate import Location

class BusLine:
    """公共交通线路对象，用于描述一条公共交通线路"""
    
    def __init__(self, id: str):
        """
        传入公交线路在高德地图上的 id, 利用高德 API 构造一条线路对象
        """
        
        # 固定的参数
        KEY = '0657aa0795e30e72c514b023dea7956a'
        EXTENSIONS = 'all'
        url = 'https://restapi.amap.com/v3/bus/lineid?parameters'
        
        # 获取线路查询结果
        params = {
            'key': KEY,
            'id': id,
            'extensions': EXTENSIONS}
        result = requests.get(url, params).json()
    
        # 简单判断是否查询成功
        status = False
        if result['status'] == '1' and result['info'] == 'OK':
            if len(result['buslines']) == 0:
                print(f'ERROR: No bus line with id: {id}')
            elif len(result['buslines']) == 1:
                status = True
            else:
                print('ERROR: Multi bus line?!')
        else:
            print('ERROR: Failed request!')
        
        # 若查询成功，则构造属性
        if status == True:
            self._busline = result['buslines'][0]
            self._id = self._busline['id']
            self._type = self._busline['type']
            self._name = self._busline['name']
            self._polyline = PolyLine(self._busline['polyline'])
            self._busstops = BusStops([BusStop(**busstop)
                                       for busstop in self._busline['busstops']])
    
    
    def validate(self) -> bool:
        """
        验证 busstops.locations() 中的所有点都被包含在 polyline.locations() 中
        """
        PRECISION = 0.0000001  # 精确到 1cm
        validation = True
        for station in self._busstops.locations:
            if min(distance(Location(*station), Location(*location))
                   for location in self._polyline.locations) > PRECISION:
                validation = False
                break
        return validation
    
    @property
    def polyline_lon(self):
        return self._polyline.lon
    @property
    def polyline_lat(self):
        return self._polyline.lat
    @property
    def polyline_locations(self):
        return self._polyline.locations
    @property
    def busstops_lon(self):
        return self._busstops.lon
    @property
    def busstops_lat(self):
        return self._busstops.lat
    @property
    def busstops_locations(self):
        return self._busstops.locations
    