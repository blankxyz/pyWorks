#!/usr/bin/python
# coding=utf-8

import re
import os
import datetime
import urlparse


class Util(object):
    def __init__(self):
        pass

    def convert_path_to_rule(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        # print path
        pos = path.rfind('.')
        if pos > 0:
            suffix = path[pos:]
            path = path[:pos]
        else:
            suffix = ''
        # print suffix,path
        split_path = path.split('/')
        # print split_path
        new_path_list = []
        for p in split_path:
            # regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
            regex = re.sub(r'\d', '\d', p)
            new_path_list.append(self.convert_regex_format(regex))
        # print new_path
        new_path = '/'.join(new_path_list) + suffix
        return urlparse.urlunparse(('', '', new_path, '', '', ''))

    def convert_regex_format(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6,6}/[a-zA-Z]\d{8,8}_\d{6,6}.htm
        '''
        ret = ''
        digit = '\d'
        word = '[a-zA-Z]'
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
                temp = '%s{%d,%d}' % (digit, cnt, cnt)
                pos = pos + len(digit)
            elif rule[pos:pos + len(word)] == word:
                if temp.find(word) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d,%d}' % (word, cnt, cnt)
                pos = pos + len(word)
            elif pos == len(rule):
                ret = ret + temp
                break
            else:
                ret = ret + temp + rule[pos]
                temp = ''
                cnt = 0
                pos = pos + 1
        return ret

    def marge_digit(self, rules):
        print '[INFO]marge_digit() start.', len(rules), rules
        # rules.sort()
        for i in range(len(rules)):
            for j in range(i + 1, len(rules), 1):
                if self.is_same_rule(rules[i], rules[j]):
                    rule_new = self.merge_digit_scope(rules[i], rules[j])
                    # 原有全部替换为新规则
                    for k in range(len(rules)):
                        if rules[k] == rules[i]:
                            rules[k] = rule_new

                    for k in range(len(rules)):
                        if rules[k] == rules[j]:
                            rules[k] = rule_new

        rules = list(set(rules))
        rules.sort()
        print '[INFO]marge_digit() end.', len(rules), rules
        return rules

    def is_same_rule(self, rule1, rule2):
        ret = False
        if len(rule1) == len(rule2):
            for i in range(len(rule1)):
                if rule1[i] != rule2[i]:
                    if rule1[i].isdigit() and rule2[i].isdigit():
                        ret = True
                    else:
                        return False
        return ret

    def merge_digit_scope(self, rule1, rule2):
        ''' {1,2} + {2,3} -> {1,3}'''
        rule_new = ''
        for i in range(len(rule1)):
            if cmp(rule1[i], rule2[i]) < 0:
                if rule1[i - 1] == '{':
                    new = rule1[i]
                else:
                    new = rule2[i]
            elif cmp(rule1[i], rule2[i]) > 0:
                if rule1[i - 1] == '{':  # {M,N}
                    new = rule2[i]
                else:
                    new = rule1[i]
            else:
                new = rule1[i]

            rule_new += new

        return rule_new

    def without_digit_regex(self, regex):
        # '/post-culture-\\d{6,6}-\\d{1,1}.shtml' -> '/post-culture--.shtml'
        return re.sub(r'\\d\{\d\,\d\}', "", regex)

    def get_words(self, regex):
        # '/post-culture--.shtml' -> ['post','culture','shtml']
        words = []
        word = ''
        for i in range(len(regex)):
            if regex[i].isalpha():
                word += regex[i]
            else:
                if word != '':
                    words.append(word)
                word = ''

        return words

    def get_regexs_words(self, regexs):
        ''' regexs:
            ['/post-\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{4,4}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{5,5}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{7,7}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{4,4}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{5,5}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-no\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-no\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
             '/list-\\d{1,1}d-\\d{1,1}.shtml',
             '/list-\\d{2,4}-\\d{1,1}.shtml',
             '/list-apply-\\d{1,1}.shtml']
        '''
        all_words = []
        for regex in regexs:
            without_digit = self.without_digit_regex(regex)
            words = self.get_words(without_digit)
            all_words.extend(words)

        all_words = list(set(all_words))
        # all_words.sort()
        # print all_words

        all_words_dic = {}
        for w in all_words:
            w_cnt = 0
            for r in regexs:
                without_digit = self.without_digit_regex(r)
                words = self.get_words(without_digit)
                if w in words:
                    w_cnt += 1  # 匹配次数

            all_words_dic[w] = w_cnt

        # return  {'apply': 1, 'post': 11, 'list': 3, 'd': 1, 'no': 2}
        return all_words_dic


########################################################################################
if __name__ == '__main__':
    util = Util()
    test_list = ['/post-\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
                 '/post-\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
                 '/post-\\d{3,3}-\\d{4,4}-\\d{1,1}.shtml',
                 '/post-\\d{3,3}-\\d{5,5}-\\d{1,1}.shtml',
                 '/post-\\d{3,3}-\\d{6,6}-\\d{1,1}.shtml',
                 '/post-\\d{3,3}-\\d{7,7}-\\d{1,1}.shtml',
                 '/post-\\d{4,4}-\\d{4,4}-\\d{1,1}.shtml',
                 '/post-\\d{4,4}-\\d{5,5}-\\d{1,1}.shtml',
                 '/post-\\d{4,4}-\\d{6,6}-\\d{1,1}.shtml',
                 '/post-no\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
                 '/post-no\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
                 '/list-\\d{1,1}d-\\d{1,1}.shtml',
                 '/list-\\d{2,4}-\\d{1,1}.shtml',
                 '/list-apply-\\d{1,1}.shtml']
    # util.marge_digit(test_list)

    # regex = '/post-no\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml'
    # print regex
    # regex_new = util.without_digit_regex(regex)
    # print regex_new
    # print util.get_words(regex_new)

    print util.get_regexs_words(test_list)
