from django import template
register = template.Library()


@register.filter(is_safe=True)
def domain_transfer(value):
    '''
    将www.sohu.com 转换为 www-sohu-com
    :param value:
    :param arg:
    :return:
    '''
    result = str(value).replace('.', '-')
    return result


@register.filter(name='delta_rank_data')
def delta_rank_data(delta, d):
    '''
    返回过滤后每个域名或配置的相关时间差数据
    :param delta:某个域名或配置时间差
    :param d:时间差1-9中的一个
    :return:
    '''
    result = delta['d' + str(d)]['cnt']
    return result


@register.filter(name='delta_custom_data')
def delta_custom_data(data, index):
    '''
    返回过滤后自定义时间差的数量值
    :param data:
    :param index:
    :return:
    '''
    result = data[index.encode('utf-8')]
    return result
