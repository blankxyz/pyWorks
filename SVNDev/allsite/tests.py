from django.test import TestCase

from .dbDriver import MongoDriver
from .setting import UNKOWN

MDB = MongoDriver()


def _setDetailAccuracy(day):
    '''
    info ={
        "date" : "20170309",
        "all_cnt" : 300221,
        "accuracy" : {
            "all" : "0.6",
            "title" : "0.7",
            "content" : "0.8",
            "source" : "0.9",
            "ctime" : "0.8"
        }
    }
    '''
    all_cnt = MDB.get_detail_search_cnt('', '', '', day)
    for part in ['all', 'title', 'content', 'source', 'ctime']:
        selected_cond = '_' + part + 'OK'
        part_ok_cnt = MDB.get_detail_part_ok_cnt('', '', selected_cond, all_cnt, part, day)
        part_accuracy_rate = float(part_ok_cnt) / all_cnt if all_cnt else UNKOWN

        info = dict()
        info['date'] = day
        info['all_cnt'] = all_cnt
        info['accuracy'][part] = part_accuracy_rate

        MDB.set_detail_accuracy(info)


if __name__ == '__main__':
    _setDetailAccuracy('20170307')
