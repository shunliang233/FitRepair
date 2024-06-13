"""
测试 BusStops 类
    >>> from BusStop import BusStop
    >>> d1 = {'id': 'BV10001595', 'location': '116.355426,39.940474',\
              'name': '西直门', 'sequence': '19'}
    >>> b1 = BusStop(**d1)
    >>> d2 = {'id': 'BV10013430', 'location': '116.373126,39.948653',\
              'name': '积水潭', 'sequence': '18'}
    >>> b2 = BusStop(**d2)
    >>> d3 = {'id': 'BV10013431', 'location': '116.393776,39.948972',\
              'name': '鼓楼大街', 'sequence': '17'}
    >>> b3 = BusStop(**d3)
    >>> stations = BusStops([b1, b2, b3])

测试属性是否正常::
    >>> type(stations._busstops)
    <class 'numpy.ndarray'>
    >>> type(stations._busstops[0])
    <class 'BusStop.BusStop'>

测试特殊函数::
    >>> len(stations)
    3

测试关于位置的方法::
    >>> stations.lon_gcj
    array([116.355426, 116.373126, 116.393776])
    >>> stations.lat_gcj
    array([39.940474, 39.948653, 39.948972])
    >>> stations.locations_gcj
    array([[116.355426,  39.940474],
           [116.373126,  39.948653],
           [116.393776,  39.948972]])

测试 append 方法::
    >>> d4 = {'id': 'BV10001936', 'location': '116.408227,39.949087',\
              'name': '安定门', 'sequence': '16'}
    >>> b4 = BusStop(**d4)
    >>> stations.append(b4)
    >>> len(stations)
    4
    >>> stations.pop()
    >>> len(stations)
    3
"""

import numpy as np
from BusStop import BusStop
from typing import Iterable

class BusStops:
    """
    公交线路上的一串公交站
    可以用 lon 和 lat 分别导出经度和纬度 array, 以便 matplotlib 画图
    """
    
    def __init__(self, busstops: Iterable[BusStop]):
        """
        接受指向 BusStop 类型对象的可迭代对象作为参数
        """
        self._busstops = np.array(busstops)
    
    def __len__(self):
        return len(self._busstops)
    
    @property
    def lon(self):
        return np.array([busstop.lon for busstop in self._busstops])
    @property
    def lat(self):
        return np.array([busstop.lat for busstop in self._busstops])
    @property
    def locations(self):
        return np.array([busstop.location for busstop in self._busstops])
    @property
    def lon_gcj(self):
        return np.array([busstop.lon_gcj for busstop in self._busstops])
    @property
    def lat_gcj(self):
        return np.array([busstop.lat_gcj for busstop in self._busstops])
    @property
    def locations_gcj(self):
        return np.array([busstop.location_gcj for busstop in self._busstops])
    
    """供 BusLine 中 validate 测试用的"""
    def append(self, busstop: BusStop):
        self._busstops = np.append(self._busstops, busstop)
    def pop(self):
        self._busstops = np.delete(self._busstops, -1)