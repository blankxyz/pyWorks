#!/usr/bin python
# coding=utf-8
import requests
import json

# baidu_map_key = 'e9ospC88hj5iHoI9xUabaHFYAEiFXlRa'
baidu_map_key = '4119853f8e9c07a0eeaf89352b2c795d'


def convert_str_xy_to_x_y(str_x_y):
    '''
    Args:
        str_x_y: '39.983424_116.322987' or '39.983424,116.322987'
    Returns:
        (x,y)
    '''
    (x, y) = (None, None)
    if str_x_y != u'None' and len(str_x_y) > 0:
        sp = '_' if '_' in str_x_y else ','
        x = str_x_y.split(sp)[0]
        y = str_x_y.split(sp)[1]
    return (x, y)


def convert_xy_to_addressComponent(str_x_y):
    '''
    Args:
        str_x_y: '39.983424_116.322987'
    Returns:
            "addressComponent": {
                                  "country": "中国",
                                  "country_code": 0,
                                  "province": "北京市",
                                  "city": "北京市",
                                  "district": "海淀区",
                                  "adcode": "110108",
                                  "street": "中关村大街",
                                  "street_number": "27号1101-08室",
                                  "direction": "附近",
                                  "distance": "7"
                                },
    '''
    addressComponent = {"country": "",
                        "country_code": 0,
                        "province": "",
                        "city": "",
                        "district": "",
                        "adcode": "",
                        "street": "",
                        "street_number": "",
                        "direction": "",
                        "distance": ""
                        }
    (x, y) = convert_str_xy_to_x_y(str_x_y)
    if x:
        url = 'http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&' \
              'location=%s,%s&output=json&pois=0&ak=%s' % (x, y, baidu_map_key)

        # logger.format('[info] convert_xy_to_address() %s' % url)
        response = requests.get(url)
        content = response.content[len('renderReverse&&renderReverse('):-1]
        j = json.loads(content)
        addressComponent = j['result']['addressComponent']

    return addressComponent