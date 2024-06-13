"""
测试 FlightLine 类
    >>> with open('data.json', 'r', encoding='utf-8') as file:
    ...     f = FlightLine(file)

测试属性::
    >>> f._aircraft
    'A6EOV'
    >>> f._flight
    'EK303'
    >>> len(f._speed)
    1210
    >>> type(f._speed[0])
    <class 'numpy.float64'>
    >>> len(f._angle)
    1210
    >>> type(f._angle[0])
    <class 'numpy.float64'>
    >>> len(f._coord)
    1210
    >>> type(f._coord[0])
    <class 'Basic.Coordinate.Coordinate'>
    >>> print(f._coord[0])
    (121.83110809326172, 31.10934066772461, 304.8, datetime.datetime(2023, 7, 9, 16, 17, 46))
"""

import sys
import json
import numpy as np
from datetime import datetime
sys.path.append("..")
import Basic.Coordinate as Coordinate

class FlightLine:
    """描述航线的一串坐标点，以及航班相关信息"""
    
    def __init__(self, file):
        _data = json.load(file)
        self._aircraft = _data[0]['anum'] # 飞机编号
        self._flight = _data[0]['fnum'] # 航班编号
        self._speed = np.array([float(item['speed']) for item in _data])
        self._angle = np.array([float(item['angle']) for item in _data])
        _coord_list = []
        for item in _data:
            _lon = float(item['longitude'])
            _lat = float(item['latitude'])
            _loc = Coordinate.Location(_lon, _lat)
            _ele = float(item['height'])
            _time_str = item['UTC Time']
            _date, _time = _time_str.split(' ')
            _year, _month, _day = list(map(int, _date.split('-')))
            _hour, _minute, _second = list(map(int, _time.split(':')))
            _datetime = datetime(_year, _month, _day, _hour, _minute, _second)
            _coord = Coordinate.Coordinate(_loc, _ele, _datetime,
                                           system=Coordinate.System.wgs84)
            _coord_list.append(_coord)
        self._coord = np.array(_coord_list)

    @property
    def lon(self):
        return np.array([coord.lon for coord in self._coord])
    @property
    def lat(self):
        return np.array([coord.lat for coord in self._coord])
    @property
    def coord(self):
        return np.array([coord.coord for coord in self._coord])

    
