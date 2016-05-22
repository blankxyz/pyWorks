# Embedded file name: /work/build/source/athena/utils/extractor/html_code.py
import re
import htmlentitydefs
import traceback
entitydefs = {'apos': u"'"}
for k, v in htmlentitydefs.name2codepoint.iteritems():
    entitydefs[k] = unichr(v)

html_special_re = re.compile('&(#?[xX]?(?:[0-9a-fA-F]+|\\w{1,8}));')

def replace_html(s):
    global entitydefs
    s = s.groups()[0]
    try:
        return entitydefs[s]
    except KeyError:
        return '&%s;' % s


def unescape_word(s):
    global html_special_re
    if '&' not in s:
        return s
    words = re.findall('&#(\\d+);', s)
    if words:
        result = s
        for r in words:
            word = unichr(int(r))
            result = result.replace('&#%s;' % r, word)

    else:
        result = s
    result = html_special_re.sub(replace_html, result)
    return result


code_re = re.compile('(?i)<meta[^>]*?charset=[\'"]{0,1}([\\w-]+)[^>]*?/?>')
codes = ['utf8', 'gbk', 'gb2312']

def get_code(html):
    code = code_re.findall(html)
    if code:
        return code[0]


def auto_code(s):
    if isinstance(s, str):
        for code in codes:
            try:
                return s.decode(code)
            except:
                pass

        return s


def html_code(html):
    code = code_re.findall(html)
    if code:
        try:
            html = html.decode(code[0])
        except Exception as e:
            html = auto_code(html)

    else:
        html = auto_code(html)
    return html