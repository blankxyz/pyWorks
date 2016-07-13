def get_keywords_match():
    keywords = "'" + ",'".join(['list', 'index', 'detail', 'post', 'content']) + "'"

    matched_cnt = ','.join(['34', '21', '20', '20', '1'])
    return keywords, matched_cnt


print get_keywords_match()