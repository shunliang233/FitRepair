from enum import Enum

class PublicType(Enum):
    BUS = '普通公交 无轨电车 旅游专线 机场大巴 社区专车'
    METRO = '地铁 轻轨 有轨电车 磁悬浮列车'
    TRAIN = '高铁 动车 普快'
    OTHER = '轮渡 索道交通 其他'


