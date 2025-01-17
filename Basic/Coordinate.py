"""
测试 Coordinate 类
    >>> loc = Location(116.3706846, 39.8621346)
    >>> Coordinate(loc, system=System.wgs84)
"""


from dataclasses import dataclass
from enum import Enum, auto
import math
from datetime import datetime
import numpy as np

@dataclass
class Location:
    lon: float
    lat: float

def distance(loc1: Location, loc2: Location):
    return math.hypot(loc1.lon - loc2.lon, loc1.lat - loc2.lat)
def sub_loc(loc1: Location, loc2: Location):
    return Location(loc1.lon - loc2.lon, loc1.lat - loc2.lat)
def add_loc(loc1: Location, loc2: Location):
    return Location(loc1.lon + loc2.lon, loc1.lat + loc2.lat)
def mul_loc(loc: Location, num: float):
    return Location(loc.lon * num, loc.lat * num)

class System(Enum):
    wgs84 = auto()
    gcj02 = auto()

class Coordinate:
    """
    坐标对象，包含 GCJ02 和 WGS84 这两种坐标
    并且可以包含坐标对应的时间、高度信息
    """
    
    # wgs2gcj 用的克拉索夫斯基椭球参数
    GCJ_A = 6378245
    GCJ_EE = 0.00669342162296594323
    # gcj2wgs 用的计算精度控制
    G2W_Precision = 0.0001 / 111391.0 # 精度控制为小于 0.0001 m
    MaxIterations = 10
    
    
    def __init__(self, loc: Location,
                 time: datetime | None = None,
                 ele: float | None = None,
                 heart_rate: int | None = None,
                 sequence: float | None = None,
                 percent: int | float | None = None,
                 system: System=System.wgs84):
        """
        将 wgs84 和 gcj02 两个坐标都计算并存储下来，以便后续使用
        ele 和 time 即使没输入，也要存储下来, coord 特性输出的时候会判断是否有值
            sequence 是坐标在 polyline 中的位置，整数代表原始坐标，非整数代表后续添加的坐标
            percent 是坐标在 polyline 中的路程百分比
        """
        if system == System.wgs84:
            self._coord_wgs = loc
            self._coord_gcj = self._wgs2gcj(loc)
        elif system == System.gcj02:
            self._coord_wgs = self._gcj2wgs(loc)
            self._coord_gcj = loc
        self._time = time
        self._ele = ele
        self._heart_rate = heart_rate
        self._sequence = sequence
        self._percent = percent
    
    @classmethod
    def add_attr(cls, coord,
                 time: datetime | None = None,
                 ele: float | None = None,
                 heart_rate: int | None = None,
                 sequence: float | None = None,
                 percent: int | float | None = None):
        """
        给 coord 对象增加属性，返回增加属性后的 Coordinate 实例
        添加策略为：
                  如果备选构造函数提供了，就用备选构造函数中的值；
                  否则就使用 coord 中的原始值
        """
        _loc = Location(coord.lon, coord.lat)
        _time = coord.time
        _ele = coord.ele
        _heart_rate = coord.heart_rate
        _sequence = coord.sequence
        _percent = coord.percent
        if time != None:
            _time = time
        if ele != None:
            _ele = ele
        if heart_rate != None:
            _heart_rate = heart_rate
        if sequence != None:
            _sequence = sequence
        if percent != None:
            _percent = percent
        return cls(_loc, _time, _ele, _heart_rate, _sequence, _percent)
        
    # TODO: 删掉这个方法，可以用 add_attr 方法代替
    @classmethod
    def change_loc(cls, coord1, coord2):
        """将 coord1 的 loc 替换为 coord2 的"""
        loc = Location(coord2.lon, coord2.lat)
        return cls(loc, coord1._ele, coord1._time)
    
    """外部函数"""
    def distance(self, other):
        return math.hypot(self.lon - other.lon, self.lat - other.lat)
    
    def distance_meter(self, other):
        R = 6371004 # Radius of Earth
        d_lon = (self.lon - other.lon) * math.pi / 180
        d_lat = (self.lat - other.lat) * math.pi / 180
        lat1 = self.lat * math.pi / 180
        lat2 = other.lat * math.pi / 180
        a = math.sin(d_lat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(d_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
        return R * c
    
    def del_time(self):
        self._time = None
        return self
    
    def middle(self, other):
        """要注意 0 也是有意义的值，应当使条件成立"""
        lon = 0.5 * (self.lon + other.lon)
        lat = 0.5 * (self.lat + other.lat)
        loc = Location(lon, lat)
        if self._ele != None and other._ele != None:
            ele = 0.5 * (self._ele + other._ele)
        elif self._ele != None and other._ele == None:
            ele = self._ele
        elif self._ele == None and other._ele != None:
            ele = other._ele
        else:
            ele = None
        if self._time != None and other._time != None:
            time = other._time + 0.5 * (self._time - other._time)
        elif self._time != None and other._time == None:
            time = self._time
        elif self._time == None and other._time != None:
            time = other._time
        else:
            time = None
        if self._heart_rate != None and other._heart_rate != None:
            heart_rate = round(0.5 * (self._heart_rate + other._heart_rate))
        elif self._heart_rate != None and other._heart_rate == None:
            heart_rate = self._heart_rate
        elif self._heart_rate == None and other._heart_rate != None:
            heart_rate = other._heart_rate
        else:
            heart_rate = None
        if self._sequence != None and other._sequence != None:
            sequence = 0.5 * (self._sequence + other._sequence)
        elif self._sequence != None and other._sequence == None:
            sequence = self._sequence
        elif self._sequence == None and other._sequence != None:
            sequence = other._sequence
        else:
            sequence = None
        if self._percent != None and other._percent != None:
            percent = 0.5 * (self._percent + other._percent)
        elif self._percent != None and other._percent == None:
            percent = self._percent
        elif self._percent == None and other._percent != None:
            percent = other._percent
        else:
            percent = None
        return Coordinate(loc, time, ele, heart_rate, sequence, percent)
    
    """外部数据接口"""
    @property
    def time(self):
        return self._time
    @property
    def ele(self):
        return self._ele
    @property
    def heart_rate(self):
        return self._heart_rate
    @property
    def sequence(self):
        return self._sequence
    @property
    def percent(self):
        return self._percent
    
    @property
    def lon(self):
        return self._coord_wgs.lon
    @property
    def lat(self):
        return self._coord_wgs.lat
    @property
    def loc(self):
        return np.array([self.lon, self.lat])
    @property
    def coord(self):
        return np.array([self.lon, self.lat, self.time, self.ele, self.heart_rate])
    @property
    def lon_gcj(self):
        return self._coord_gcj.lon
    @property
    def lat_gcj(self):
        return self._coord_gcj.lat
    @property
    def loc_gcj(self):
        return np.array([self.lon_gcj, self.lat_gcj])
    @property
    def coord_gcj(self):
        if self._ele and self._time:
            return np.array([self.lon_gcj, self.lat_gcj, self._time, self._ele])
        elif self._ele:
            return np.array([self.lon_gcj, self.lat_gcj, self._ele])
        elif self._time:
            return np.array([self.lon_gcj, self.lat_gcj, self._time])
        else:
            return np.array([self.lon_gcj, self.lat_gcj])
    
    """特殊函数"""
    def __iter__(self):
        return (i for i in self.coord)
    
    def __str__(self):
        return str(tuple(self))

    """内部函数"""
    def _out_of_china(self, loc: Location) -> bool:
        return loc.lat < 0.8293 or loc.lat > 55.8271\
            or loc.lon < 72.004 or loc.lon > 137.8347
    
    def _wgs2gcj(self, wgs: Location):
        if self._out_of_china(wgs):
            return wgs
        
        x = wgs.lon - 105
        y = wgs.lat - 35

        dLat_m = -100.0 + 2.0*x + 3.0*y + 0.2*y*y + 0.1*x*y + \
                 0.2*math.sqrt(abs(x)) + \
                 (2.0*math.sin(x*6.0*math.pi) + 2.0*math.sin(x*2.0*math.pi) + \
                  2.0*math.sin(y*math.pi) + 4.0*math.sin(y/3.0*math.pi) + \
                  16.0*math.sin(y/12.0*math.pi) + \
                  32.0*math.sin(y/30.0*math.pi)) * 20.0 / 3.0
        dLon_m = 300.0 + x + 2.0*y + 0.1*x*x + 0.1*x*y + \
                 0.1*math.sqrt(abs(x)) + \
                 (2.0*math.sin(x*6.0*math.pi) + 2.0*math.sin(x*2.0*math.pi) + \
                  2.0*math.sin(x*math.pi) + 4.0*math.sin(x/3.0*math.pi) + \
                  15.0*math.sin(x/12.0*math.pi) + \
                  30.0*math.sin(x/30.0*math.pi)) * 20.0 / 3.0

        radLat = wgs.lat / 180.0 * math.pi
        magic = 1.0 - self.GCJ_EE*math.pow(math.sin(radLat), 2.0)

        lat_deg_arclen = (math.pi / 180.0) * (self.GCJ_A*(1.0 - self.GCJ_EE)) \
                         / math.pow(magic, 1.5)
        lon_deg_arclen = (math.pi / 180.0) * (self.GCJ_A * math.cos(radLat) \
                         / math.sqrt(magic))

        return Location(lon = wgs.lon + (dLon_m / lon_deg_arclen),
                        lat = wgs.lat + (dLat_m / lat_deg_arclen))
    
    def _gcj2wgs(self, gcj: Location):
        """
        考虑 gcj 是 wgs 的已知表达式的函数，即 gcj(wgs).
        该函数使 gcj(wgs) 和 wgs 相差 500 m 左右
        在 500m 的小范围内坐标变换基本上可以看作是平移相同的矢量：
            设 gcj(wgs) = wgs + x，
            则近似有 gcj(gcj(wgs)) = gcj(wgs + x) ≈ wgs + 2x
                ==> wgs ≈ 2 * gcj(wgs) - gcj(gcj(wgs))
                ==> wgs_1 = 2 * gcj(wgs) - gcj(gcj(wgs))
        由于 gcj(wgs) 是已知量，因此可以用该式求出 wgs 的近似值
        将近似解 wgs_1 带入 gcj() 函数，得到的 gcj_1 与 gcj 之差，
            视为误差第二次迭代的 wgs_2 与 wgs_1 之间的误差：
            d_1 = gcj - gcj(wgs_1)
                = wgs_2 - wgs_1
        再计算第二次迭代后的误差，并视为第三次迭代的 wgs_3 与 wgs_2 的误差：
            d_2 = gcj - gcj(wgs_2)
                = wgs_3 - wgs_2
        最终直到超过最大迭代次数，或者 gcj - gcj(wgs_n) 的误差小于指定精度，
            就把 wgs_n 当作 gcj 对应反解出的 wgs 坐标
        """
        wgs = sub_loc(mul_loc(gcj, 2.0), self._wgs2gcj(gcj))
        d = sub_loc(gcj, self._wgs2gcj(wgs))
        it = 1
        while it <= self.MaxIterations and (abs(d.lon) > self.G2W_Precision or abs(d.lat) > self.G2W_Precision):
            wgs = add_loc(wgs, d)
            d = sub_loc(gcj, self._wgs2gcj(wgs))
            it += 1
        return wgs