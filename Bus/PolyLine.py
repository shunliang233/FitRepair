"""
测试 PolyLine 类
    >>> coords = '116.355426,39.940474;116.355425,39.939513;116.355498,39.9375'
    >>> p = PolyLine(coords)

测试属性是否正常::
    >>> type(p._polyline)
    <class 'numpy.ndarray'>
    >>> type(p._polyline[0])
    <class 'Coordinate.Coordinate'>

测试特殊函数::
    >>> len(p)
    3

测试方法是否正常::
    >>> p.lon_gcj
    array([116.355426, 116.355425, 116.355498])
    >>> p.lat_gcj
    array([39.940474, 39.939513, 39.9375  ])
    >>> p.locations_gcj
    array([[116.355426,  39.940474],
           [116.355425,  39.939513],
           [116.355498,  39.9375  ]])
"""

import numpy as np
import Basic.Coordinate as Coordinate

class PolyLine:
    """
    描述公交线路的一串坐标点
    可以用 lon 和 lat 分别导出经度和纬度 array, 以便 matplotlib 画图
    """
    
    def __init__(self, polyline: str):
        """
        接受高德地图的 polyline 字符串作为参数
        """
        _coord_list = []
        for _loc_str in polyline.split(';'):
            _loc = Coordinate.Location(*[float(coord)
                                         for coord in _loc_str.split(',')])
            _coord = Coordinate.Coordinate(_loc, system=Coordinate.System.gcj02)
            _coord_list.append(_coord)
        self._polyline = np.array(_coord_list)
    
    def __len__(self):
        return len(self._polyline)
    
    @property
    def lon(self):
        return np.array([coord.lon for coord in self._polyline])
    @property
    def lat(self):
        return np.array([coord.lat for coord in self._polyline])
    @property
    def locations(self):
        return np.array([coord.location for coord in self._polyline])
    @property
    def lon_gcj(self):
        return np.array([coord.lon_gcj for coord in self._polyline])
    @property
    def lat_gcj(self):
        return np.array([coord.lat_gcj for coord in self._polyline])
    @property
    def locations_gcj(self):
        return np.array([coord.location_gcj for coord in self._polyline])