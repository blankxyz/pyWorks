# Embedded file name: /work/build/source/athena/utils/extractor/content.py
import sys
sys.setrecursionlimit(10000)
import re
import htmlentitydefs
import copy
import traceback
import time
import numpy as np
import max_sub_str
import html_code

def debug():
    print 'in debug function'


chinese_re = re.compile(u'[\u4e00-\u9fa5]+')
english_re = re.compile(u'(?i)[\\w]+')

def replace(re_object):
    return '\n'


def img_replace(re_object):
    if re_object is not None:
        return ''.join(re_object.groups())
    else:
        return ''
        return


def a_replace(re_object):
    if re_object.groups()[0].strip() or re_object.groups()[2].strip():
        return ''.join(re_object.groups())
    else:
        return '\n'


clean_tag_res = [(re.compile('<!--[\\s\\S]*?-->'), ''),
 (re.compile('(?i)<[\\s]*script[\\s\\S]+?</[\\s]*script[\\s]*>'), ''),
 (re.compile('(?i)<[\\s]*style[\\s\\S]+?((</[\\s]*style[\\s]*>)|(/\\s*>))'), ''),
 (re.compile('([^>]*?)<a[^>]*?>([\\s\\S]*?)</a>([^<]*?)'), a_replace),
 (re.compile('</?strong>'), '  '),
 (re.compile('(?i)</?br[\\s]*/?>'), ' '),
 (re.compile('<[^>]+?>'), '\n'),
 (re.compile('(?i)\\s*(http:[\\s\\S]*?\\.((bmp)|(jpg)|(jpeg)|(png)|(gif)))\\s*'), '\n'),
 (re.compile('\t+'), '')]

def clean_tag(data):
    global clean_tag_res
    text = data['html']
    for reg, new_s in clean_tag_res:
        text = reg.sub(new_s, text)

    return html_code.unescape_word(text.strip())


def clean_tag2(html):
    text = html
    for reg, new_s in clean_tag_res:
        text = reg.sub(new_s, text)

    return unescape_word(text.strip())


def get_lines(data):
    lines = data['text'].splitlines()
    result = []
    for line in lines:
        if line and (chinese_re.findall(line) or english_re.findall(line)):
            result.append(line.strip())
        else:
            result.append('')

    return result


modulus = 2

def get_line_score(l1, l2, score, lines, words):
    if l1 > l2:
        l1, l2 = l2, l1
    if score[l1][l2] == 0:
        if l1 == l2:
            score[l1][l2] = 0
        else:
            score[l1][l2] = max_sub_str.get_like(lines[words[l1]], lines[words[l2]]) * modulus - (words[l2] - words[l1])
    return score[l1][l2]


def get_group(l, score, lines, words, group = None):
    if not group:
        group = set([l])
    else:
        group.add(l)
    if l != 0:
        for i in range(l - 1, -1, -1):
            if i not in group:
                if get_line_score(i, l, score, lines, words) >= 0:
                    get_group(i, score, lines, words, group)
                elif i > 0 and get_line_score(i - 1, l, score, lines, words) >= 0:
                    get_group(i, score, lines, words, group)
                    get_group(i - 1, score, lines, words, group)
                else:
                    break

    if l != len(words):
        for j in range(l + 1, len(words)):
            if j not in group:
                if get_line_score(l, j, score, lines, words) >= 0:
                    get_group(j, score, lines, words, group)
                elif j < len(words) - 1 and get_line_score(l, j + 1, score, lines, words) >= 0:
                    get_group(j, score, lines, words, group)
                    get_group(j + 1, score, lines, words, group)
                else:
                    break

    return group


def content_text(data):
    text = data['text']
    lines = data['lines']
    words = []
    for line_num in range(len(lines)):
        if lines[line_num].strip():
            words.append(line_num)

    groups = []
    score = np.zeros((len(words), len(words)))
    found_line = set()
    for i in range(len(words)):
        if i not in found_line:
            nums = get_group(i, score, lines, words)
            found_line.update(nums)
            groups.append(nums)

    temp = []
    group_1 = groups.pop()
    group_2 = None
    while groups:
        group_2 = groups.pop()
        if len(group_1 & group_2) > 0:
            group_1.update(group_2)
        else:
            temp.append([])
            temp[-1].extend(group_1)
            temp[-1].sort()
            group_1 = group_2
    else:
        temp.append([])
        if group_2:
            temp[-1].extend(group_2)
            temp[-1].sort()

    temp.reverse()
    groups = temp
    groups_text = [ '\n'.join([ lines[words[line]] for line in group ]) for group in groups ]
    max_score = 0
    max_group_num = 0
    for i in range(len(groups_text)):
        score = float(len(groups_text[i]))
        score_coefficient = 1.0
        if data.has_key('title'):
            if isinstance(data['title'], str):
                data['title'] = html_code.auto_code(data['title'])
            if data['title'].strip() == groups_text[i].strip():
                score = 0
            else:
                pub_strs = max_sub_str.get_all_pub(data['title'], groups_text[i])
                pub_len = 0.0
                for pub_str in pub_strs:
                    pub_len += float(len(pub_str)) * float(data['title'].count(pub_str))

                score_coefficient += pub_len / float(len(data['title']))
        if data.has_key('summary'):
            if isinstance(data['summary'], str):
                data['summary'] = html_code.auto_code(data['summary'])
            pub_strs = max_sub_str.get_all_pub(data['summary'], groups_text[i])
            pub_len = 0.0
            for pub_str in pub_strs:
                pub_len += float(len(pub_str)) * float(data['summary'].count(pub_str))

            score_coefficient += pub_len / float(len(data['summary']))
        score *= score_coefficient
        if score > max_score:
            max_score = score
            max_group_num = i

    data['content'] = groups_text[max_group_num]
    data['content_start'] = words[groups[max_group_num][0]]
    data['content_end'] = words[groups[max_group_num][-1]]
    return


def get_content(data):
    if not data.has_key('html'):
        raise Exception('key:html \xe6\x9c\xaa\xe7\x9f\xa5!!')
    if isinstance(data['html'], str):
        data['html'] = html_code.html_code(data['html'])
    data['text'] = clean_tag(data)
    data['lines'] = get_lines(data)
    content_text(data)


if __name__ == '__main__':
    import down_load
    import title
    url = sys.argv[1]
    html, response = down_load.down_load(url)
    data = {'html': html,
     'response': response}
    if len(sys.argv) >= 3:
        data['title'] = sys.argv[2]
        print 'title', data['title']
    if len(sys.argv) >= 4:
        data['summary'] = sys.argv[3]
        print 'summary', data['summary']
    start = time.time()
    title.get_title_tag(data)
    get_content(data)
    end = time.time()
    print '=====TITLE========='
    print data.get('title', '')
    print '=====CONTENT======='
    print data['content']
    print '=====USED TIME====='
    print end - start