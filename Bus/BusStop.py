"""
测试 BusStop 类
    >>> d = {'id': 'BV10001595', 'location': '116.355426,39.940474',\
             'name': '西直门', 'sequence': '19'}
    >>> station = BusStop(**d)

测试属性是否正常::
    >>> station._id
    'BV10001595'
    >>> station._name
    '西直门'
    >>> type(station._coordinate)
    <class 'Coordinate.Coordinate'>
    
测试 property 是否正常::
    >>> type(station.lon)
    <class 'float'>
    >>> station.lon_gcj
    116.355426
    >>> station.lat_gcj
    39.940474
    >>> station.location_gcj
    array([116.355426,  39.940474])
    >>> station.lon
    116.34924069326846
    >>> station.lat
    39.93912181555644
    >>> station.location
    array([116.34924069,  39.93912182])
"""

import numpy as np
import Basic.Coordinate as Coordinate

class BusStop:
    """
    独立的公交站对象
    """
    
    def __init__(self, id, name, location, **kwargs):
        self._id = str(id)
        self._name = str(name)
        _loc = Coordinate.Location(*[float(coord)
                                     for coord in location.split(',')])
        self._coordinate = Coordinate.Coordinate(_loc, system=Coordinate.System.gcj02)
    
    @property
    def lon(self):
        return self._coordinate.lon
    @property
    def lat(self):
        return self._coordinate.lat
    @property
    def location(self):
        return self._coordinate.location
    @property
    def lon_gcj(self):
        return self._coordinate.lon_gcj
    @property
    def lat_gcj(self):
        return self._coordinate.lat_gcj
    @property
    def location_gcj(self):
        return self._coordinate.location_gcj
        
        