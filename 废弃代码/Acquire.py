"""
测试 acquire 函数
    >>> KEY = '0657aa0795e30e72c514b023dea7956a'
    >>> realID = '110100023099'
    >>> fakeID = '111111111111'
    >>> acquire(KEY, realID)['id']
    '110100023099'
    >>> acquire(KEY, realID)['name']
    '地铁2号线外环(西直门--西直门)'
    >>> acquire(KEY, fakeID)
    ERROR: No bus line with id: 111111111111
"""


import requests

def acquire(key: str, identity: str) -> dict | None:
    """根据 ID 搜索线路，以字典形式返回，如果没搜到就返回 None 并打印报错信息

    Args:
        key (str): _description_
        identity (str): _description_

    Returns:
        dict | None: _description_
    """

    # 固定的参数
    EXTENSIONS = 'all'
    url = 'https://restapi.amap.com/v3/bus/lineid?parameters'

    # 获取线路查询
    params = {
        'key': key,
        'id': identity,
        'extensions': EXTENSIONS}
    result = requests.get(url, params).json()
    
    # 简单判断是否查询成功
    if result['status'] == '1' and result['info'] == 'OK':
        if len(result['buslines']) != 0:
            return result['buslines'][0]
        else:
            print(f'ERROR: No bus line with id: {identity}')
    else:
        print('ERROR: Failed request!')