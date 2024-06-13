"""
测试 validate 函数
    >>> d = dict{'polyline': '116,39;117,39;118,40'}
    >>> validate(d)
"""

def validate(busline: dict) -> bool:
    polyline = []
    for coord in busline['polyline'].split(';'):
        polyline.append(tuple(coord.split(',')))
    
    stations = []
    
    