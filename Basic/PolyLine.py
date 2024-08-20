"""
测试 train_vicc::
    >>> file = 'data.kml'
    >>> with open(file, 'r', encoding='utf-8') as file:
    ...     trainline = PolyLine(LineType.train_vicc, file)
    
    
"""

from enum import Enum, auto
import numpy as np
from datetime import datetime
from datetime import timedelta

import pykml.parser
import json
import gpxpy
from fitparse import FitFile
from tcxreader.tcxreader import TCXReader

from Coordinate import Location
from Coordinate import System
from Coordinate import Coordinate
import sys
import math

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
    def json_VariFlight(cls, file: str):
        """
        从国内的 VariFlight 网站获取的 json 格式的航班飞行数据
        """
        coord_list = []
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            lon = float(item['longitude'])
            lat = float(item['latitude'])
            ele = float(item['height'])
            time = datetime.fromisoformat(item['UTC Time'] + 'Z')
            loc = Location(lon, lat)
            coord = Coordinate(loc, time, ele, system=System.wgs84)
            coord_list.append(coord)
        _coords = np.array(coord_list)
        return cls(_coords)

    @classmethod
    def json_GaoDe(cls, *files: tuple[str, ...]):
        """
        从高德 API 获取的 JSON 文件中提取位置信息
        在拼接多个文件时，删除前一个文件末尾和后一个文件开头重复的坐标
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
        
        # # 增加点，防止热图上出现间隔
        # MAX_SEPARATION = 0.001
        # index = 0
        # pre_coord = coord_list[index]
        # while index != len(coord_list):
        #     cur_coord = coord_list[index]
        #     if cur_coord.distance(pre_coord) > MAX_SEPARATION:
        #         coord_list.insert(index, cur_coord.middle(pre_coord))
        #     else:
        #         pre_coord = cur_coord
        #         index += 1
        
        _coords = np.array(coord_list)
        return cls(_coords)
    
    @classmethod
    def kml(cls, *files: tuple[str, ...]):
        """
        从 kml 文件中获取位置和时间信息
        在拼接多个文件时，删除前一个文件末尾和后一个文件开头重复的坐标
        目前有三种 kml 文件：
            vicc 导出的中国铁路线，只有水平位置信息
            Google My Map 画的路线，有立体位置信息，但是高度信息始终为 0，需要删掉
            FlightAware 导出的飞行路线，有立体位置信息和时间信息
        """
        # 点过于密集的话 strava 会罢工，过于稀疏的话热图上会有间断
        # MAX_SEPARATION = 0.001 # 100m
        
        lon_str_list = []
        lat_str_list = []
        alt_str_list = []
        time_str_list = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                data = pykml.parser.parse(f).getroot()
            ns = {'kml': 'http://www.opengis.net/kml/2.2',
                  'gx': 'http://www.google.com/kml/ext/2.2'}
            LineString = data.find('.//kml:LineString', namespaces=ns)
            Track = data.find('.//gx:Track', namespaces=ns)
            
            # My Map 画的和 vicc 导出的 kml 文件，只有水平位置，没有时间信息
            if LineString != None:
                coordinates = LineString.find('kml:coordinates', namespaces=ns)
                for coord in str(coordinates).split():
                    lon, lat, *other = coord.split(',')
                    if not lon_str_list:
                        lon_str_list.append(lon)
                        lat_str_list.append(lat)
                        alt_str_list.append(None)
                        time_str_list.append(None)
                    elif lon != lon_str_list[-1] or lat != lat_str_list[-1]:
                        lon_str_list.append(lon)
                        lat_str_list.append(lat)
                        alt_str_list.append(None)
                        time_str_list.append(None)
            # FlightAware 导出的飞行路线，有立体位置和时间信息
            elif Track != None:
                coordinates = Track.findall('gx:coord', namespaces=ns)
                times = Track.findall('kml:when', namespaces=ns)
                if len(coordinates) != len(times):
                    print('ERROR: the number of coordinates and times in FlightAware is different!')
                    sys.exit()
                for i in range(len(coordinates)):
                    lon, lat, alt = str(coordinates[i]).split()
                    time = str(times[i])
                    if not lon_str_list:
                        lon_str_list.append(lon)
                        lat_str_list.append(lat)
                        alt_str_list.append(alt)
                        time_str_list.append(time)
                    elif lon != lon_str_list[-1] or lat != lat_str_list[-1] or alt != alt_str_list[-1]:
                        lon_str_list.append(lon)
                        lat_str_list.append(lat)
                        alt_str_list.append(alt)
                        time_str_list.append(time)
        
        coord_list = []
        for i in range(len(lon_str_list)):
            lon = float(lon_str_list[i])
            lat = float(lat_str_list[i])
            if alt_str_list[i] != None:
                alt = float(alt_str_list[i])
            else:
                alt = alt_str_list[i]
            if time_str_list[i] != None:
                time = datetime.fromisoformat(time_str_list[i])
            else:
                time = time_str_list[i]
            loc = Location(lon, lat)
            coord = Coordinate(loc, time, alt, system=System.wgs84)
            coord_list.append(coord)
        
        # 现在都是以时间间隔制作轨迹的，因此不用添加点了
        # # 增加点，防止热图上出现间隔；但是对于有时间信息的航班不增加点
        # has_time = False
        # for coord in coord_list:
        #     if coord.time != None:
        #         has_time = True
        #         break
        # if has_time == False:
        #     index = 0
        #     pre_coord = coord_list[index]
        #     while index != len(coord_list):
        #         cur_coord = coord_list[index]
        #         if cur_coord.distance(pre_coord) > MAX_SEPARATION:
        #             coord_list.insert(index, cur_coord.middle(pre_coord))
        #         else:
        #             pre_coord = cur_coord
        #             index += 1
        
        _coords = np.array(coord_list)
        return cls(_coords)
    
    @classmethod
    def gpx(cls, file: str, MAX_SEPARATION: float | None = None):
        """从设备记录的 gpx 文件获取位置信息"""
        # 不再需要添加轨迹点了
        # 当 gpx 文件描述的是 GPX Studio 绘制的路线时，需要指定 MAX_SEPARATION
        # 使轨迹点的最大间距为 100 m
        
        coord_list = []
        with open(file, 'r', encoding='utf-8') as f:
            gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    loc = Location(point.longitude, point.latitude)
                    coord = Coordinate(loc, point.time, point.elevation)
                    coord_list.append(coord)
        
        if MAX_SEPARATION != None:
            index = 0
            pre_coord = coord_list[index]
            while index != len(coord_list):
                cur_coord = coord_list[index]
                if cur_coord.distance(pre_coord) > MAX_SEPARATION:
                    coord_list.insert(index, cur_coord.middle(pre_coord))
                else:
                    pre_coord = cur_coord
                    index += 1
        
        _coords = np.array(coord_list)
        return cls(_coords)
    
    @classmethod
    def fit(cls, file: str):
        """
        从设备记录的 fit 文件获取位置信息
        TODO: 佳明在信号较弱时会报告估计的虚假坐标，如何鉴别这些虚假坐标？
        TODO: Strava 在信号较弱时会报告误差超过 10 km 的坐标，并且偶尔会出现完全偏离轨迹的坐标
        """
        PRECISION = 0.0000000001 # 0.00001m
        coord_list = []
        fit_file = FitFile(file)
        # Get all data messages that are of type record
        for record in fit_file.get_messages('record'):
            # Go through all the data entries in this record
            lon, lat, time, ele = [None, None, None, None]
            for record_data in record:
                if record_data.name == 'position_long':
                    lon = record_data.value
                if record_data.name == 'position_lat':
                    lat = record_data.value
                # fit 文件里面存储的 datetime 对象没有时区信息，因此要手动加上
                if record_data.name == 'timestamp':
                    time = datetime.fromisoformat(str(record_data.value) + 'Z')
                # 优先使用 enhanced_altitude
                if record_data.name == 'enhanced_altitude':
                    ele = record_data.value
                if record_data.name == 'altitude':
                    if ele == None:
                        ele = record_data.value
            if lon != None and lat != None:
                lon *= ( 180.0 / 2**31 )
                lat *= ( 180.0 / 2**31 )
                loc = Location(lon, lat)
                coord = Coordinate(loc, time, ele)
                if not coord_list:
                    coord_list.append(coord)
                elif coord.distance(coord_list[-1]) > PRECISION:
                    coord_list.append(coord)
        
        """
        用 strava 记录的 fit 文件可能会出现相邻的 coord 具有相同的时间
        具有相同时间的 coord 坐标位置是飘忽不定的，因此这里合并具有相同时间的 coord
        """
        # 每一个循环处理一个 coord 片段，该片段中的 coord 具有相同的时间
        while True:
            coord_segment = []
            # 第一个循环先找到 coord 片段的开头
            pre_coord = coord_list[0]
            index = 1
            while index != len(coord_list):
                coord = coord_list[index]
                if coord.time == pre_coord.time:
                    break
                pre_coord = coord
                index += 1
            if index == len(coord_list):
                break
            start = index - 1
            # 第二个循环读取具有相同时间的 coord 片段
            time = coord_list[start].time
            coord_segment.append(coord_list[start])
            index = start + 1
            while index != len(coord_list):
                coord = coord_list[index]
                if coord.time == time:
                    coord_segment.append(coord)
                    index += 1
                else:
                    break
            end = index
            # 第三个循环对 coord 片段中的坐标求平均
            sum_lon = 0
            sum_lat = 0
            sum_ele = 0
            n_ele = 0
            for coord in coord_segment:
                sum_lon += coord.lon
                sum_lat += coord.lat
                if coord.ele != None:
                    sum_ele += coord.ele
                    n_ele += 1
            avg_lon = sum_lon / (end - start)
            avg_lat = sum_lat / (end - start)
            if n_ele == 0:
                avg_ele = None
            else:
                avg_ele = sum_ele / n_ele
            avg_loc = Location(lon=avg_lon, lat=avg_lat)
            avg_coord = Coordinate(avg_loc, time, avg_ele)
            # 最后删除 coord_list 中的片段并将平均 coord 添加进去
            n = end - start
            for i in range(n):
                del coord_list[start]
            coord_list.insert(start, avg_coord)
            
        _coords = np.array(coord_list)
        return cls(_coords)
    
    @classmethod
    def tcx(cls, file: str):
        """从设备记录的 tcx 文件获取位置信息"""
        """
        当设备收不到就 GPS 信号时，可能会在 tcx 文件中写入最后收到的 GPS 坐标，
        这会导致 tcx 文件中的坐标长时间静止，直到探测到 GPS 信号后，在短时间内移动大量距离
        可以在读入时删掉连续的相同坐标，这样做不会误删真正静止的测量结果，
        因为即使是真正静止，测量到的坐标也总是在误差范围内变化的
        """
        PRECISION = 0.0000000001 # 0.00001m
        coord_list = []
        tcx_reader = TCXReader()
        data = tcx_reader.read(file)
        for track_point in data.trackpoints:
            lon = track_point.longitude
            lat = track_point.latitude
            if lon != None and lat != None:
                loc = Location(lon, lat)
                time = track_point.time
                coord = Coordinate(loc, time)
                if not coord_list:
                    coord_list.append(coord)
                elif coord.distance(coord_list[-1]) > PRECISION:
                    coord_list.append(coord)
        _coords = np.array(coord_list)
        return cls(_coords)
    
    @classmethod
    def add_points(cls, poly):
        """
        对于有时间但间隔过大的 poly 段添加坐标
        """
        for coord in poly._coords:
            if not coord.time:
                print("ERROR: Some coordinates don't have time.")
                sys.exit()
            elif coord.time.microsecond != 0:
                print("ERROR: Some time aren't in integral seconds.")
                sys.exit()
        
        interval = 1 # 允许的最大时间间隔为 1 s
        coord_list = []
        pre_coord = poly._coords[0]
        for coord in poly._coords:
            time_diff = round((coord.time - pre_coord.time).total_seconds())
            if time_diff > interval:
                for i in range(1, time_diff):
                    percent = i / time_diff
                    lon = pre_coord.lon + (coord.lon - pre_coord.lon) * percent
                    lat = pre_coord.lat + (coord.lat - pre_coord.lat) * percent
                    time = pre_coord.time + timedelta(seconds=i)
                    if pre_coord.ele and coord.ele:
                        ele = pre_coord.ele + (coord.ele - pre_coord.ele) * percent
                    else:
                        ele = None
                    if pre_coord.heart_rate and coord.heart_rate:
                        heart_rate = pre_coord.heart_rate + (coord.heart_rate - pre_coord.heart_rate) * percent
                    else:
                        heart_rate = None
                    add_coord = Coordinate(Location(lon, lat), time, ele, heart_rate)
                    coord_list.append(add_coord)
            coord_list.append(coord)
            pre_coord = coord
            
        return cls(np.array(coord_list))
    
    @classmethod
    def add_times(cls, poly, start_time: datetime, end_time: datetime):
        """
        根据提供的起始和结束时间，为完全无时间的坐标添加时间信息
        仅添加整数时刻，因此会略微修改坐标的位置
        """
        # 提供的时间必须是整数秒，并且结束时间晚于起始时间
        if start_time.microsecond != 0 or end_time.microsecond != 0:
            print("ERROR: Start time or end time aren't in integral seconds.")
            sys.exit()
        elif start_time >= end_time:
            print("ERROR: Start time later than end time!")
            sys.exit()
        
        # 坐标列表中各个点的里程
        accumulate_distances = []
        accumulate_distance = 0
        pre_coord = poly._coords[0]
        for coord in poly._coords:
            accumulate_distance += coord.distance_meter(pre_coord)
            accumulate_distances.append(accumulate_distance)
            pre_coord = coord
        
        # 获取平均速度
        time_interval = int((end_time - start_time).total_seconds())
        speed = accumulate_distances[-1] / time_interval
        
        # 获取每一秒的坐标
        coord_list = []
        coord = Coordinate.add_attr(poly._coords[0], start_time)
        coord_list.append(coord)
        point = 0
        for i in range(1, time_interval):
            distance = i * speed
            while distance > accumulate_distances[point]:
                point += 1
            percent = (distance - accumulate_distances[point-1]) / (accumulate_distances[point] - accumulate_distances[point-1])
            lon = poly._coords[point-1].lon + (poly._coords[point].lon - poly._coords[point-1].lon) * percent
            lat = poly._coords[point-1].lat + (poly._coords[point].lat - poly._coords[point-1].lat) * percent
            if poly._coords[point-1].ele and poly._coords[point].ele:
                ele = poly._coords[point-1].ele + (poly._coords[point].ele - poly._coords[point-1].ele) * percent
            else:
                ele = None
            if poly._coords[point-1].heart_rate and poly._coords[point].heart_rate:
                heart_rate = poly._coords[point-1].heart_rate + (poly._coords[point].heart_rate - poly._coords[point-1].heart_rate) * percent
            else: 
                heart_rate = None
            if poly._coords[point-1].sequence and poly._coords[point].sequence:
                sequence = poly._coords[point-1].sequence + (poly._coords[point].sequence - poly._coords[point-1].sequence) * percent
            else:
                sequence = None
            if poly._coords[point-1].percent and poly._coords[point].percent:
                poly_percent = poly._coords[point-1].percent + (poly._coords[point].percent - poly._coords[point-1].percent) * percent
            else:
                poly_percent = None
            time = start_time + timedelta(seconds=i)
            coord = Coordinate(Location(lon, lat), time, ele, heart_rate, sequence, poly_percent)
            coord_list.append(coord)
        coord = Coordinate.add_attr(poly._coords[-1], end_time)
        coord_list.append(coord)
        
        return cls(np.array(coord_list))
                
        
        # TODO: 使用 add_percent 函数来改进该函数
        # 没有调整原坐标位置，因此添加的时间都不是整数
        # acc_dists = []
        # acc_dist = 0
        # pre_coord = self._coords[0]
        # for coord in self._coords:
        #     acc_dist += coord.distance(pre_coord) 
        #     acc_dists.append(acc_dist)
        #     pre_coord = coord
        # total_dist = acc_dists[-1]
        # percents = [acc_dist/total_dist for acc_dist in acc_dists]
        # time_interval = end_time - start_time
        # times = [start_time+time_interval*percent for percent in percents]
        
        # coord_list = []
        # for i in range(len(self._coords)):
        #     coord = Coordinate.add_attr(self._coords[i], time=times[i])
        #     coord_list.append(coord)
        # self._coords = np.array(coord_list)
    
    @classmethod
    def compensate_time(cls, poly, start: datetime=None, end: datetime=None):
        """
        为一条部分拥有时间的 PolyLine 补充时间，仅处理整秒的情况
        工作内容包括：
            验证所有时间都是整秒的，并且没有出现时间倒流
            根据现有时间计算全程的平均速度
            获取起点和终点的时刻：
                如果起点和终点自身带有时刻，则使用其自身带有的时刻
                如果不带有时刻则使用形参提供的时刻
                如果都没有则使用平均速度计算所处的时刻，精确到 1 s
            使用 add_times() 函数给中间不含时间的坐标补充时间
            使用 add_points() 函数给间隔过大的点之间插入新的点
            最后验证输出的 PolyLine 没有出现时间倒序
        """
        '''提取出所有坐标，避免在输入的对象上操作'''
        coord_list = []
        for coord in poly._coords:
            coord_list.append(coord)
        
        '''如果起点和终点自带时间，就忽略提供的时间'''
        if coord_list[0].time:
            start = None
        if coord_list[-1].time:
            end = None
        
        '''验证所有时间都是整秒'''
        if start:
            if start.microsecond != 0:
                print("ERROR: Start time aren't in integral seconds.")
                sys.exit()
        if end:
            if end.microsecond != 0:
                print("ERROR: End time aren't in integral seconds.")
                sys.exit()
        for coord in coord_list:
            if coord.time:
                if coord.time.microsecond != 0:
                    print("ERROR: Some coord aren't in integral seconds.")
                    sys.exit()
        
        '''验证时间没有出现倒流'''
        if start:
            pre_time = start
        else:
            pre_time = datetime.fromisoformat('1999-11-03T00:00:00Z')
        for coord in coord_list:
            if coord.time:
                if coord.time <= pre_time:
                    print("ERROR: Time back flow!")
                    sys.exit()
                pre_time = coord.time
        if end:
            if end <= pre_time:
                print("ERROR: Time back flow!")
                sys.exit()
        
        '''计算全程的平均速度'''
        accumulate_distances = []
        accumulate_distance = 0
        pre_coord = coord_list[0]
        for coord in coord_list:
            accumulate_distance += coord.distance_meter(pre_coord)
            accumulate_distances.append(accumulate_distance)
            pre_coord = coord
        if start and end:
            time_interval = (end - start).total_seconds()
            distance = accumulate_distances[-1]
        elif start and not end:
            i = 0
            while i != len(coord_list):
                if coord_list[i].time:
                    end_time = coord_list[i].time
                    end_i = i
                i += 1
            time_interval = (end_time - start).total_seconds()
            distance = accumulate_distances[end_i]
        elif not start and end:
            i = 0
            while i != len(coord_list):
                if coord_list[i].time:
                    start_time = coord_list[i].time
                    start_i = i
                    break
                i += 1
            time_interval = (end - start_time).total_seconds()
            distance = accumulate_distances[-1] - accumulate_distances[start_i]
        else:
            i = 0
            while i != len(coord_list):
                if coord_list[i].time:
                    start_time = coord_list[i].time
                    start_i = i
                    i += 1
                    break
                i += 1
            while i != len(coord_list):
                if coord_list[i].time:
                    end_time = coord_list[i].time
                    end_i = i
                i += 1
            time_interval = (end_time - start_time).total_seconds()
            distance = accumulate_distances[end_i] - accumulate_distances[start_i]
        speed = distance / time_interval
        
        '''给起点和终点补充时间'''
        if coord_list[0].time:
            pass
        elif start:
            coord_list[0] = Coordinate.add_attr(coord_list[0], time=start)
        else:
            i = 0
            while i != len(coord_list):
                if coord_list[i].time:
                    time_1 = coord_list[i].time
                    i_1 = i
                    break
                i += 1
            distance_1 = accumulate_distances[i_1]
            time_interval_1 = round(distance_1 / speed)
            start_time = time_1 - timedelta(seconds=time_interval_1)
            coord_list[0] = Coordinate.add_attr(coord_list[0], time=start_time)
        if coord_list[-1].time:
            pass
        elif end:
            coord_list[-1] = Coordinate.add_attr(coord_list[-1], time=end)
        else:
            i = 0
            while i != len(coord_list):
                if coord_list[i].time:
                    time_2 = coord_list[i].time
                    i_2 = i
                i += 1
            distance_2 = accumulate_distances[-1] - accumulate_distances[i_2]
            time_interval_2 = round(distance_2 / speed)
            end_time = time_2 + timedelta(seconds=time_interval_2)
            coord_list[-1] = Coordinate.add_attr(coord_list[-1], time=end_time)
        
        '''使用 add_times() 函数给中间不含时间的坐标补充时间'''
        while True:
            # 先寻找是否还有缺少时间的坐标点，如果没有了就结束循环
            finished = True
            for coord in coord_list:
                if coord.time == None:
                    finished = False
                    break
            if finished == True:
                break
            # 寻找第一个缺少时间的坐标点片段的索引
            index = 0
            while index != len(coord_list):
                if coord_list[index].time == None:
                    break
                index += 1
            start = index # 片段中第一个没有时间的坐标
            while index != len(coord_list):
                if coord_list[index].time != None:
                    break
                index += 1
            end = index # 片段之后第一个有时间的坐标
            # 利用 Coordinate.add_times() 备选构造函数重新构造一段 PolyLine
            no_time_list = []
            index = start - 1
            while index != end + 1:
                no_time_list.append(coord_list[index])
                index += 1
            no_time_poly = PolyLine(np.array(no_time_list))
            time_poly = PolyLine.add_times(no_time_poly, no_time_list[0].time, no_time_list[-1].time)
            time_list = [coord for coord in time_poly._coords]
            # 删除 coord_list 中缺少时间的坐标，将添加好时间的坐标写入 coord_list
            del coord_list[start - 1:end + 1]
            for coord in time_list[::-1]:
                coord_list.insert(start - 1, coord)
        
        '''验证 PolyLine 没有出现时间倒序'''
        pre_time = datetime.fromisoformat('1999-11-03T00:00:00Z')
        for coord in coord_list:
            if coord.time <= pre_time:
                print("ERROR: Time back flow after compensate_time() function!")
                sys.exit()
            pre_time = coord.time
        
        '''给时间间隔过大的点补充中间点'''
        coord_poly = cls(np.array(coord_list))
        return cls.add_points(coord_poly)
    
    @classmethod
    def combine(cls, FlightAware, VariFlight):
        """
        将 FlightAware 和 VariFlight 记录的数据合并
        放弃 VariFlight 的时间信息，仅选用其位置信息
        根据到当前坐标的距离来判断下一个点是位于哪个集合中
        最后补全时间位置信息，并精确到秒
        """
        # 按照距离信息来选择点的插入顺序，在首尾插入的 VariFlight 就不要删除时间了
        coord_list = []
        if FlightAware._coords[0].time <= VariFlight._coords[0].time:
            coord_list.append(FlightAware._coords[0])
            i = 1
            j = 0
        else:
            coord_list.append(VariFlight._coords[0])
            i = 0
            j = 1
        while True:
            if i == len(FlightAware._coords) and j == len(VariFlight._coords):
                break
            elif i == len(FlightAware._coords) and j != len(VariFlight._coords):
                coord_list.append(VariFlight._coords[j])
                j += 1
            elif i != len(FlightAware._coords) and j == len(VariFlight._coords):
                coord_list.append(FlightAware._coords[i])
                i += 1
            else:
                point_F = FlightAware._coords[i]
                point_V = VariFlight._coords[j].del_time()
                to_F = coord_list[-1].distance_meter(point_F)
                to_V = coord_list[-1].distance_meter(point_V)
                if to_F < to_V:
                    coord_list.append(point_F)
                    i += 1
                else:
                    coord_list.append(point_V)
                    j += 1
        if len(FlightAware._coords) + len(VariFlight._coords) != len(coord_list):
            print('ERROR: The combine() function in Polyline class is wrong!')
            sys.exit()
        pre_time = coord_list[0].time
        for coord in coord_list:
            if coord.time:
                if coord.time < pre_time:
                    print('ERROR: Time backflow, re-cording the combine() function!')
                    sys.exit()
                else:
                    pre_time = coord.time
        
        # 给缺少时间的坐标补充时间 (TODO: 写成函数，在 repair 函数中也能用)
        # 仅补充整数的时刻，因此实际会调整坐标的位置
        while True:
            # 先寻找是否还有缺少时间的坐标点，如果没有了就结束循环
            finished = True
            for coord in coord_list:
                if coord.time == None:
                    finished = False
                    break
            if finished == True:
                break
            # 寻找第一个缺少时间的坐标点片段的索引
            index = 0
            while index != len(coord_list):
                if coord_list[index].time == None:
                    break
                index += 1
            start = index # 片段中第一个没有时间的坐标
            while index != len(coord_list):
                if coord_list[index].time != None:
                    break
                index += 1
            end = index # 片段之后第一个有时间的坐标
            # 利用 Coordinate.add_times() 备选构造函数重新构造一段 PolyLine
            no_time_list = []
            index = start - 1
            while index != end + 1:
                no_time_list.append(coord_list[index])
                index += 1
            no_time_poly = PolyLine(np.array(no_time_list))
            time_poly = PolyLine.add_times(no_time_poly, no_time_list[0].time, no_time_list[-1].time)
            time_list = [coord for coord in time_poly._coords]
            # 删除 coord_list 中缺少时间的坐标，将添加好时间的坐标写入 coord_list
            del coord_list[start - 1:end + 1]
            for coord in time_list[::-1]:
                coord_list.insert(start - 1, coord)
        
        # 给时间间隔过大的点补充中间点
        coord_poly = cls(np.array(coord_list))
        return PolyLine.add_points(coord_poly)
            
        
        # # 寻找 FlightAware 和 VariFlight 中距离小于 1 m 的点
        # less_distance = 1 # 两个文件中挑出相距小于 1 m 的点
        # coord1_list = []
        # coord2_list = []
        # time_diff = []
        # distance_list = []
        # for coord1 in track1._coords:
        #     min_distance = 10000000
        #     min_coord2 = None
        #     for coord2 in track2._coords:
        #         distance = coord1.distance_meter(coord2)
        #         if distance < min_distance:
        #             min_distance = distance
        #             min_coord2 = coord2
        #     if min_distance < less_distance:
        #         coord1_list.append(coord1)
        #         coord2_list.append(min_coord2)
        #         time_diff.append((min_coord2.time-coord1.time).total_seconds())
        #         distance_list.append(min_distance)
        
        # i = 0
        # while i != len(coord1_list):
        #     print()
        #     print(f'Distance: {distance_list[i]} m, Time Difference: {time_diff[i]}')
        #     print(f'Time for Track1: {coord1_list[i].time}')
        #     print(f'Time for Track2: {coord2_list[i].time}')
        #     i += 1
        
        
        
        # coord_list.sort(key=lambda coord: coord.time)
        
        # # 删除具有相同时间的点，直接删除后者就行了，因为原则上都是从同一个设备上获取的数据，因此相同时间的位置不会有多大差别
        # # 其实并不是，位置误差不大，都在同一个轨迹上，但是两者时间误差很大
        # # 目前和 Strava 的测量结果比较认为 FlightAware 的时间是基本准确的，而 VariFlight 的时间误差可能有 30 s
        # # 但是 VariFlight 的轨迹测量间隔较短，只有 10 s 左右，而 FlightAware 的间隔有 30 s 左右
        # i = 1
        # while i != len(coord_list):
        #     if coord_list[i].time == coord_list[i-1].time:
        #         # print(f'Same time {coord_list[i].time}: {coord_list[i-1].distance_meter(coord_list[i])}')
        #         del coord_list[i]
        #     else:
        #         i += 1
        
        # _coords = np.array(coord_list)
        # return cls(_coords)
    
    # 外部函数
    def missing(self):
        """
        输出相邻两时刻之间大于 2 s 且间隔大于 100 m 的情况
        
        Strava 是平均以 1 s 为间隔记录的，但是并不一定在整秒进行记录
        可能是在 10.3 s 和 11.8 s 进行记录，因此四舍五入存储后就会缺少 11 s 时刻的记录
        这种情况是正常的，不需要处理，只有时间间隔大于 2 s 才表明信号出现了丢失
        
        当时间间隔大于 2 s 而距离小于 100 m 时，说明飞机速度小于 180 km/h
        此时一定是位于地面的，这种情况下即使增加点也没有效果，只能徒增工作量
        """
        TIME_INTERVAL = 2
        DISTANCE_INTERVAL = 100
        start_time = self._coords[0].time
        end_time = self._coords[-1].time
        coord_list = []
        if start_time == None or end_time == None:
            print("ERROR: A no time polyline, can't find missing time!")
            sys.exit()
        elif start_time > end_time:
            print('ERROR: Start time later than end time!')
            sys.exit()
        else:
            for coord in self._coords:
                if coord.time != None:
                    coord_list.append(coord)
                else:
                    print("ERROR: some middle point don't have time!")
                    sys.exit()
        print(f'Start Time: {start_time}')
        print(f'End Time: {end_time}')
        print()
        
        pre_coord = coord_list[0]
        interval_list = []
        for coord in coord_list:
            time = coord.time - pre_coord.time
            if time > timedelta(seconds=TIME_INTERVAL):
                distance = int(coord.distance_meter(pre_coord))
                if distance > DISTANCE_INTERVAL:
                    print(f'({time}, {distance} m) ({pre_coord.time.time()}, {pre_coord.lon}, {pre_coord.lat}) --> ({coord.time.time()}, {coord.lon}, {coord.lat})')
                    interval_list.append((pre_coord.time, coord.time))
            pre_coord = coord
        return interval_list
    
    def add_point(self, interval_list: list):
        """
        根据提供的时间段列表，在这些时间段的起始点之间以整秒间隔添加直线匀速的点
        函数返回一个 PolyLine 对象用于进行画图比较
        """
        for interval in interval_list:
            if interval[0].microsecond != 0 or interval[1].microsecond != 0:
                print('ERROR: The time must be integral in seconds!')
                sys.exit()
            elif interval[1] <= interval[0]:
                print('ERROR: The second is earlier than the first time!')
                sys.exit()
        
        i = 1
        coord_list = []
        append_list = []
        for interval in interval_list:
            find = False
            while i != len(self._coords):
                coord1 = self._coords[i - 1]
                coord2 = self._coords[i]
                if coord1.time == interval[0] and coord2.time == interval[1]:
                    find = True
                    # 在这两个 coord 之间均匀插入 coord
                    lon_diff = coord2.lon - coord1.lon
                    lat_diff = coord2.lat - coord1.lat
                    ele_diff = coord2.ele - coord1.ele
                    time_diff = (coord2.time - coord1.time).total_seconds()
                    coord_list.append(coord1)
                    if not append_list or coord1.time != append_list[-1].time:
                        append_list.append(coord1)
                    time = 1
                    while time != time_diff:
                        lon = coord1.lon + time/time_diff * lon_diff
                        lat = coord1.lat + time/time_diff * lat_diff
                        ele = coord1.ele + time/time_diff * ele_diff
                        coord = Coordinate(Location(lon, lat), coord1.time + timedelta(seconds=time), ele)
                        coord_list.append(coord)
                        append_list.append(coord)
                        time += 1
                    i += 1
                    break
                else:
                    coord_list.append(coord1)
                    i += 1
            append_list.append(self._coords[i - 1])
            if find == False:
                print(f"ERROR: Didn't find {interval[0]} and {interval[1]}")
                print('       or no continuous time interval.')
                sys.exit()
        while i != len(self._coords) + 1:
            coord_list.append(self._coords[i - 1])
            i += 1
        
        self._coords = np.array(coord_list)
        return PolyLine(np.array(append_list))
        
    
    def speed(self):
        """计算全程的平均速度，单位是：经纬度/s"""
        total_distance = 0
        pre_coord = self._coords[0]
        for coord in self._coords:
            total_distance += coord.distance(pre_coord)
            pre_coord = coord
        
        if self._coords[0].time != None and self._coords[-1].time != None:
            t1 = self._coords[0].time
            t2 = self._coords[-1].time
            total_time = (t2 - t1).total_seconds()
        else:
            print('ERROR: can\'t calculate speed without time information!')
            sys.exit()
        
        return total_distance / total_time
    
    def add_percent(self):
        """为坐标点添加 percent 属性"""
        accumulate_list = []
        accumulate = 0
        pre_coord = self._coords[0]
        for coord in self._coords:
            accumulate += coord.distance(pre_coord) 
            accumulate_list.append(accumulate)
            pre_coord = coord
        total_distance = accumulate_list[-1]
        percents = [accumulate / total_distance
                    for accumulate in accumulate_list]
        # 有的点可能因为计算误差导致 percent 大于 1, 需要手动调整为 1
        for index in range(len(percents)):
            if percents[index] > 1:
                percents[index] = 1
        
        coord_list = []
        for i in range(len(self._coords)):
            coord = Coordinate.add_attr(self._coords[i], percent=percents[i])
            coord_list.append(coord)
        self._coords = np.array(coord_list)
    
    def add_sequence(self):
        """
        为坐标点添加sequence 属性，在这里直接添加的 sequence 类型都是 int
        后面再添加新的坐标的 sequence 类型就是 float
        """
        coord_list = []
        for i in range(len(self._coords)):
            seq_coord = Coordinate.add_attr(self._coords[i], sequence=i)
            coord_list.append(seq_coord)
        self._coords = np.array(coord_list)
    
    def analytical(self):
        """
        增加 PolyLine 的坐标点密度，设定模拟的解析线路精度
        用于和设备记录的 GPS 轨迹进行匹配
        添加的坐标中的 sequence 属性类型是 float
        """
        PRECISION = 0.00001 # 1m
        coord_list = list(self._coords)
        index = 0
        pre_coord = coord_list[index]
        while index != len(coord_list):
            cur_coord = coord_list[index]
            if cur_coord.distance(pre_coord) > PRECISION:
                coord_list.insert(index, cur_coord.middle(pre_coord))
            else:
                pre_coord = cur_coord
                index += 1
        self._anas = np.array(coord_list)
    
    def repair(self, poly, start: datetime=None, end: datetime=None):
        """根据 polyline, 对 self 中的轨迹进行修复"""
        
        """先用 nearest 方法找到首尾两个点匹配的轨迹点"""
        start_coord = self._coords[0]
        end_coord = self._coords[-1]
        start_repair = poly._anas[0]
        min_start = start_coord.distance(start_repair)
        end_repair = poly._anas[-1]
        min_end = end_coord.distance(end_repair)
        for coord in poly._anas:
            if start_coord.distance(coord) < min_start:
                start_repair = coord
                min_start = start_coord.distance(start_repair)
            if end_coord.distance(coord) < min_end:
                end_repair = coord
                min_end = end_coord.distance(end_repair)
        
        """将 poly 掐头去尾，得到新的 polyline"""
        coord_list = []
        for coord in poly._anas:
            if coord.sequence >= start_repair.sequence \
            and coord.sequence <= end_repair.sequence:
                coord_list.append(coord)
        coords = np.array(coord_list)
        polyline = PolyLine(coords)
        
        """给新的 polyline 中的坐标增加 percent 属性"""
        polyline.add_percent()
        
        """
        使用 percentage 方法找到 self 中所有点匹配的轨迹点
        内层使用 while 循环使得不需要对每个 coord 都做一遍 polyline 的循环
        polyline 中点的数量是巨大的，这样只做一遍 polyline 循环可以大大减少运算时间
        """
        coord_list = []
        index = 0
        for coord in self._coords:
            while index != len(polyline._coords):
                point = polyline._coords[index]
                if point.percent < coord.percent:
                    index += 1
                    continue
                else:
                    repair_coord = \
                        Coordinate.add_attr(point,
                                            time=coord.time,
                                            ele=coord.ele,
                                            heart_rate=coord.heart_rate)
                    coord_list.append(repair_coord)
                    break
        
        """给 coord_list 补上用于标定轨迹形状的 sequence 为整数的 point"""
        for point in poly._coords:
            index = 0
            while index != len(coord_list):
                coord = coord_list[index]
                if coord.sequence < point.sequence:
                    index += 1
                    continue
                elif coord.sequence == point.sequence:
                    break
                else:
                    coord_list.insert(index, point)
                    break
            # 如果 point 位于所有 coord 之后，也需要将 point 插入到末尾
            if index == len(coord_list):
                coord_list.append(point)
        
        """给 coord_list 中缺少时间的 coord 补充时间信息"""
        '''Version 1'''
        # # 这个方法不好，可能会导致后面的坐标点时间比前面的坐标点早
        # # 第一个循环从左往右，把 coord 左边具有时间点的情况解决掉
        # index = 0
        # while index != len(coord_list):
        #     coord = coord_list[index]
        #     if coord.time == None:
        #         if index == 0:
        #             pass
        #         elif coord_list[index - 1].time == None:
        #             pass
        #         else:
        #             left = coord_list[index - 1]
        #             distance = left.distance(coord)
        #             d_time = distance / speed
        #             time = left.time + timedelta(seconds=d_time)
        #             coord_list[index] = Coordinate.add_attr(coord, time=time)
        #     index += 1
        
        # # 第二个循环从右往左，把 coord 右边具有时间点的情况解决掉
        # index = -1
        # while index != -1 - len(coord_list):
        #     coord = coord_list[index]
        #     if coord.time == None:
        #         if index == -1:
        #             pass
        #         elif coord_list[index + 1].time == None:
        #             pass
        #         else:
        #             right = coord_list[index + 1]
        #             distance = right.distance(coord)
        #             d_time = distance / speed
        #             time = right.time - timedelta(seconds=d_time)
        #             coord_list[index] = Coordinate.add_attr(coord, time=time)
        #     index -= 1
        # """
        # 最后精修 coord_list 中的元素
        # 需要处理左边的 coord 时间比右边时间大的情况
        # 这种情况
        # 出现此问题就将两个点合并，loc 使用左边的点（添加的点）， 其他信息使用原始点
        # """
        # index = 0
        # while index != len(coord_list):
        #     if index == 0:
        #         pass
        #     else:
        #         if coord_list[index - 1].time > coord_list[index].time:
        #             coord_list[index - 1] = \
        #             Coordinate.add_attr(coord_list[index - 1],
        #                                 time=coord_list[index].time,
        #                                 ele=coord_list[index].ele,
        #                                 heart_rate=coord_list[index].heart_rate)
        #             del coord_list[index]
        #             continue
        #     index += 1
        
        
        # """
        # 实际上有很多 insert 进来的 poly 点也是不必要的，其作用只是为了精确描述出轨迹
        # 如果原始的点本身就比较接近（比如每间隔 1 s 都有测量值），
        # 那么 insert 进来的 poly 点就有点多余
        # 因此考虑如果相邻点的时间间隔小于 1 s，就进行合并，不小于 1 s 的话就取整
        # """
        # index = 0
        # while index != len(coord_list):
        #     coord = coord_list[index]
        #     if coord.time.microsecond != 0:
        #         if 
            
            
        #     index += 1
        
        
        '''Version 2, 标定轨迹的点会导致非整秒时间'''
        # speed = self.speed()
        
        # # 第一个循环解决开头没有时间的问题
        # index = 0
        # if coord_list[index].time == None:
        #     # 先找到第一个拥有时间的点
        #     while index != len(coord_list):
        #         if coord_list[index].time != None:
        #             break
        #         index += 1
        #     # 再依次往回赋予时间
        #     index -= 1
        #     while index != -1:
        #         coord = coord_list[index]
        #         right = coord_list[index + 1]
        #         distance = coord.distance(right)
        #         d_time = distance / speed
        #         time = right.time - timedelta(seconds=d_time)
        #         coord_list[index] = Coordinate.add_attr(coord, time=time)
        #         index -= 1
        
        # # 第二个循环解决结尾没有时间的问题
        # index = len(coord_list) - 1
        # if coord_list[index].time == None:
        #     # 先找到第一个拥有时间的点
        #     while index != -1:
        #         if coord_list[index].time != None:
        #             break
        #         index -= 1
        #     # 再依次往回赋予时间
        #     index += 1
        #     while index != len(coord_list):
        #         coord = coord_list[index]
        #         left = coord_list[index - 1]
        #         distance = coord.distance(left)
        #         d_time = distance / speed
        #         time = left.time + timedelta(seconds=d_time)
        #         coord_list[index] = Coordinate.add_attr(coord, time=time)
        #         index += 1
        
        # # 第三个循环解决中间没有时间的问题
        # while True:
        #     # 先寻找是否还有缺少时间的坐标点，如果没有了就结束循环
        #     finished = True
        #     for coord in coord_list:
        #         if coord.time == None:
        #             finished = False
        #             break
        #     if finished == True:
        #         break
        #     # 寻找第一个缺少时间的坐标点片段的索引
        #     index = 0
        #     while index != len(coord_list):
        #         if coord_list[index].time == None:
        #             break
        #         index += 1
        #     start = index
        #     while index != len(coord_list):
        #         if coord_list[index].time != None:
        #             break
        #         index += 1
        #     end = index
        #     # 利用 Coordinate.add_times() 方法给中间的点添加时间
        #     no_time_list = []
        #     index = start - 1
        #     while index != end + 1:
        #         no_time_list.append(coord_list[index])
        #         index += 1
        #     no_time_poly = PolyLine(np.array(no_time_list))
        #     no_time_poly.add_times(no_time_list[0].time, no_time_list[-1].time)
        #     time_list = [coord for coord in no_time_poly._coords]
        #     # 将添加好时间的坐标写入 coord_list
        #     index = start
        #     while index != end:
        #         coord_list[index] = time_list[index - start + 1]
        #         index += 1
        
        '''Version 3, 直接写在 compensate_time() 备选构造函数中'''
        self._coords = PolyLine.compensate_time(PolyLine(np.array(coord_list)), start, end)._coords

            
    '''Version 0, 最初的失败品'''
    # def repair(self, polyline):
    #     """
    #     根据 polyline, 对 self 中的轨迹进行修复
    #     先将 self 中的每个点匹配到 polyline_ana 中距离最近的点上
    #     """
    #     coords_measure = list(self._coords)
    #     coords_ana = list(polyline._anas)
    #     coords = []
    #     for coord in coords_measure:
    #         min_index = 0
    #         min_distance = coord.distance(coords_ana[min_index])
    #         index = 0
    #         while index != len(coords_ana):
    #             if coord.distance(coords_ana[index]) < min_distance:
    #                 min_index = index
    #                 min_distance = coord.distance(coords_ana[min_index])
    #             index += 1
    #         coord = Coordinate.change_loc(coord, coords_ana[min_index])
    #         coords.append(coord)
        
    #     """
    #     然后再往 self 点集合中插入 polyline._coords 中的点，以防 self 中的点有间断
    #     通过总距离的大小来判断应该将 polyline._coords 中的点插入到 self 中的位置
    #     考虑到 coords 的起点可能与 polyline._coords 不同，
    #     因此无论如何都要先把 polyline._coords 中的第一个点放到 coords 的第一个位置
    #     """
    #     # if coords
        
    #     reals_distance = 0
    #     pre_real = polyline._coords[0]
    #     for real in polyline._coords:
    #         reals_distance += real.distance(pre_real)
    #         index = 0
    #         coords_distance = 0
    #         pre_coord = coords[index]
    #         while index != len(coords):
    #             coords_distance += coords[index].distance(pre_coord)
    #             if reals_distance < coords_distance:
    #                 coords.insert(index, real)
    #                 break
    #             elif reals_distance == coords_distance:
    #                 break
    #             pre_coord = coords[index]
    #             index += 1
    #         # 如果 while 是正常结束的，就需要把 real 插入到 coords 的末尾
    #         if index == len(coords):
    #             coords.append(real)            
    #         pre_real = real

    #     """最后再给没有时间的 coord 点补充时间和高度信息"""
    #     # for coord in coords:
            
    #     self._coords = np.array(coords)
    
    @property
    def lon(self):
        return np.array([coord.lon for coord in self._coords])
    @property
    def lat(self):
        return np.array([coord.lat for coord in self._coords])
    @property
    def coord(self):
        return np.array([coord.coord for coord in self._coords])
    
    
        