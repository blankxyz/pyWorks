

def convert_regex_format_keyword(rule):
    '''
    /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
    /news/\d{6}/[a-zA-Z]\d{8}_\d{6}.htm
    '''
    ret = ''
    digit = '\d'
    cnt = 0
    pos = 0
    temp = ''
    while pos <= len(rule):
        if rule[pos:pos + len(digit)] == digit:
            if temp.find(digit) < 0:
                ret = ret + temp
                temp = ''
                cnt = 0
            cnt = cnt + 1
            temp = '%s{%d}' % (digit, cnt)
            pos = pos + len(digit)
        elif pos == len(rule):
            ret = ret + temp
            break
        else:
            ret = ret + temp + rule[pos]
            temp = ''
            cnt = 0
            pos = pos + 1

    return ret

if __name__ == '__main__':
    convert_regex_format_keyword('http://bbs.tianya.cn/list-838-1.shtml')



