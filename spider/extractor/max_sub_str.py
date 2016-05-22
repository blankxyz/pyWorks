# Embedded file name: /work/build/source/athena/utils/extractor/max_sub_str.py
import time
import max_pub_sub
stop_words = u' ,.'
max_pub_sub.set_stop_word(stop_words)

def max_sub(s1, s2, stop_words):
    s1_index = 0
    s2_index = 0
    str_len = 0
    line = [0] * len(s2)
    for i in range(len(s1)):
        for j in range(len(s2) - 1, -1, -1):
            if s1[i] == s2[j]:
                if j == 0:
                    line[j] = 1
                else:
                    line[j] = line[j - 1] + 1
                if line[j] > str_len:
                    str_len = line[j]
                    s1_index = i
                    s2_index = j
            else:
                line[j] = 0

    return (s1_index, s2_index, str_len)


def get_like(s1, s2):
    correlation = 0.0
    while 1:
        i, j, l = max_pub_sub.py_max_sub(s1, s2)
        public_str = s1[i - l + 1:i + 1]
        if len(public_str) < 2:
            break
        s1_count = s1.count(public_str)
        s2_count = s2.count(public_str)
        correlation += float(len(public_str)) * s1_count + float(len(public_str)) * s2_count
        s1 = s1.replace(public_str, '')
        s2 = s2.replace(public_str, '')

    return correlation


def get_all_pub(s1, s2):
    result = []
    while 1:
        i, j, l = max_pub_sub.py_max_sub(s1, s2)
        public_str = s1[i - l + 1:i + 1]
        if len(public_str) < 2:
            break
        result.append(public_str)
        s1 = s1.replace(public_str, '')
        s2 = s2.replace(public_str, '')

    return result


def test(s1, s2):
    correlation = 0.0
    while 1:
        i, j, l = max_pub_sub.py_max_sub(s1, s2)
        public_str = s1[i - l + 1:i + 1]
        if len(public_str) < 2:
            break
        s1_count = s1.count(public_str)
        s2_count = s2.count(public_str)
        print public_str, s1_count
        print public_str, s2_count
        correlation += float(len(public_str)) * s1_count + float(len(public_str)) * s2_count
        s1 = s1.replace(public_str, '')
        s2 = s2.replace(public_str, '')

    print 'correlation', correlation


if __name__ == '__main__':
    s1 = u'\uff0c \u4e2a,\u6e21\u90e8\u6052\u96c4\u53ca\u65e5'
    s2 = u', ,\u6e21\u90e8\u6052\u96c4\u5206\u6790'
    test(s1, s2)