#!/usr/bin/python
# coding=utf-8

import re
import os
import datetime
import urlparse


class Util(object):
    def __init__(self):
        pass

    def merge_word(self, advice_regex_dic, ignore_words):
        print '[INFO]merge_word() start.', advice_regex_dic, ignore_words
        ret_merge_word = {}
        for k, v in advice_regex_dic.items():
            matched = False
            #和所有的忽略词匹配
            for word in ignore_words:
                if k.find(word) >= 0:
                    matched = True
                    replace = '[a-zA-Z]{%d,%d}' % (len(word), len(word))
                    regex = re.sub(word, replace, k)
                    ret_merge_word.update({regex: v})

            # 没有忽略词匹配
            if matched is False:
                ret_merge_word.update({k: v})

        l = [k for k,v in ret_merge_word.items()]
        print self.merge_digit(l)

        print '[INFO]merge_word() end.', ret_merge_word
        return ret_merge_word

    def merge_digit(self, rules):
        print '[INFO]merge_digit() start.', len(rules), rules
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
        print '[INFO]merge_digit() end.', len(rules), rules
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


########################################################################################
if __name__ == '__main__':
    util = Util()
    advice_regex_dic = {
        "/post-\\d{2,4}-\\d{4,7}-\\d{1,1}.shtml": 83,
        "/list-\\d{2,4}-\\d{1,1}.shtml": 251,
        "/post-no\\d{2,2}-\\d{6,7}-\\d{1,1}.shtml": 24,
        "/post-funinfo-\\d{7,7}-\\d{1,1}.shtml": 42,
        "/post-stocks-\\d{6,7}-\\d{1,1}.shtml": 16,
        "/post-free-\\d{7,7}-\\d{1,1}.shtml": 21,
        "/post-worldlook-\\d{7,7}-\\d{1,1}.shtml": 13
    }
    ignore_words = ['funinfo','free','stocks','worldlook','no']

    print util.merge_word(advice_regex_dic,ignore_words)
