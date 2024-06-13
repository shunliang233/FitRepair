"""
测试 TrainLine 类
    >>> with open('data.kml', 'r', encoding='utf-8') as file:
    ...     f = TrainLine(file)

测试属性::
    >>> len(f._coord)
    12030
    >>> type(f._coord[0])
    <class 'Basic.Coordinate.Coordinate'>
    >>> print(f._coord[0])
    (116.3706846, 39.8621346)
"""

import sys
from pykml import parser
import numpy as np
sys.path.append("..")
import Basic.Coordinate as Coordinate

class TrainLine:
    """描述火车线路的类"""
    
    def __init__(self, *files):
        _coord_str = ''
        for file in files:
            _data = parser.parse(file).getroot()
            _ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            _coordinates = _data.findall('.//kml:coordinates', namespaces=_ns)
            for coord in _coordinates:
                _coord_str += coord
                _coord_str += ' '
        _coord_str = _coord_str.strip()
        
        _coord_list = []
        for loc_str in _coord_str.split(' '):
            _lon, _lat = list(map(float, loc_str.split(',')))
            _loc = Coordinate.Location(_lon, _lat)
            _coord = Coordinate.Coordinate(_loc, system=Coordinate.System.wgs84)
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

    
