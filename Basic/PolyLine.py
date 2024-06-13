"""
测试 train_vicc::
    >>> file = 'data.kml'
    >>> with open(file, 'r', encoding='utf-8') as file:
    ...     trainline = PolyLine(LineType.train_vicc, file)
    
    
"""

from enum import Enum, auto
import numpy as np
from datetime import datetime

from pykml import parser
import json

from Coordinate import Location
from Coordinate import System
from Coordinate import Coordinate

# class LineType(Enum):
#     bus_GaoDe = auto()
#     train_vicc = auto()
#     flight = auto()

class PolyLine():
    """
    描述交通线路的一串 Coordinate 坐标点
    """
    
    def __init__(self, coords: np.array):
        self._coords = coords
    
    @classmethod
    def train_vicc(cls, *files: tuple[str, ...]):
        """
        从 train_vicc 文件中仅获取位置信息
        在拼接多个文件时，删除前一个文件末尾和后一个文件开头重复的坐标
        """
        coord_str_list = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                data = parser.parse(f).getroot()
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            coordinates = data.findall('.//kml:coordinates', namespaces=ns)
            for coords in coordinates:
                for coord in str(coords).split(' '):
                    if not coord_str_list:
                        coord_str_list.append(coord)
                    elif coord != coord_str_list[-1]:
                        coord_str_list.append(coord)

        coord_list = []
        for loc_str in coord_str_list:
            lon, lat = list(map(float, loc_str.split(',')))
            loc = Location(lon, lat)
            coord = Coordinate(loc, system=System.wgs84)
            coord_list.append(coord)
        _coords = np.array(coord_list)
        
        return cls(_coords)
    
    @classmethod
    def bus_GaoDe(cls, *files: tuple[str, ...]):
        """
        从 train_vicc 文件中仅获取位置信息
        在拼接多个文件时，删除前一个文件末尾和后一个文件开头重复的坐标
        高德地图提供的坐标串有时间隔比较大，需要手动添加中间坐标点
        """
        coord_str_list = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                busline = json.load(f)
            for coord in busline['polyline']:
                if not coord_str_list:
                    coord_str_list.append(coord)
                elif coord != coord_str_list[-1]:
                    coord_str_list.append(coord)
        
        coord_list = []
        for loc_str in coord_str_list:
            lon, lat = list(map(float, loc_str.split(',')))
            loc = Location(lon, lat)
            coord = Coordinate(loc, system=System.gcj02)
            coord_list.append(coord)
        
        index = 0
        pre_coord = coord_list[index]
        while index != len(coord_list):
            cur_coord = coord_list[index]
            if cur_coord.distance(pre_coord) > 0.001: # 100m
                coord_list.insert(index, cur_coord.middle(pre_coord))
            else:
                pre_coord = cur_coord
                index += 1
        
        _coords = np.array(coord_list)
        return cls(_coords)
                
    
    def add_times(self, start_time: datetime, end_time: datetime):
        """根据提供的起始和结束时间，为坐标添加时间信息"""
        acc_dists = []
        acc_dist = 0
        pre_coord = self._coords[0]
        for coord in self._coords:
            acc_dist += coord.distance(pre_coord) 
            acc_dists.append(acc_dist)
            pre_coord = coord
        total_dist = acc_dists[-1]
        percents = [acc_dist/total_dist for acc_dist in acc_dists]
        time_interval = end_time - start_time
        times = [start_time+time_interval*percent for percent in percents]
        
        coord_list = []
        for i in range(len(self._coords)):
            lon = self._coords[i].lon
            lat = self._coords[i].lat
            loc = Location(lon, lat)
            coord = Coordinate(loc, time=times[i], system=System.wgs84)
            coord_list.append(coord)
        self._coords = np.array(coord_list)
    
    
    @property
    def lon(self):
        return np.array([coord.lon for coord in self._coords])
    @property
    def lat(self):
        return np.array([coord.lat for coord in self._coords])
    @property
    def coord(self):
        return np.array([coord.coord for coord in self._coords])
    
    
        